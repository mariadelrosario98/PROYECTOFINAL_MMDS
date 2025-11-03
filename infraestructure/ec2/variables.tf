
variable "region" {
  default = "us-east-1"
}

variable "instance_type" {
  description = "El tipo de la instancia EC2."
  type        = string
  # Cambiado a t2.medium, como pediste inicialmente
  default     = "t2.medium" 
}

variable "vpc_id" {
  description = "El ID de la VPC de destino para la instancia EC2."
  type        = string
}

variable "subnet_id" {
  description = "El ID de la Subnet de destino para la instancia EC2."
  type        = string
}


variable "ssh_allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"] 
}

# Puedes simplificar instance_user_data y user_data en una sola variable:
variable "instance_user_data" {
  description = "The cloud-init script to run on instance bootstrap."
  type        = string
  default     = <<-EOF
      #!/bin/bash
      apt-get update -y
      apt-get install -y python3 python3-pip -y 
      pip3 install pandas
      EOF
}