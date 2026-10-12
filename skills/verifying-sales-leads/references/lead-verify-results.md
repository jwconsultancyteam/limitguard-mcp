# Reading a verify_lead result

## Verdict

| `verdict` | Meaning | What to tell the user |
|---|---|---|
| `real_active` | The register knows the company and shows it as active. | Real and active; go on to the findings. |
| `real_inactive` | The register knows the company but it is no longer active. | Do not treat it as a trading company. |
| `not_found` | No company matched the number or name. | Check the number or name with the lead. |
| `ambiguous` | A Dutch name matched more than one company. | Ask for the KVK number and check again. |
| `unverifiable` | A Belgian lead was sent without its KBO number (`reason: be_requires_number`). | Ask for the 10-digit KBO number and check again. |
| `sanctioned` | The registered name is a possible match on the OFAC, EU or UN list; `lead_score` is 0. The result shows no entry. | Say it is a possible match to review, not a finding that the company is sanctioned. To see the entries, offer `sanctions_screen` on the registered name (paid). |

A register that cannot be reached is not a verdict: the call returns an error that says nothing was charged.

## Lead score

`lead_score` runs from 0 to 100, higher is better. Each check adds its points only when its input was sent and passed, so an input left out raises no flag but adds no points. Compare scores only between leads checked with the same inputs.

## Flags

Each flag has a finding in `findings[]` with `action`, `why` and `expected_result`; pass those on as they are. `findings[]` can also hold cross-check results that have no flag.

| Flag | What it says |
|---|---|
| `name_mismatch` | The name the lead gave differs from the registered name. |
| `address_mismatch` | The address the lead gave differs from the registered address. |
| `iban_invalid` | The IBAN fails the checksum or the bank check. |
| `vat_invalid` | VIES does not know the VAT number as valid. |
| `vat_owner_mismatch` | The VAT number is valid but VIES registers it under another name. |
| `no_mail_server` | The email domain has no mail server, so mail cannot arrive. |
| `disposable_email` | The email domain is a disposable-mail service. |
| `recently_registered` | The company was registered less than 12 months ago. |
| `inactive` | The register shows the company as no longer active. |
| `business_stopped` | KVK records that the business has stopped. |
| `dormant_shell_signals` | Several signals point to a dormant or shell company. |

## Sanctions block

- `screened: false` means no screen ran; `reason` says why (for example a sole trader or partnership, whose name is a person's name). Never report that as "no sanctions match".
- With any sanctions result, give `lists_as_of` (the date of each list) and `list_note`.

## Other blocks

`company`, `vat`, `iban` and `email` hold the per-source answers. The IBAN block returns only the country, bank, BIC and last 4 characters, never the full IBAN.
