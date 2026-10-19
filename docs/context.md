# Context, scope and requirements

**Scenario:** DemoMart is an invented online retailer. All numbers below are design assumptions for a practice case study, not measured customer outcomes.

## Stakeholders

| Role | Desired outcome | Key measure |
| --- | --- | --- |
| Customer | Find and buy goods quickly | Successful checkout rate |
| Operations | Know order and fulfilment state | Reconciliation exceptions |
| Product owner | Release safely without downtime | Deployment frequency and rollback success |
| Security lead | Minimise exposure of personal/payment data | No card data stored; access reviews |
| Finance | Predict cloud spending | Cost per completed order |

## Scope

**In:** web entry point, catalogue reads, checkout workflow, order persistence, tokenised payment integration, shipping events, alerts and audit trails.

**Out:** warehouse robotics, physical point-of-sale terminals, card processing, CRM replacement, predictive recommendations.

## Requirements and design mapping

| ID | Requirement | Candidate solution | Validation |
| --- | --- | --- | --- |
| FR-01 | Customer can search catalogue | CDN-cached read endpoint | Contract + search scenario tests |
| FR-02 | Customer can place an order | Order API, idempotency key, DB transaction | Duplicate-request integration test |
| FR-03 | Shipping status updates eventually appear | Durable events + fulfilment adapter | Replay/duplicate/failure tests |
| NFR-01 | Monthly checkout availability target ≥ 99.9% | Multi-AZ managed services + rollback | Synthetic checks and recovery drill |
| NFR-02 | Catalogue p95 service time < 300 ms | Caching, index tuning | Load test at assumed demand |
| NFR-03 | No card primary account numbers stored | Hosted payment/tokenisation | Data-flow and logs review |
| NFR-04 | Recover service within 2 h, data loss ≤ 15 min | Encrypted backups, tested restore | Quarterly restore test |

## Assumptions needing discovery

- 2,000 concurrent users at peak is an illustrative initial load assumption.
- Payment provider supports idempotent intent creation and webhook verification.
- Shipping service can accept a stable fulfilment reference; duplicate callbacks are possible.
- Addresses and order data are personal information and need limited retention.

## Open questions

- Which markets and tax rules apply?
- Which order states require strong consistency?
- Who owns reconciliation between payment and fulfilment?
- What consent, residency and deletion obligations apply?

These items must be resolved before production deployment.
