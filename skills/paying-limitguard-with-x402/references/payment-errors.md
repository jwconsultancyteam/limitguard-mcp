# x402 payment errors

A refused payment answers `402` with an `errorCode`. Full reference: https://docs.limitguard.ai/guides/errors?utm_source=agent_skill&utm_medium=agent&utm_campaign=docs&utm_content=skill_errors

| `errorCode` | What happened | What to do |
|---|---|---|
| `payment_required` | No key and no payment header. The body is the quote. | Pay one `accepts` entry within the user's ceiling, or stop. |
| `insufficient_funds` | The amount is below the price for this endpoint and quality tier. | Use the quote's `amount` exactly; quote again after changing `X-Response-Quality`. |
| `invalid_signature` | The signature does not verify against the sender, or a transaction hash failed on chain. | Check that the signer is the paying wallet; let the x402 library sign. |
| `unsupported_network` | The payload's network is not one the quote listed. | Pick a network from `accepts`. |
| `duplicate_settlement` | The nonce or transaction was already used. | Sign a fresh authorization. A payment pays exactly once. |
| `expired_payment` | The authorization's ten minutes have passed. | Sign a fresh one; never reuse a payload. |
| `invalid_payment` | The payment header could not be parsed, or its timing is invalid. | Rebuild the payload from the quote with the x402 library. |
| `server_error` | Payment verification was unavailable. Nothing was charged. | Retry later with backoff. |
| `insufficient_balance` | An API key's prepaid balance is below the price. | Tell the user to top up, or pay this call by x402 within the ceiling. |
| `settlement_challenge_required` | A settled transfer was presented without the quote's `X-Payment-Challenge`. | Send the challenge from that quote, or use the `exact` path. |
| `settlement_not_yet_visible` | The transfer is not visible on chain yet. Nothing is wrong. | Wait `Retry-After` seconds and send the same request again. |
| `settlement_claim_stuck` | A temporary internal error held the claim. Not a double charge. | Retry later with the same proof. |
| `settlement_signature_invalid` | The challenge signature does not match the sending wallet. The proof is not consumed. | Sign with the wallet that sent the USDC, or leave the optional header out. |

A `404` with `errorCode: not_cached` on `X-Response-Quality: cached` is not charged; its `retry` block names the fresh tier and price.
