# Security design review

This is a training application. Its single shared API key only demonstrates request authentication. It is **not sufficient for applicant data**, which would need consent, purpose limitation, retention policies and protection under applicable privacy law.

- Replace shared key with OIDC/OAuth2 identity provider, short-lived tokens, RBAC, least privilege and per-tenant isolation.
- Do not log names, emails, CVs, access tokens, headers or unredacted request bodies.
- Enforce TLS 1.2+, encrypted managed storage and secret rotation; use Secrets Manager or workload identity, never plain Terraform variables in ECS task definitions.
- Protect public endpoints with gateway, WAF, request-rate limiting and abuse controls.
- Encrypt and test database backups, implement deletion requests and documented retention.
- Run dependency, image, IaC and SAST scanning with pinned digests and reviewed upgrades.
- Keep DB private; use separate dev/staging/prod, reviewed deploy approvals and an audit trail.
- Threat-model injection, broken access controls, ID enumeration, DoS, privacy leakage and supply-chain compromise.
- The Kubernetes manifest needs network policy, TLS ingress and external secrets before deployment.

No AI ranking or hiring decision-making is included. Adding this would require a separate fairness, transparency, governance and human-review assessment.
