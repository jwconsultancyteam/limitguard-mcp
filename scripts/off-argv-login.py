#!/usr/bin/env python3
"""Run `mcp-publisher login http` with the domain key kept out of /proc.

Why this exists
---------------
`mcp-publisher login http` only accepts the Ed25519 key as a command-line
flag (`--private-key <hex>`); as of 1.8.1 (the newest release) there is no
key-file, stdin, or environment-variable option, and the in-process signer is
the only signer that works with a locally held key (the Azure Key Vault and
Google KMS signers are for cloud-held keys). A flag value is visible to any
process on the shared self-hosted runner via /proc/<pid>/cmdline for the whole
login call, so passing the key directly is a MEDIUM-severity leak.

What this does instead
----------------------
The key travels only through environment and heap memory -- never through any
process's argv, and never through this script's own argv or /proc-visible
environment:

1. Read the key from $MCP_OFF_ARGV_KEY, then remove it from the environment
   and scrub its copy from this process's original stack-top strings (the
   region /proc/<pid>/environ is built from).
2. fork(); the child marks itself PTRACE_TRACEME and execs the CLI with the
   key in argv (the CLI parses flags only from argv, so it has to be there).
   The child's environment no longer carries the key.
3. The parent follows the child with PTRACE_SYSCALL. The moment any thread
   is about to make the child's *first* connect(2) -- which in the 1.8.1
   login flow happens strictly after the flags are parsed and the token is
   signed (the signature is computed when the exchange request is built,
   before any byte leaves the machine) -- the parent overwrites every copy
   of the key in the child's stack-top argv/environment region (the region
   /proc/<pid>/cmdline and /proc/<pid>/environ are built from) with 'x'.
4. Tracing then continues until the process exits (detaching mid-run wedged
   Go's netpoller in testing: connection established, handshake never
   continued), and the parent reaps it and propagates its exit status.

After step 3 the running login process no longer exposes the key through
/proc at all. The residual window is exec-to-first-connect (process startup,
typically well under a second, during which nothing has reached the network);
that window cannot be closed further without patching the CLI.

Detection detail: aarch64 has no syscall-entry register marker, so entry
stops are recognised by strict alternation per thread (the first syscall stop
of a thread is always an entry). The syscall number register is only read at
entry stops, and no thread can hold connect's syscall number (203) at an
entry stop before the net stack runs -- which only happens after parsing and
signing.

Deliberately fail-open: any error in the tracing/scrub machinery produces a
::warning:: and the login proceeds exactly as it did before this script
existed. A release must never fail because of its key-hiding wrapper; the
worst case is the old exposure level, which is also what an unexpected kernel
or CLI behaviour would produce.

Usage:
    MCP_OFF_ARGV_KEY=<64 hex chars> python3 scripts/off-argv-login.py \
        --binary /path/to/mcp-publisher --domain api.limitguard.ai \
        --registry https://registry.modelcontextprotocol.io

The key is read exclusively from $MCP_OFF_ARGV_KEY; it must not appear in
this script's argv.
"""

import argparse
import ctypes
import os
import platform
import re
import signal
import struct
import sys

PTRACE_TRACEME = 0
PTRACE_DETACH = 17
PTRACE_SYSCALL = 24
PTRACE_SETOPTIONS = 0x4200
PTRACE_GETEVENTMSG = 0x4201
PTRACE_GETREGSET = 0x4204

PTRACE_O_TRACESYSGOOD = 0x00000001
# Without TRACECLONE the kernel does not auto-attach CLONE_THREAD children at
# all (unlike fork children): the Go runtime spawns its netpoller/M threads
# that way, and the login's connect(2) can run on any of them.
PTRACE_O_TRACECLONE = 0x00000008
PTRACE_EVENT_CLONE = 3

NT_PRSTATUS = 1

# ptrace request numbers are architecture-independent; syscall numbers are
# not. Only aarch64 is implemented: the workflow pins the ARM64 runner and
# downloads the linux_arm64 CLI, and other architectures fall back to the
# unhidden exec below rather than guessing register layouts.
ARCH = platform.machine()
CONNECT_NR = {"aarch64": 203}

# aarch64 user_pt_regs: 31 general registers + sp + pc + pstate; the syscall
# number is x8. Unlike x86-64, aarch64 has no -ENOSYS entry marker (x0 keeps
# its argument at entry), so entry/exit is tracked by stop alternation.
PT_REGS_SIZE = 34 * 8
REG_SYSCALL_NR = 8

__WALL = 0x40000000
PAGE = 4096

