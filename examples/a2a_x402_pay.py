#!/usr/bin/env python3
"""
Example: an agent pays a Limitguard skill over A2A with x402 (a2a-x402 v0.2).

No API key. Two A2A ``message/send`` calls to POST /a2a:

1. Call a priced skill with the header ``X-A2A-Extensions: <a2a-x402 v0.2 URI>``.
   Limitguard answers with a Task in state ``input-required`` whose status message
   carries ``x402.payment.required`` (the price, the USDC asset and the recipient).
2. Sign one of those requirements (an EIP-3009 USDC authorization on Base) and send
   it back with the task id as ``x402.payment.payload``. Limitguard verifies it, runs
   the check, settles only if the check succeeded, and answers a completed Task with
   the result and ``x402.payment.receipts``.

Safety built in: the quote is printed and nothing is signed until you type "yes"
(or pass --yes), and a quote above --max-usd (default $0.20) is refused. The key is
read from EVM_PRIVATE_KEY or asked for without echo; it is never printed.

Prerequisites:
    pip install "x402[evm,httpx]"

Environment:
    EVM_PRIVATE_KEY     - optional, 0x-prefixed hex private key of the paying wallet
                          (USDC on Base mainnet, eip155:8453; no ETH needed for gas)
    LIMITGUARD_API_URL  - optional, default https://api.limitguard.ai

Usage:
    python examples/a2a_x402_pay.py
    python examples/a2a_x402_pay.py --skill verify_wallet \\
        --input '{"wallet_address": "0x...", "chain_id": "eip155:8453"}'
"""

import argparse
import asyncio
import getpass
import json
import os
import sys
import uuid

import httpx
from eth_account import Account
from x402 import x402Client
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.schemas.payments import PaymentRequired

DEFAULT_API_URL = "https://api.limitguard.ai"
EXTENSION_URI = "https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2"
BASE_MAINNET = "eip155:8453"
USDC_DECIMALS = 6
DEFAULT_INPUT = {
    "verify_wallet": {"wallet_address": "0x4200000000000000000000000000000000000006", "chain_id": BASE_MAINNET},
    "risk_score": {"entity_name": "Acme Corp BV", "country": "NL"},
}


