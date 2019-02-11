################################################################
## This file creates a RDS Postgres10 instance with a database #
## named clouduav. Master username is supgadmin.               #
################################################################

resource "aws_security_group" "db-sg" {
  name        = "ingress-to-${var.project_name}-db"
  description = "Ingress to ${var.project_name}-db"
  vpc_id      = "${var.vpc_id}"

  ingress {
    protocol        = "tcp"
    from_port       = "5432"
    to_port         = "5432"
    cidr_blocks = ["${var.internet_cidr}"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["${var.internet_cidr}"]
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "${var.project_name}-rds-subnet-group"
  description = "RDS subnet group"
  subnet_ids  = ["${var.subnet_ids}"]

}


resource "aws_db_instance" "rds" {
  identifier             = "${var.project_name}-db"
  allocated_storage      = "10"
  engine                 = "postgres"
  engine_version         = "10.4"
  instance_class         = "db.t2.micro"
  username               = "supgadmin"
  password               = "${var.db_master_password}"
  port                   = 5432
  db_subnet_group_name   = "${aws_db_subnet_group.rds_subnet_group.id}"
  vpc_security_group_ids = ["${aws_security_group.db-sg.id}"]
  final_snapshot_identifier = "${var.project_name}-db-final"

  publicly_accessible = true

  ## This is the name of the database created in RDS instance
  name = "${var.database_name}"

  tags = {
    Owner       = "${var.project_name}"
    Environment = "dev"
  }
}
