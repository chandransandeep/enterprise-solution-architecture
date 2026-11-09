terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type = string
  default = "eu-west-2"
}
variable "project" {
  type = string
  default = "civic-talent-demo"
}
variable "container_image" {
  type = string
  description = "Approved ECR image URI"
}
variable "database_password" {
  type = string
  sensitive = true
}
variable "api_key" {
  type = string
  sensitive = true
}

# Reference-only low-complexity AWS topology: public-facing Fargate + private RDS.
# Not hardened or applied. For real workloads: private ECS networking, ALB/WAF,
# HTTPS, Secrets Manager, backups, audit trails, IAM least privilege and budgets.
data "aws_availability_zones" "available" { state = "available" }
resource "aws_vpc" "main" {
  cidr_block = "10.42.0.0/16"
  enable_dns_hostnames = true
  tags = {Name = var.project}
}
resource "aws_subnet" "public_a" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.42.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
}
resource "aws_subnet" "private_a" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.42.11.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
}
resource "aws_subnet" "private_b" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.42.12.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]
}
resource "aws_internet_gateway" "igw" { vpc_id = aws_vpc.main.id }
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}
resource "aws_route_table_association" "public" {
  subnet_id = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}
resource "aws_security_group" "api" {
  name = "${var.project}-api"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port = 8000
    to_port = 8000
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_security_group" "db" {
  name = "${var.project}-db"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    security_groups = [aws_security_group.api.id]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_db_subnet_group" "db" {
  name = "${var.project}-db"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}
resource "aws_db_instance" "db" {
  identifier = var.project
  allocated_storage = 20
  engine = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro"
  db_name = "talent"
  username = "talent"
  password = var.database_password
  db_subnet_group_name = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible = false
  storage_encrypted = true
  skip_final_snapshot = true # Training only; unsafe for production data.
}
resource "aws_ecs_cluster" "main" { name = var.project }
resource "aws_iam_role" "execution" {
  name = "${var.project}-ecs-execution"
  assume_role_policy = jsonencode({Version = "2012-10-17", Statement = [{Effect = "Allow", Principal = {Service = "ecs-tasks.amazonaws.com"}, Action = "sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "execution" {
  role = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_cloudwatch_log_group" "api" {
  name = "/ecs/${var.project}"
  retention_in_days = 7
}
resource "aws_ecs_task_definition" "api" {
  family = var.project
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = aws_iam_role.execution.arn
  container_definitions = jsonencode([{name = "api", image = var.container_image, essential = true, portMappings = [{containerPort = 8000}], environment = [{name = "DATABASE_URL", value = "postgresql+psycopg://talent:${urlencode(var.database_password)}@${aws_db_instance.db.address}:5432/talent"}, {name = "API_KEY", value = var.api_key}], logConfiguration = {logDriver = "awslogs", options = {"awslogs-group" = aws_cloudwatch_log_group.api.name, "awslogs-region" = var.region, "awslogs-stream-prefix" = "api"}}}])
}
resource "aws_ecs_service" "api" {
  name = var.project
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    subnets = [aws_subnet.public_a.id]
    security_groups = [aws_security_group.api.id]
    assign_public_ip = true
  }
}

# NOTE: This example exposes HTTP and secrets via task definition/state. DO NOT APPLY
# to any public or sensitive workload. This exists solely to read Terraform syntax.
