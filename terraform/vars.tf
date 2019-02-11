variable "project_name" {
  default = "clouduavdev"
}

variable "vpc_id" {
  default = "vpc-db804ea3"
}

variable "subnet_ids"{
  default = ["subnet-286f4572", "subnet-404e0b0b", "subnet-acda82d5"]
}

variable "internet_cidr" {
  description = "CIDR for internet access"
  default     = "0.0.0.0/0"
}


variable "db_master_password" {}

variable "database_name"{
  default = "clouduavdev"
}
