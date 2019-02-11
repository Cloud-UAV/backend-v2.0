from flask import session

from app import db, ma

from sqlalchemy.dialects.postgresql import JSONB


user_to_user = db.Table(
    'user_to_user',
    db.Column('person_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class User(db.Model):
    __tablename__ = 'user'

    # PK
    id = db.Column(db.Integer, primary_key=True)
    aws_cognito_id = db.Column(db.String)

    # ATTR
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone_number = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    avatar_path = db.Column(db.String)

    # RELATIONSHIPS
    uavs = db.relationship('UAV')
    sensors = db.relationship('Sensor')
    projects = db.relationship('Project')
    personnel = db.relationship(
        'User',
        secondary=user_to_user,
        primaryjoin=id == user_to_user.c.person_id,
        secondaryjoin=id == user_to_user.c.user_id,
        backref=db.backref('user_personnel', lazy='dynamic'),
        lazy='dynamic'
    )
    roles = db.relationship('Role')

    def attach_personnel(self, user):
        # attach personnel relationship
        if not self.is_attached(user):
            self.user_personnel.append(user)
        return self

    def detach_personnel(self, user):
        # remove personnel relationship
        if not self.is_attached(user):
            self.user_personnel.remove(user)
        return self

    def is_attached(self, user):
        # checks for attached personnel
        return self.user_personnel.filter(user_to_user.c.person_id == user.id).count() > 0


class Project(db.Model):
    __tablename__ = 'project'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK - the owner of the project
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # RELATIONSHIPS
    missions = db.relationship('Mission', lazy='joined', backref='project')
    roles = db.relationship('Role', secondary='project_mission_personnel_role', lazy='joined')
    personnel = db.relationship('User', secondary='project_mission_personnel_role', lazy='joined')

    # ATTR
    name = db.Column(db.String)
    description = db.Column(db.Text)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)


class UAV(db.Model):
    __tablename__ = 'uav'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # ATTR
    name = db.Column(db.String)
    description = db.Column(db.String)
    inventory = db.Column(JSONB)  # todo: decide on json structure for inventory


class Sensor(db.Model):
    __tablename__ = 'sensor'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # ATTR
    name = db.Column(db.String)
    description = db.Column(db.String)
    inventory = db.Column(JSONB)  # todo: decide on json structure for inventory


class Mission(db.Model):
    __tablename__ = 'mission'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    uav_id = db.Column(db.Integer, db.ForeignKey(UAV.id))
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id))

    # RELATIONSHIPS
    uav = db.relationship('UAV')
    # project = db.relationship('Project')
    personnel = db.relationship('User', secondary='project_mission_personnel_role', lazy='dynamic', cascade='all,delete')
    sensors = db.relationship('Sensor', secondary='mission_sensors', lazy='joined', cascade='all,delete')
    roles = db.relationship('Role', secondary='project_mission_personnel_role', lazy='dynamic')

    # ATTR
    name = db.Column(db.String)
    description = db.Column(db.Text)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)


class MissionSensors(db.Model):
    __tablename__ = 'mission_sensors'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    mission_id = db.Column(db.Integer, db.ForeignKey(Mission.id))
    sensor_id = db.Column(db.Integer, db.ForeignKey(Sensor.id, ondelete='SET NULL'))


class Role(db.Model):
    __tablename__ = 'role'

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # ATTR
    name = db.Column(db.String)
    description = db.Column(db.Text)


class ProjectMissionPersonnelRole(db.Model):
    __tablename__ = 'project_mission_personnel_role'

    # PK
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id), primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey(Mission.id), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id), primary_key=True)
    db.PrimaryKeyConstraint(project_id, mission_id, user_id, role_id)


# ------------------------ Schema --------------------------


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User


class RoleSchema(ma.ModelSchema):
    class Meta:
        model = Role


class PersonnelSchemaLinkless(ma.ModelSchema):
    class Meta:
        fields = [
            'avatar_path',
            'aws_cognito_id',
            'email',
            'id',
            'first_name',
            'last_name',
            'phone_number'
        ]


class ProjectSchema(ma.ModelSchema):
    class Meta:
        model = Project


class UAVSchema(ma.ModelSchema):
    class Meta:
        model = UAV


class SensorSchema(ma.ModelSchema):
    class Meta:
        model = Sensor


class MissionSchema(ma.ModelSchema):
    class Meta:
        fields = [
            'id',
            'name',
            'description',
            'start',
            'end',
            'project_id',
            'uav_id',
        ]


db.create_all()
