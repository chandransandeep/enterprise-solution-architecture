# ADR-0001: Start with modular service boundaries

## Status
Accepted for this fictional reference design.

## Context
DemoMart wants independent development and scalable catalogue reads but has a small platform team. Immediate deployment of many microservices would increase complexity and operational burden.

## Decision
Use a **modular API application** for catalogue and order functions, with explicit internal domain interfaces. Introduce an independently deployable fulfilment adapter only where external callbacks and queue-driven workloads justify it.

## Alternatives
1. Single unstructured monolith: lowest initial effort, poor boundary discipline.
2. Full microservices from day one: strong independent scaling, higher operational cost and distributed failure modes.
3. Modular core plus selected adapters: balanced migration path (**chosen**).

## Consequences
Positive: simpler operations, clearer ownership, manageable transactional consistency. Negative: some modules still share deployment cadence and database boundaries need enforcement. Revisit if team ownership and load profiles justify extracting services.

## Validation
Code review rules enforce module dependency direction. Test contract compatibility and record deployment lead-time and incident data.
