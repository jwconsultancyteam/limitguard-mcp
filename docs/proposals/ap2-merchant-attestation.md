# Proposal: verified merchant identity for AP2

Status: proposal, 13 October 2026. Audience: the AP2 maintainers and the FIDO Alliance working groups.
Discussion: an issue in [google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2) links here.

### Problem

AP2 lets a user limit who an agent may pay: `payment.allowed_payees` in a Payment Mandate, and the Merchant object with id, name and website. The spec does not say how the shopping agent or the trusted surface knows that a merchant is real. Real means registered, active and the business the user means. Issue #315 shows the effect: payee matching falls back to mutable display fields. Issues #163 and #187 ask for a structured Risk Payload, and that work is still open.

Before an agent pays an unknown merchant, it needs a verifiable answer to one question. Is this a real business, and the one the user means?

### Proposal

Add an optional, verifiable **merchant attestation**. A trust provider issues it. The shopping agent or the trusted surface checks it before it puts the merchant in `allowed_payees`.

```json
{
  "merchant": {
    "name": "Example B.V.",
    "website": "https://example.nl",
    "registry_id": {"scheme": "NL-KVK", "value": "12345678"},
    "vat_id": "NL123456789B01"
  },
  "status": "active",
  "checks": ["registry", "vat", "sanctions"],
  "issued_at": "2026-10-13T18:00:00Z",
  "expires_at": "2026-10-14T18:00:00Z",
  "issuer": "https://trust-provider.example",
  "signature": "<JWS or SD-JWT>"
}
```

- **The identity anchor** is a registry identifier with a scheme, so payee matching no longer depends on a display name. Example schemes are NL-KVK, BE-KBO, VAT and LEI.
- **The attestation is short-lived**, so a closed or sanctioned business drops out fast.
- **The signature uses the same SD-JWT tooling** that mandates already use, and the issuer publishes its key.
- **Several providers can issue attestations,** so no single provider owns the field. The user's credential provider or trusted surface decides which issuers it trusts.

### Where it plugs in

1. The trusted surface shows the attestation next to the Checkout Mandate. The user then sees that a trust provider verified the merchant.
2. The shopping agent only adds a merchant to `allowed_payees` in an Open Payment Mandate when it holds a valid attestation.
3. The attestation can travel in the Risk Payload that #163 proposes.

### Reference implementation

We run a register-backed check for Dutch and Belgian businesses: KVK, KBO, VIES VAT and sanctions screening. We can publish a reference issuer and a verifier sample under the repository's license, if the maintainers find the direction useful.

Happy to adjust the shape to the v0.2 schemas and to whatever comes out of the FIDO work.
