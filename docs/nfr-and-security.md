# Non-functional requirements, security and assurance

Targets below are *proposed* and have not been verified by testing.

| Characteristic | Target | Assurance method |
| --- | --- | --- |
| Checkout availability | 99.9% monthly | External synthetic probes |
| Catalogue p95 response | < 300 ms at defined load | Load test + tracing |
| Recovery time objective (RTO) | 2 hours | Recovery exercise |
| Recovery point objective (RPO) | 15 minutes | Restore validation |
| Event processing | 99% < 60 seconds in healthy state | Queue age SLI |
| Credentials | No long-lived credentials in code | CI secret scan and workload identity |
| Data handling | No raw payment card details in app | Architecture review and log scan |

## Lightweight threat model (STRIDE)

| Risk | Example | Control |
| --- | --- | --- |
| Spoofing | Forged shipping callback | Signed webhook + nonce/timestamp validation |
| Tampering | Customer changes another user's order | Server-side authorisation and audit trail |
| Repudiation | Untraceable refund | Immutable audit events with restricted access |
| Disclosure | Customer address in traces | PII redaction and access controls |
| Denial of service | Catalogue burst overload | WAF, quotas, caching, backpressure |
| Privilege elevation | Broad service role | Least privilege, reviews and separation of duties |

## Data handling

Personal data (contact details and shipping addresses) requires purpose limitation, retention periods, deletion strategy and encryption in transit/at rest. Secrets live in a dedicated vault. Production access is time-bound, logged and regularly reviewed.

## Operational readiness

Before launch: complete threat modelling, penetration test planning, privacy review, restore test, failover exercise, third-party risk review, on-call runbooks and a cost forecast. Publish operational SLOs only after baseline measurements.
