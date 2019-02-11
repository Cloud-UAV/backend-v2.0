from flask import jsonify, request
from sqlalchemy import and_

from app import manager, app
from app.models import *


# SCHEMAS
user_schema = UserSchema()
# personnel_schema = UserSchema(many=True)
personnel_schema_linkless = PersonnelSchemaLinkless(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
uav_schema = UAVSchema()
uavs_schema = UAVSchema(many=True)
# sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)
mission_schema = MissionSchema()
missions_schema = MissionSchema(many=True)
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']


# HOME ROUTE
@app.route('/', methods=['GET'])
def main():
    return jsonify(dict(
        name='CloudUAV API',
        version=0.1,
        routes_allowed=[
            '/api/user',
            '/api/project',
            '/api/uav',
            '/api/sensor',
            '/api/mission',
            '/api/personnel',
            '/api/role'
        ]
    )), 200


@app.route('/api/personnel', methods=['POST'], defaults={'user_id': None})
@app.route('/api/personnel/<user_id>', methods=['GET', 'PATCH', 'DELETE'])
def personnel(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)
        personnel = user.user_personnel
        if len(personnel) > 0:
            return jsonify(personnel_schema_linkless.dump(personnel).data)
        else:
            return jsonify(personnel)
    elif request.method == 'PATCH':
        data = request.get_json()
        user = User.query.get(user_id)
        user.first_name = data.get('first_name') or user.first_name
        user.last_name = data.get('last_name') or user.last_name
        user.phone_number = data.get('phone_number') or user.phone_number
        user.email = data.get('email') or user.email
        user.avatar_path = data.get('avatar_path') or user.avatar_path
        user.last_name = data.get('last_name') or user.last_name
        user.last_name = data.get('last_name') or user.last_name
        user.last_name = data.get('last_name') or user.last_name
        personnel_ids = data.get('user_personnel')
        for person_id in personnel_ids:
            person = User.query.get(person_id)
            u = user.attach_personnel(person)
            db.session.add(u)

        # uncomment below to remove users from attached
        # user_personnel_ids = [p.id for p in user.user_personnel]
        # personnel_diff = set(user_personnel_ids) - set(personnel_ids)
        # for person_id in personnel_diff:
        #     person = User.query.get(person_id)
        #     u = user.detach_personnel(person_id)
        #     db.session.add(u)

        db.session.commit()
        ret = jsonify(user_schema.dump(user).data)
        # del ret['personnel']
        return ret


@app.route('/api/test_mission', methods=['POST'], defaults={'mission_id': None})
@app.route('/api/test_mission/<mission_id>', methods=['GET', 'PATCH', 'DELETE'])
def mission(mission_id):
    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        """ 
            json structure:
                {
                    "name": "",
                    "description": "",
                    "start": "",
                    "end": "",
                    "uav_id": "",
                    "project": "",
                    "personnel": [
                        {
                            "id": 1, "role_ids": [1, 2, 3]
                        }
                    ],
                    "sensors": [{"id": 1}],
                    "project": 1
                }, 

        """
        data = request.get_json()
        project_id = data.get('project') or None
        mission = Mission()
        mission.name = data.get('name') or None
        mission.description = data.get('description') or None
        mission.start = data.get('start') or None
        mission.end = data.get('end') or None
        mission.uav_id = data.get('uav_id') or None
        mission.project_id = project_id

        db.session.add(mission)
        db.session.commit()

        personnel = data.get('personnel') or None

        if personnel is not None:
            for person in personnel:
                role_ids = person.get('role_ids')
                for role_id in role_ids:
                    pmpr = ProjectMissionPersonnelRole(
                        project_id=project_id,
                        role_id=role_id,
                        mission_id=mission.id,
                        user_id=person.get('id')
                    )
                    db.session.add(pmpr)

        db.session.commit()

        return jsonify(mission_serializer(mission))

    elif request.method == 'PATCH':
        pass

    elif request.method == 'DELETE':
        # first delete all links from join table
        pmpr_list = ProjectMissionPersonnelRole.query.filter_by(mission_id=mission_id).all()
        for pmpr in pmpr_list:
            db.session.delete(pmpr)
            db.session.commit()

        # then delete mission itself
        mission = Mission.query.get(mission_id)
        db.session.delete(mission)
        db.session.commit()
        return '', 204


def mission_serializer(mission):
    ret = mission_schema.dump(mission).data
    personnel = personnel_schema_linkless.dump(mission.personnel).data

    roles = roles_schema.dump(mission.roles).data
    sensors = sensors_schema.dump(mission.sensors).data
    uav = uav_schema.dump(mission.uav).data
    ret['personnel'] = personnel
    for person in personnel:
        person_role_ids = db.session.query(Role)\
            .filter(and_(Role.id == ProjectMissionPersonnelRole.role_id,
                    ProjectMissionPersonnelRole.mission_id == mission.id,
                    ProjectMissionPersonnelRole.user_id == person['id'])).add_columns('id').all()

        role_id_list = [role_id['id'] for role_id in roles_schema.dump(person_role_ids).data]
        person['role_ids'] = role_id_list

    ret['roles'] = roles
    ret['sensors'] = sensors
    ret['uav'] = uav
    return ret


def project_serializer(project):
    ret = project_schema.dump(project).data
    personnel = personnel_schema_linkless.dump(project.personnel).data
    roles = roles_schema.dump(project.roles).data
    missions = [mission_serializer(mission) for mission in project.missions]
    ret['personnel'] = personnel
    ret['roles'] = roles
    ret['missions'] = missions
    return ret


def user_serializer(user):
    ret = user_schema.dump(user).data
    projects = [project_serializer(project) for project in user.projects]
    missions, personnel, roles = [], [], []
    user_personnel = []

    for person_id in ret.get('user_personnel'):
        person = User.query.get(person_id)
        user_personnel.append(person)
    user_personnel = personnel_schema_linkless.dump(user_personnel).data

    ids_only_projects = []
    for project in projects:
        ids_only_missions = []
        for mission in project.get('missions'):
            mission_cp = mission
            ids_only_personnel = []
            for person in mission.get('personnel'):
                ids_only_personnel.append({'id': person.get('id'), 'role_ids': person.get('role_ids')})
                del person['role_ids']
                personnel.append(person) if person not in personnel else None
            for role in mission.get('roles'):
                roles.append(role) if role not in roles else None
            ids_only_sensors = []
            for sensor in mission.get('sensors'):
                ids_only_sensors.append({'id': sensor.get('id')})
            missions.append(mission_cp) if mission not in missions else None
            id_only_uav = {'id': mission.get('uav').get('id')}
            del mission['uav']
            del mission['personnel']
            del mission['roles']
            del mission['sensors']

            ids_only_missions.append(
                {
                    'id': mission.get('id'),
                    'personnel': ids_only_personnel,
                    'sensors': ids_only_sensors,
                    'uav': id_only_uav
                }
            )
        ids_only_projects.append(
            {
                'id': project.get('id'),
                'name': project.get('name'),
                'description': project.get('description'),
                'start': project.get('start'),
                'end': project.get('end'),
                'missions': ids_only_missions
            }
        )

    uavs = uavs_schema.dump(user.uavs).data
    sensors = sensors_schema.dump(user.sensors).data

    ret['missions'] = missions
    # ret['personnel'] = personnel
    ret['personnel'] = user_personnel
    ret['projects'] = ids_only_projects
    ret['roles'] = [role_schema.dump(role).data for role in user.roles]
    ret['sensors'] = sensors
    ret['uavs'] = uavs
    del ret['user_personnel']

    return ret


# https://flask-restless.readthedocs.io/en/stable/
manager.create_api(User, methods=methods, serializer=user_serializer)
manager.create_api(Project, methods=methods, serializer=project_serializer)
manager.create_api(UAV, methods=methods)
manager.create_api(Sensor, methods=methods)
manager.create_api(Mission, methods=methods, serializer=mission_serializer)
manager.create_api(MissionSensors, methods=methods)
manager.create_api(Role, methods=methods)
