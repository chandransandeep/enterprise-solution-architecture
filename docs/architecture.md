# Proposed solution architecture

This is a **logical design**, intentionally cloud-provider neutral. Vendor choice should follow requirements, pricing, support model and operational maturity.

## System context

```mermaid
flowchart LR
    Customer["Customer"] --> Platform["DemoMart commerce platform"]
    Support["Support agent"] --> Platform
    Platform --> Payment["Hosted payment processor"]
    Platform --> Courier["Third-party courier"]
    Platform --> IdP["Identity service"]
```

## Logical containers

```mermaid
flowchart TB
    subgraph Edge["Public edge"]
      CDN["CDN + WAF"] --> BFF["Backend-for-frontend / gateway"]
    end
    subgraph Private["Private application network"]
      BFF --> Catalogue["Catalogue module"]
      BFF --> Orders["Order module"]
      Orders --> OrderDB[("Orders DB")]
      Orders --> Outbox[("Outbox table")]
      Outbox --> Relay["Outbox relay"]
      Relay --> Bus["Durable event bus"]
      Bus --> Fulfilment["Fulfilment adapter"]
      Bus --> Projection["Order-status projector"]
      Projection --> ReadDB[("Read model")]
    end
    Orders --> Payment["Tokenised payment API"]
    Fulfilment --> Courier["Courier API"]
```

## Order lifecycle

```mermaid
sequenceDiagram
    actor Buyer
    participant API as Checkout API
    participant DB as Orders DB + outbox
    participant PSP as Hosted payment API
    participant Bus as Event bus
    participant Ship as Fulfilment adapter
    Buyer->>API: POST order + idempotency key
    API->>DB: Reserve order ID (transaction)
    API->>PSP: Create payment intent (idempotent)
    PSP-->>API: Tokenised result
    API->>DB: Confirm order + record event atomically
    API-->>Buyer: 202 / order reference
    DB-->>Bus: Relay pending outbox event
    Bus-->>Ship: OrderPlaced
    Ship-->>Bus: FulfilmentRequested / status
```

### Failure and consistency semantics

- **Order DB:** source of truth for order state.
- **Outbox:** avoids committing an order without recording the event to publish.
- **Bus:** assume at-least-once delivery; consumers must deduplicate by event ID.
- **Payment:** use provider idempotency keys and reconcile ambiguous timeout outcomes; never assume a timeout equals a failed charge.
- **Fulfilment:** retries with backoff, dead-letter review, poison-message handling and an explicit reconciliation process.
- **Read projection:** eventually consistent; customer UI displays “processing” when appropriate.

## Trust boundaries

Public web traffic crosses WAF and authentication boundaries. Internal components authenticate using short-lived workload identities and only access required services. Payment card entry occurs on the hosted provider surface; logs must redact personal identifiers and tokens.

## Deployment view

Deploy gateway and stateless components across at least two availability zones, use managed encrypted storage and a managed queue, and use separate development/staging/production accounts or subscriptions. Set resource quotas, autoscaling bounds and cost alerts.

## Observability

Trace a request using a correlation ID across API, outbox, event relay and fulfilment. Track checkout success, queue age, consumer failures, time-to-reconcile and payment ambiguity rates. Audit administrative access separately.
