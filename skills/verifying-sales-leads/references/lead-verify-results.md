# Reading a verify_lead result

## Verdict

| `verdict` | Meaning | What to tell the user |
|---|---|---|
| `real_active` | The register knows the company and shows it as active. | Real and active; go on to the flags. |
| `real_inactive` | The register knows the company but it is no longer active. | Do not treat it as a trading company. |
| `not_found` | No company matched the number or name. | Check the number or name with the lead. |
| `ambiguous` | A Dutch name matched more than one company. | Ask for the KVK number and check again. |
| `unverifiable` | The register could not be asked. With `reason: be_requires_number`, a Belgian lead was sent without its KBO number. | Ask for the missing number. |
| `sanctioned` | The sanctions screen matched. `lead_score` is 0. | Stop and review the match; a name match is not a legal determination. |

`lead_score` runs from 0 to 100, higher is better. Inputs that were not sent are not scored against the lead.

## Flags

Each flag comes with a finding in `findings[]` that carries `action`, `why` and `expected_result`. Pass those on as they are.

| Flag | What it says |
|---|---|
| `name_mismatch` | The name the lead gave differs from the registered name. |
| `address_mismatch` | The address the lead gave differs from the registered address. |
| `iban_invalid` | The IBAN does not pass validation. |
| `iban_foreign` | The IBAN is valid but issued in another country than the company's register. |
| `vat_invalid` | VIES does not know the VAT number as valid. |
| `vat_owner_mismatch` | The VAT number is valid but VIES registers it under another name. |
| `no_mail_server` | The email domain has no mail server, so mail cannot arrive. |
| `disposable_email` | The email domain is a disposable-mail service. |
| `recently_registered` | The company was registered less than 12 months ago. |
| `inactive` | The register shows the company as no longer active. |
| `business_stopped` | KVK records that the business has stopped. |
| `dormant_shell_signals` | Several signals point to a dormant or shell company. |

## Other blocks

`company`, `vat`, `iban`, `sanctions` and `email` hold the per-source answers. The IBAN block returns only the country, bank, BIC and last 4 characters, never the full IBAN.
