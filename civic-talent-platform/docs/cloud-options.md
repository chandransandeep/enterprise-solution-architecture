# Cloud options: AWS, GCP and on-premises

| Concern | AWS | Google Cloud | On-premises |
|---|---|---|---|
| Container compute | ECS Fargate or EKS | Cloud Run or GKE | Kubernetes / VMs |
| Relational database | RDS PostgreSQL | Cloud SQL PostgreSQL | Managed PostgreSQL cluster |
| Secrets | Secrets Manager | Secret Manager | Vault or enterprise secrets store |
| Monitoring | CloudWatch / OpenTelemetry | Cloud Monitoring / OpenTelemetry | Prometheus/Grafana/OpenTelemetry |
| Network boundary | VPC, ALB, security groups | VPC, load balancer, firewall | VLAN, firewall, reverse proxy |
| Automation | Terraform, GitHub Actions | Terraform, GitHub Actions | Terraform/Ansible, GitHub Actions |

## Why one architecture does not fit all

- Choose managed containers when operations capacity is limited.
- Choose Kubernetes when portability or workload orchestration requirements justify the higher operational cost.
- Choose on-premises when sovereignty, latency or existing platform constraints dominate.
- Decide with explicit cost, resilience, regulatory and team-skill assumptions, not cloud fashion.

The learning code runs locally. AWS and Kubernetes deployment configurations are architecture examples, and no GCP resources are created.
