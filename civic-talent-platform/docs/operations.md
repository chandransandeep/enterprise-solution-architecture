# Operations and service reliability

- `/health/live` checks process responsiveness. Liveness should not depend on external services or it can trigger cascading restarts.
- `/health/ready` checks DB connectivity; on a failure the instance should temporarily stop receiving requests.
- Every response has `X-Request-ID`; logs include method, path, HTTP status and duration.
- Avoid putting candidate attributes in logs. Ship JSON to an aggregator in actual deployments.
- Suggested alerts: API 5xx error rate, latency p95, readiness flapping, DB connection exhaustion, disk utilization, failed backups, elevated authorization failures.
- Measure availability and latency using both load tests and realistic traffic; define SLO burn alerts.
- Deployment lifecycle: PR -> unit/integration/security tests -> image build -> signed image -> staging -> smoke test -> approved canary/rolling production deployment -> rollback when alerts breach thresholds.
- CI in this repository runs tests and builds a local Docker image. It does not publish/deploy or incur cloud charges.
