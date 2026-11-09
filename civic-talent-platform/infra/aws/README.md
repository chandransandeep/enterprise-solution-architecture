# AWS Terraform learning example — do not apply

This folder demonstrates provider configuration, VPC/subnet topology, security groups, managed PostgreSQL, ECS/Fargate, CloudWatch Logs and task definitions. It is a **non-deployable learning scaffold for public use**, not a production blueprint.

The example deliberately lacks the controls necessary for a secure deployment, including TLS termination, ALB/WAF, secrets delivery via Secrets Manager, private app subnets, IAM task policy review, production database backups and deletion protection. Terraform state would also expose sensitive values. No cloud charges have been incurred and no resources have been provisioned.

For a genuine deployment, redesign and review these controls before running `terraform apply`. `terraform fmt` and `terraform validate` are appropriate read-only checks when Terraform is installed.