# Signals that must never be injected back into the tracee: ptrace-internal
# stops (SIGTRAP family), group/auto-attach stops (SIGSTOP), and the noise
# signals a short-lived CLI child has no handler for. Everything else --
# SIGSEGV, SIGABRT, SIGPIPE, ... -- is delivered so a fault cannot livelock
# the tracer by re-faulting at the same instruction.
SWALLOWED_SIGNALS = {
    0,
    signal.SIGSTOP,
    signal.SIGTRAP,
    signal.SIGCHLD,
    signal.SIGWINCH,
    signal.SIGURG,
    signal.SIGCONT,
}

_libc = ctypes.CDLL(None, use_errno=True)
# Pointer-sized arguments; without this ctypes converts bare Python ints to
# 32-bit c_int and high heap addresses reach the kernel truncated (EFAULT).
_libc.ptrace.restype = ctypes.c_long
_libc.ptrace.argtypes = [ctypes.c_ulong] * 4


def ptrace(request, pid, addr=0, data=0):
    if _libc.ptrace(request, pid, addr, data) == -1:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))


class IOVec(ctypes.Structure):
    _fields_ = [("iov_base", ctypes.c_void_p), ("iov_len", ctypes.c_size_t)]


def getregs(tid):
    buf = ctypes.create_string_buffer(PT_REGS_SIZE)
    iov = IOVec(ctypes.addressof(buf), PT_REGS_SIZE)
    ptrace(PTRACE_GETREGSET, tid, NT_PRSTATUS, ctypes.addressof(iov))
    return struct.unpack("<34q", buf.raw)


def stack_ranges(pid):
    """The main-thread [stack] mapping: the kernel builds argv and the
    environment (arg_start..env_end) at its top, and that is what
    /proc/<pid>/cmdline and /proc/<pid>/environ are read from."""
    ranges = []
    with open(f"/proc/{pid}/maps") as fh:
        for line in fh:
            if line.rstrip().endswith("[stack]"):
                start, end = (int(part, 16) for part in line.split()[0].split("-"))
                ranges.append((start, end))
    return ranges


def scrub_stack(mem, ranges, needle):
    """Overwrite every occurrence of needle in the mapped stack pages with
    'x', page by page so guard-page holes short-read instead of aborting."""
    patches = 0
    tail = b""
    for start, end in ranges:
        addr = start
        while addr < end:
            want = min(PAGE, end - addr)
            try:
                mem.seek(addr)
                page = mem.read(want)
            except OSError:
                page = b""
            haystack = tail + page
            base = addr - len(tail)
            pos = 0
            while True:
                hit = haystack.find(needle, pos)
                if hit < 0:
                    break
                mem.seek(base + hit)
                mem.write(b"x" * len(needle))
                patches += 1
                pos = hit + len(needle)
            tail = haystack[-(len(needle) - 1) :] if len(needle) > 1 else b""
            addr += want
    return patches


def detach_all(pid):
    """Detach from every thread of pid, best effort."""
    try:
        tids = [int(t) for t in os.listdir(f"/proc/{pid}/task")]
    except OSError:
        tids = [pid]
    for tid in tids:
        try:
            ptrace(PTRACE_DETACH, tid, 0, 0)
        except OSError:
            pass


def reap(pid):
    while True:
        try:
            done, status = os.waitpid(pid, 0)
        except InterruptedError:
            continue
        if done == pid:
            break
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return 1


