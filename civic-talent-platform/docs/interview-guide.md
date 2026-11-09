# Explain this project in a Solution Architect interview

## Honest two-minute narrative

"My professional background is in enterprise application, integration and data architecture. To expand my cross-platform skills, I built Civic Talent Platform, a fictional recruitment workflow demonstration. I designed the relational model, a validated REST API and status-transition rules; containerised the application with PostgreSQL; added automated tests and CI; and documented how the same workload could be operated using Kubernetes or AWS managed services. The cloud infrastructure remains a reference design, not a production deployment. This helped me compare architecture trade-offs around availability, security, deployment and operational ownership."

## Questions you should be able to answer

1. Why PostgreSQL over a document store? Relational integrity and uniqueness; JSON for bounded flexibility.
2. Why one API service rather than microservices? Modest domain and deployment complexity; a split can follow real scaling/team boundaries.
3. What happens when DB is down? Readiness fails; requests may fail; HA/backup/retry strategy is a production design task.
4. Why is an API key insufficient? No user identity, roles, audit or tenant isolation.
5. Kubernetes versus ECS? Portability and scheduling flexibility versus lower operational burden.
6. What does CI verify? Tests and container construction. It does **not** establish security or production reliability.
7. How would you deploy safely? Secrets, private networking, HTTPS, review, migration, smoke test, canary, rollback.
8. How would you meet 99.9% availability? Multi-AZ DB, multiple healthy replicas, load balancing, measured SLOs and failure drills.
9. What would you improve next? OIDC/RBAC, tenant isolation, migrations, PostgreSQL integration tests and audit logs.
10. How does this relate to Pega? Familiar business rules, data models, APIs and architecture governance, expressed in a vendor-neutral stack.

Never present this learning scaffold as experience operating a production cloud platform.
