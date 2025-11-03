# --------------------------------------------------------------------------------------------------
# 1. ROL DE IAM Y PERFIL DE INSTANCIA para SSM
# --------------------------------------------------------------------------------------------------

# Política de confianza (Trust Policy) para que EC2 pueda asumir este rol
data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

# 1.1. Creación del Rol de IAM
resource "aws_iam_role" "ssm_instance_role" {
  name               = "EC2-SSM-T2Medium-Role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

# 1.2. Adjuntar la política administrada de AWS (AmazonSSMManagedInstanceCore)
resource "aws_iam_role_policy_attachment" "ssm_policy_attachment" {
  role       = aws_iam_role.ssm_instance_role.name
  # Esta política es esencial para que la instancia pueda ser gestionada por SSM
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# 1.3. Creación del Perfil de Instancia (necesario para asociar el rol a la EC2)
resource "aws_iam_instance_profile" "ssm_instance_profile" {
  name = "EC2-SSM-T2Medium-Profile"
  role = aws_iam_role.ssm_instance_role.name
}

# --------------------------------------------------------------------------------------------------
# 2. GRUPO DE SEGURIDAD
# --------------------------------------------------------------------------------------------------

# Creamos un grupo de seguridad con acceso saliente (Outbound) abierto
# NO necesitamos abrir el puerto 22 (SSH) para el acceso por Session Manager
resource "aws_security_group" "ssm_sg" {
  name        = "ssm-only-access-sg"
  description = "Permite solo trafico saliente para que SSM funcione"
  # Asume que ya tienes un VPC ID o lo obtienes con un data source
  vpc_id      = var.vpc_id # Reemplazar con tu VPC ID

  # Regla de salida: Permite todo el tráfico saliente.
  # El SSM Agent necesita acceso a AWS por HTTPS (443)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "SSM-Only-SG"
  }
}

# --------------------------------------------------------------------------------------------------
# 3. INSTANCIA EC2 (t2.medium)
# --------------------------------------------------------------------------------------------------

# Opcional: Usar un data source para obtener la AMI más reciente de Amazon Linux 2
# Estas AMIs suelen traer preinstalado el SSM Agent.
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"] # ID de la cuenta de AWS para las AMIs de Amazon
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "t2_medium_ssm" {
  ami                         = data.aws_ami.amazon_linux_2.id
  instance_type               = "t2.medium"
  subnet_id                   = var.subnet_id # Reemplazar con tu Subnet ID
  vpc_security_group_ids      = [aws_security_group.ssm_sg.id]
  # Asocia el Perfil de Instancia que creamos en el paso 1
  iam_instance_profile        = aws_iam_instance_profile.ssm_instance_profile.name
  
  # Si la pones en una subred privada, esta opción debe ser 'false'
  # Si la pones en una subred pública (sin EIP), esta opción debe ser 'true'
  associate_public_ip_address = true 

  tags = {
    Name = "T2-Medium-with-SSM-Access"
  }
}