def login_off_argv(binary, domain, registry, key):
    """Run `binary login http` with key only in the child's argv, scrubbing
    the child's /proc-visible copies at its first connect(2)."""
    argv = [
        binary,
        "login",
        "http",
        "--domain",
        domain,
        "--private-key",
        key,
        "--registry",
        registry,
    ]
    needle = key.encode()
    connect_nr = CONNECT_NR[ARCH]

    pid = os.fork()
    if pid == 0:
        try:
            # The kernel reports the exec to the parent as a SIGTRAP stop.
            ptrace(PTRACE_TRACEME, 0, 0, 0)
            os.execve(binary, argv, os.environ)
        except OSError as exc:
            print(f"::error::failed to exec {binary}: {exc}", file=sys.stderr)
            os._exit(127)

    try:
        # Exec stop: the child is now the CLI, one SIGTRAP away from running.
        _, status = os.waitpid(pid, 0)
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)  # exec itself failed (message printed)
        if os.WIFSIGNALED(status):
            return 128 + os.WTERMSIG(status)
        # TRACESYSGOOD makes syscall stops arrive as SIGTRAP|0x80, distinct
        # from signal-delivery stops. Options are inherited by every thread
        # the CLI later clones.
        ptrace(
            PTRACE_SETOPTIONS, pid, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_TRACECLONE
        )
        ptrace(PTRACE_SYSCALL, pid, 0, 0)

        # aarch64 has no register marker for syscall-entry stops (x0 keeps
        # its argument), so entry/exit is tracked by strict alternation: the
        # first syscall stop of a thread -- the CLI's right after exec, a new
        # thread's right after its attach stop -- is always an entry.
        parity = {}
        scrubbed = 0
        stops = 0
        while True:
            done, status = os.waitpid(-1, __WALL)
            if os.WIFEXITED(status):
                if done == pid:
                    return os.WEXITSTATUS(status)  # exited without ever connecting
                continue
            if os.WIFSIGNALED(status):
                if done == pid:
                    return 128 + os.WTERMSIG(status)
                continue
            event = status >> 16
            if event == PTRACE_EVENT_CLONE:
                # A new thread: the kernel created it stopped. Name the same
                # options (they are inherited, but set them anyway) and start
                # it; it cannot reach connect(2) before its first restart.
                new_tid = ctypes.c_ulong(0)
                ptrace(PTRACE_GETEVENTMSG, done, 0, ctypes.addressof(new_tid))
                try:
                    ptrace(
                        PTRACE_SETOPTIONS,
                        new_tid.value,
                        0,
                        PTRACE_O_TRACESYSGOOD | PTRACE_O_TRACECLONE,
                    )
                    ptrace(PTRACE_SYSCALL, new_tid.value, 0, 0)
                except OSError:
                    pass  # the thread died as fast as Go threads can
                ptrace(PTRACE_SYSCALL, done, 0, 0)
                continue
            stopsig = os.WSTOPSIG(status)
            if stopsig == (signal.SIGTRAP | 0x80):
                entry = parity.get(done, True)
                parity[done] = not entry
                inject = 0
                if entry and not scrubbed:
                    try:
                        regs = getregs(done)
                    except OSError:
                        regs = None  # a task we cannot read registers at (exiting)
                    if regs and regs[REG_SYSCALL_NR] == connect_nr:
                        # First connect's syscall-entry stop: parsing and
                        # signing are done (see module docstring) and no key
                        # material has left the machine, so from here the
                        # /proc-visible copies can go.
                        with open(f"/proc/{pid}/mem", "r+b", buffering=0) as mem:
                            scrubbed = scrub_stack(
                                mem, stack_ranges(pid), needle
                            )
                        print(
                            f"key hidden: scrubbed {scrubbed} /proc-visible "
                            "cop(y|ies).",
                            file=sys.stderr,
                        )
                        # No detach here: detaching mid-run left Go's
                        # netpoller wedged in testing (connection
                        # established, handshake never continued). Tracing
                        # continues -- the login's remaining life is a few
                        # hundred syscalls -- until the process exits and is
                        # reaped from the waitpid loop above.
            else:
                inject = 0 if stopsig in SWALLOWED_SIGNALS else stopsig
            try:
                ptrace(PTRACE_SYSCALL, done, 0, inject)
            except OSError:
                pass  # the thread raced us into exit_group; its exit reports via waitpid
            stops += 1
            if stops > 5_000_000:
                raise RuntimeError("no child exit seen after 5M stops")
    except (OSError, RuntimeError) as exc:
        # Fail open: the release flow must not break because of the wrapper.
        print(
            f"::warning::key-hiding scrub failed ({exc}); login continues with "
            "the key on the child's command line, the pre-existing exposure.",
            file=sys.stderr,
        )
    detach_all(pid)
    return reap(pid)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--binary", required=True, help="path to the mcp-publisher binary")
    parser.add_argument("--domain", required=True, help="domain for login http")
    parser.add_argument("--registry", required=True, help="registry URL")
    args = parser.parse_args()

    key = os.environ.get("MCP_OFF_ARGV_KEY", "")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", key):
        print(
            "::error::MCP_REGISTRY_PRIVATE_KEY_HEX is not a 64-character hex "
            "Ed25519 private key.",
            file=sys.stderr,
        )
        return 1

    if ARCH not in CONNECT_NR:
        print(
            f"::warning::key-hiding scrub not implemented for {ARCH}; login "
            "continues with the key on the child's command line.",
            file=sys.stderr,
        )
        os.environ.pop("MCP_OFF_ARGV_KEY", None)
        os.execve(
            args.binary,
            [
                args.binary,
                "login",
                "http",
                "--domain",
                args.domain,
                "--private-key",
                key,
                "--registry",
                args.registry,
            ],
            os.environ,
        )

    # The key leaves the /proc-visible environment before any child exists.
    os.environ.pop("MCP_OFF_ARGV_KEY", None)
    try:
        with open("/proc/self/mem", "r+b", buffering=0) as mem:
            scrub_stack(mem, stack_ranges(os.getpid()), key.encode())
    except OSError as exc:
        print(f"::warning::could not scrub own environ copy: {exc}", file=sys.stderr)

    return login_off_argv(args.binary, args.domain, args.registry, key)


if __name__ == "__main__":
    sys.exit(main())
