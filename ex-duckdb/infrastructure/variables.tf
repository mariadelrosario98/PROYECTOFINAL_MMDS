variable "prefix" {
  description = "Prefix for the resources"
  type        = string
  default = "papirelar"
}
 
variable "bucket_name" {
  description = "S3 bucket used for deployment"
  type        = string
  default = "papirelar-db73d78d9436d9b3"
}
 
variable "instance_type" {
  description = "Instance type to use"
  type        = string
  default     = "m5.2xlarge"
}
 
variable "script_path" {
  description = "Script initializer path"
  type        = string
}
 
variable "experiment_name" {
  description = "Script initializer path"
  type        = string
}
 
 
variable "source_name" {
  description = "Script initializer path"
  type        = string
}

variable "data_size" {
  description = "Script initializer path"
  type        = string
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "profile" {
  type        = string
  description = "Perfil de AWS CLI a usar"
  default     = "papirelar"
}