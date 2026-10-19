# ADR-0002: Publish order events through transactional outbox

## Status
Accepted for this fictional reference design.

## Context
The checkout process must not lose an order event when database commit succeeds but the event broker is temporarily unavailable.

## Decision
Write an order record and its outbox message in one database transaction. A relay publishes events asynchronously to a durable broker. Consumers process events at least once and maintain an idempotency record.

## Alternatives
1. Publish directly after DB write: vulnerable to a crash gap.
2. Distributed 2-phase commit: costly coupling and limited support.
3. Transactional outbox plus idempotent consumer (**chosen**).

## Consequences
Events are eventually delivered rather than instantly visible. A relay can send duplicates; consumers must tolerate them. Teams need schema-version policies, retention, DLQ handling and reconciliation.

## Validation
Simulate broker outage, relay crash after publish, duplicate deliveries and event-ordering changes. Demonstrate that no committed order lacks a retained outbox record.
