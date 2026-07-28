# 10. Terraform — Infrastructure as Code for Data Platforms

## Why Infrastructure as Code (IaC) Matters for Data Engineers
Manually clicking through a cloud console to create an S3 bucket, an IAM role, and a Glue job works fine ONCE — but it's not repeatable, not reviewable, not version-controlled, and impossible to reliably reproduce identically across dev/staging/production environments. **Terraform** (and cloud-native alternatives like CloudFormation/ARM/Bicep) lets you define your ENTIRE infrastructure as version-controlled, human-readable configuration files — treated with the same rigor (Git, PR review, CI/CD) as application code.

## Why Terraform Specifically (vs cloud-native IaC tools)
```
CloudFormation (AWS-only), ARM/Bicep (Azure-only), Deployment Manager (GCP-only):
  each locked to ONE specific cloud's own tooling/syntax

Terraform (HashiCorp, open-source): works across AWS, Azure, GCP, and
  hundreds of other providers using ONE consistent language (HCL) —
  the practical industry-standard choice for teams wanting a single,
  portable IaC skill/toolset regardless of which cloud(s) they use
```

## Basic Terraform Structure
```hcl
# main.tf — declare WHAT infrastructure should exist
provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "data_lake_raw" {
  bucket = "my-company-data-lake-raw"

  tags = {
    Environment = "production"
    Team        = "data-engineering"
    Project     = "orders-pipeline"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_lifecycle" {
  bucket = aws_s3_bucket.data_lake_raw.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_glue_catalog_database" "analytics_db" {
  name = "analytics"
}
```

## The Terraform Workflow
```bash
terraform init      # download required provider plugins
terraform plan       # show EXACTLY what will change (create/modify/destroy) — critical safety step
terraform apply      # actually make the changes, after reviewing the plan
terraform destroy    # tear down everything this configuration created (careful!)
```
**Why `terraform plan` is so important in production**: it shows you a preview of EXACTLY what will happen BEFORE anything actually changes — catching a mistake (like an unintended resource deletion) before it happens, rather than discovering it after the fact.

## State Management — Terraform's Most Important, Most Misunderstood Concept
```
Terraform tracks the CURRENT state of your infrastructure in a "state file"
(terraform.tfstate) — this is how it knows what already exists vs what needs
to be created/changed/destroyed on the next apply.

CRITICAL production practice: NEVER store the state file only locally on
one engineer's laptop — use REMOTE STATE (e.g., an S3 bucket + DynamoDB
for locking, or Terraform Cloud) so the whole team shares a single source
of truth, and concurrent changes don't corrupt each other.
```
```hcl
# Remote state configuration (AWS example)
terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state"
    key            = "data-platform/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"   # prevents two people applying simultaneously
  }
}
```

## Modules — Reusable Infrastructure Patterns
```hcl
# modules/data-lake-bucket/main.tf — a reusable pattern for "a properly configured
# data lake bucket with standard lifecycle policies and encryption"
variable "bucket_name" {}
variable "environment" {}

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = { Environment = var.environment }
}
# ... lifecycle rules, encryption config, etc., defined ONCE here ...

# In the main project, reuse this module for EVERY new data lake bucket needed,
# ensuring every single one automatically gets the same standard security/
# lifecycle configuration, rather than each engineer configuring it slightly
# differently (and likely imperfectly) by hand each time
module "raw_zone_bucket" {
  source      = "./modules/data-lake-bucket"
  bucket_name = "my-company-raw-zone"
  environment = "production"
}

module "curated_zone_bucket" {
  source      = "./modules/data-lake-bucket"
  bucket_name = "my-company-curated-zone"
  environment = "production"
}
```
**Real production value**: modules encode organizational best practices ONCE (proper encryption, tagging standards, lifecycle policies) and every team reuses them, rather than each pipeline/team reinventing (and likely under-securing) their own bucket configuration independently — a genuinely important consistency and security win at scale.

## A Real Data Platform Terraform Example (putting it together)
```hcl
# Provisioning a complete environment: S3 buckets, Glue catalog, IAM role for a pipeline
resource "aws_iam_role" "etl_pipeline_role" {
  name = "orders-etl-pipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
}

# Least-privilege policy — recap from file 9, expressed as versioned, reviewable code
resource "aws_iam_role_policy" "etl_pipeline_s3_access" {
  role = aws_iam_role.etl_pipeline_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = ["${aws_s3_bucket.data_lake_raw.arn}/*"]
    }]
  })
}
```
This exact pattern — infrastructure AND its security configuration defined together, versioned, and reviewed via a pull request — is how mature data engineering teams manage cloud environments in 2026, rather than manual console clicks that leave no audit trail of WHO configured WHAT, WHEN, or WHY.

## CI/CD for Terraform (tying into `10-devops/ci-cd/` in this repo)
```
Pull Request opened with Terraform changes
        |
        v
CI pipeline runs `terraform plan` automatically, posts the plan output
as a PR comment for human review (exactly what will change)
        |
   (human reviews and approves the PR)
        |
        v
CI pipeline runs `terraform apply` automatically upon merge to main
```
This "plan on PR, apply on merge" pattern brings the same code-review discipline to infrastructure changes that good engineering teams already apply to application code changes.

## Interview Traps
- "Why use Terraform instead of just clicking through the AWS/Azure/GCP console?" — repeatability, version control/PR review, consistency across environments (dev/staging/prod), and avoiding undocumented "how did this get configured" mysteries.
- "What is Terraform state and why does remote state matter?" — Terraform's record of what infrastructure currently exists; remote state (with locking) prevents team members' local state files from conflicting/corrupting each other and provides one shared source of truth.
- "How would you enforce security best practices across many teams' infrastructure?" — reusable Terraform modules encoding least-privilege IAM/encryption/tagging standards ONCE, so every team's infrastructure inherits them by default rather than reinventing (and likely under-securing) their own configuration.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"The one who gives knowledge without holding back is never truly poorer for it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
