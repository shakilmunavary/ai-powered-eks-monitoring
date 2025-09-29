variable "aws_access_key" {
  type        = string
  description = "Your AWS access key"
  default = "aa"
}


variable "aws_region" {
  type        = string
  description = "Region"
  default = "us-west-2"
}


variable "aws_secret_key" {
  type        = string
  description = "Your AWS secret key"
  default = "aa"
}

variable "cluster_name" {
  type        = string
  description = "Name of your EKS cluster"
  default = "ai-eks-cluster"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where EKS will be deployed"
  default = "vpc-123"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs for EKS"
  default     = ["subnet-123", "subnet-456"]
}


variable "account_id" {
  default = "1234"
}

variable "oidc_provider" {
  default = "https://oidc.eks.us-west-2.amazonaws.com/id/12342323232xyz"
}
