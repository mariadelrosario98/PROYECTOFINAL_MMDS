terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "terraforms3backend21-paulapirela-terraform-state"
    key = ""
    region = "us-east-1"
    encrypt    = true
    kms_key_id = "752bf32d-a3a0-4783-95f4-8f479f83a702"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Topic = "terraform"
    }
  }
}