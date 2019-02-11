### Setup steps (linux/mac)

Python version - 3.6.7
Pip version - 18.1

 1. Clone repo
 2. Create virtual environment `python -m venv venv`
 3. Activate virtual environment `source venv/bin/activate`
 4. Upgrade pip `pip install --upgrade pip`
 5. Install dependencies `pip install -r requirements.txt`
 6. create file in project main directory `touch rds_postgres.env` with the following contents:
 
_dev only configuration_
```.env
DB_USR=user
DB_PWD=password
DB_ENPOINT=db_server
DB_NAME=db_name
DB_PORT=port
SECRET_KEY=nosecretkey

```
 
 _to run locally_ - `flask run`  or  `python clouduav.py`


---

###  Zappa (AWS deployment)

This application is deployed to AWS using Zappa Framework - 

See the documentation - https://github.com/Miserlou/Zappa


 ---
### Database

#### Models
_see Database models `app/models.py`_


![CloudUAV UML](docs/cloudUAV_UML.jpg?raw=true "CloudUAV")

 * User - Users can be owners of the other entities or linked via `Personnel`
 
    A user can have multiple Sensors, UAV's, Projects
   
    The `User.avatar_path` is inteded as a path to user's image stored on s3 or other 
    
 * Personnel - Other people (users) who are linked to a particular user.  
 
    Personnel are people who participate in projects/missions
    
 * UAV - (or Drone) owned by a user and used for missions
 
 * Sensor - Sensor owned by a user

 * Mission - 1 UAV per mission

 * Project - A project has 1 project owner (User table relationship), 
 
    A project can have multiple missions associated

 * Role
 
    Each person (personnel) associated with a particular mission has a role

 * MissionSensors
    
    join table linking sensors to missions in many-to-many relationship (missions can have multiple sensors)


 * ProjectMissionPersonnelRole
 
    `user_id` in this context refers to the mission personnel and their role
 
 
#### Flask Migrate

https://flask-migrate.readthedocs.io/en/latest/

_to apply database model changes_

```
flask db migrate
flask db upgrade
```

 
#### Terraform
https://www.terraform.io/intro/getting-started/install.html

The database is deployed to AWS RDS using the Terraform script: `cloud-uav-backend/terraform/rds-clouduav.tf`


##### init 

```
cd /cloud-uav/backend/db/terraform
terraform init
```

##### create database in RDS

``` 
terraform apply
```

##### destroy

```
terraform destroy
```

---
### Links

FLASK - http://flask.pocoo.org/

FLASK MIGRATE - https://flask-migrate.readthedocs.io/en/latest/

FLASK RESTLESS - https://flask-restless.readthedocs.io/en/stable/

FLASK SQLALCHEMY - http://flask-sqlalchemy.pocoo.org/2.3/

MARSHMALLOW - https://flask-marshmallow.readthedocs.io/en/latest/\

SQLALCHEMY - https://docs.sqlalchemy.org/en/latest/

TERRAFORM - https://www.terraform.io/intro/getting-started/install.html

ZAPPA - https://github.com/Miserlou/Zappa

