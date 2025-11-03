# main.tf

# Define los proveedores requeridos
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.83"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Configuración del proveedor AWS
provider "aws" {
  region = "us-east-1"
}

# --- VARIABLES ---

variable "prefix" {
  description = "Prefix for the bucket"
  type        = string
  default     = "livejournal-data-mds" 
}

# RUTA CORREGIDA: Usando barras inclinadas (/) en lugar de barras invertidas (\)
variable "file_path" {
  description = "Local path to the large data file"
  type        = string
  # RUTA CORREGIDA AQUÍ
  default     = "C:/Users/ASUS/Documents/Maestria Ciencia de los Datos/TERCER SEMESTRE/MINERIA DE GRANDES VOLUMENES INFO/PROYECTO FINAL/DATA/soc-LiveJournal1.txt" 
}

# --- RECURSOS ---

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 1. Crea el Bucket de S3
resource "aws_s3_bucket" "data_bucket" {
  bucket        = "${var.prefix}-${random_id.bucket_suffix.hex}"
  force_destroy = true 
}

# 2. Sube el Archivo Grande al Bucket
resource "aws_s3_bucket_object" "data_file" {
  bucket = aws_s3_bucket.data_bucket.id 
  key    = "raw/soc-LiveJournal1.txt"
  source = var.file_path 

  content_type = "text/plain"
  etag = filemd5(var.file_path)
}

# 3. Output (Muestra la URL del archivo subido)
output "s3_file_url" {
  value = "s3://${aws_s3_bucket.data_bucket.id}/${aws_s3_bucket_object.data_file.key}"
}