def _message(parts: list, *, task_id: str | None = None, metadata: dict | None = None) -> dict:
    message = {"role": "user", "kind": "message", "messageId": str(uuid.uuid4()), "parts": parts}
    if task_id:
        message["taskId"] = task_id
    if metadata:
        message["metadata"] = metadata
    return {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send", "params": {"message": message}}


async def _send(http: httpx.AsyncClient, body: dict) -> dict:
    resp = await http.post("/a2a", json=body, headers={"X-A2A-Extensions": EXTENSION_URI})
    resp.raise_for_status()
    answer = resp.json()
    if "error" in answer:
        error = answer["error"]
        raise SystemExit(f"JSON-RPC error {error.get('code')}: {error.get('message')}\n{json.dumps(error.get('data'), indent=2)}")
    return answer["result"]


def _meta(task: dict) -> dict:
    return ((task.get("status") or {}).get("message") or {}).get("metadata") or {}


def _print_result(task: dict) -> None:
    state = (task.get("status") or {}).get("state")
    meta = _meta(task)
    print(f"Task {task.get('id')}: {state} ({meta.get('x402.payment.status', 'no payment')})")
    for receipt in meta.get("x402.payment.receipts") or []:
        print(f"  receipt: success={receipt.get('success')} network={receipt.get('network')} "
              f"payer={receipt.get('payer', '')} transaction={receipt.get('transaction') or '(settled after the response)'}")
        if receipt.get("errorReason"):
            print(f"  reason: {receipt['errorReason']}")
    text = next((p.get("text") for p in ((task.get("status") or {}).get("message") or {}).get("parts") or []
                 if p.get("kind") == "text"), None)
    if text and state != "completed":
        print(f"  {text}")
    for artifact in task.get("artifacts") or []:
        for part in artifact.get("parts") or []:
            if part.get("kind") == "data":
                print(json.dumps(part["data"], indent=2)[:2000])


async def run(
    base_url: str, skill: str, input_data: dict, max_usd: float, assume_yes: bool,
    transport: httpx.AsyncBaseTransport | None = None,
) -> int:
    """The whole flow. ``transport`` is only for tests (httpx.ASGITransport)."""
    async with httpx.AsyncClient(base_url=base_url, timeout=60, transport=transport) as http:
        print(f"1. Calling skill {skill!r} on {base_url}/a2a with the a2a-x402 extension, no key")
        task = await _send(http, _message([{"kind": "data", "data": {"skill": skill, "input": input_data}}]))
        if task.get("kind") == "message":
            raise SystemExit("Got a plain message, not a task: is the skill name right?")
        if _meta(task).get("x402.payment.status") != "payment-required":
            print("No payment was asked (a free skill, or the extension is switched off):")
            _print_result(task)
            return 0

        required = PaymentRequired.model_validate(_meta(task)["x402.payment.required"])
        base = [a for a in required.accepts if a.network == BASE_MAINNET and a.scheme == "exact"]
        if not base:
            raise SystemExit(f"No 'exact' requirement on {BASE_MAINNET}; offered: {[(a.network, a.scheme) for a in required.accepts]}")
        offer = base[0]
        usd = int(offer.amount) / 10**USDC_DECIMALS
        print(f"2. Quote for task {task['id']}: {usd:.2f} USDC on {offer.network} to {offer.pay_to}")
        if usd > max_usd:
            raise SystemExit(f"Refusing: {usd:.2f} USDC is above --max-usd {max_usd:.2f}.")

        private_key = os.environ.get("EVM_PRIVATE_KEY") or getpass.getpass("Paying wallet private key (0x..., not shown): ")
        account = Account.from_key(private_key.strip())
        del private_key
        print(f"   Paying wallet: {account.address}")
        if not assume_yes and input(f"   Sign {usd:.2f} USDC to {offer.pay_to}? Type yes: ").strip().lower() != "yes":
            print("Not signed; sending payment-rejected so the task is closed.")
            await _send(http, _message([{"kind": "text", "text": "rejected"}], task_id=task["id"],
                                       metadata={"x402.payment.status": "payment-rejected"}))
            return 1

        client = x402Client().register(BASE_MAINNET, ExactEvmScheme(account))
        client.set_spend_controls({"max_amount_per_payment": f"${max_usd}"})
        payload = await client.create_payment_payload(
            PaymentRequired(x402_version=required.x402_version, resource=required.resource, accepts=[offer])
        )
        print("3. Submitting the signed payment with the task id")
        done = await _send(http, _message(
            [{"kind": "text", "text": "payment"}],
            task_id=task["id"],
            metadata={
                "x402.payment.status": "payment-submitted",
                "x402.payment.payload": payload.model_dump(mode="json", by_alias=True, exclude_none=True),
            },
        ))
        _print_result(done)
        return 0 if (done.get("status") or {}).get("state") == "completed" else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Pay a Limitguard A2A skill with x402 (a2a-x402 v0.2).")
    parser.add_argument("--skill", default="verify_wallet")
    parser.add_argument("--input", help="skill input as JSON (default: an example for the skill)")
    parser.add_argument("--max-usd", type=float, default=0.20, help="refuse a quote above this (default 0.20)")
    parser.add_argument("--yes", action="store_true", help="sign without asking")
    args = parser.parse_args()
    input_data = json.loads(args.input) if args.input else DEFAULT_INPUT.get(args.skill)
    if input_data is None:
        parser.error(f"--input is required for skill {args.skill!r}")
    base_url = os.environ.get("LIMITGUARD_API_URL", DEFAULT_API_URL).rstrip("/")
    sys.exit(asyncio.run(run(base_url, args.skill, input_data, args.max_usd, args.yes)))


if __name__ == "__main__":
    main()
