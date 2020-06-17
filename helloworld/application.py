#!flask/bin/python
import os
import datetime
import json
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from jose import jwt
from helloworld.flaskrun import flaskrun

application = Flask(__name__)
sqlalchemy_database_uri_key = 'SQLALCHEMY_DATABASE_URI'
if sqlalchemy_database_uri_key in os.environ:
    application.config[sqlalchemy_database_uri_key] = os.environ[sqlalchemy_database_uri_key]

db = SQLAlchemy(application)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    owner = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Project %r>' % self.name


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    type = db.Column(db.Integer, nullable=False)
    assignee = db.Column(db.String(50))
    storypoints = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    index = db.Column(db.Integer, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
                           nullable=False)
    project = db.relationship('Project',
                              backref=db.backref('issues', lazy=True))

    def __repr__(self):
        return '<Issue %r>' % self.title


class ProjectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    owner = fields.Str(dump_only=True)


class IssueSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    type = fields.Int()
    assignee = fields.Str()
    storypoints = fields.Int()
    status = fields.Int()
    priority = fields.Int()
    index = fields.Int()
    project = fields.Nested(ProjectSchema)


project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)

projects = [
    {'project_id': 0, 'name': 'Star Wars: Episode IV', 'description': 'A New Hope'},
    {'project_id': 1, 'name': 'Star Wars: Episode V', 'description': 'The Empire Strikes Back'},
    {'project_id': 2, 'name': 'Star Wars: Episode VI', 'description': 'Return of the Jedi'}
]
count = len(projects)


@application.route('/time', methods=['GET'])
def time():
    response = Response(json.dumps({'Output': str(datetime.datetime.now())}), mimetype='application/json', status=200)
    return response


@application.route('/env', methods=['GET'])
def env():
    s = ''
    for key, value in os.environ.items():
        s += key + ': ' + value + '\n'
    response = Response(s, mimetype='application/json', status=200)
    return response


@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/projects', methods=['GET'])
def list_projects():
    username = get_username(request)

    _projects = Project.query.filter(Project.owner == username).all()

    if len(_projects) == 0:
        add_sample_projects(db.session, username)
        _projects = Project.query.filter(Project.owner == username).all()

    result = projects_schema.dump(_projects)

    return Response(json.dumps(result), mimetype='application/json', status=200)


@application.route('/projects', methods=['POST'])
def create_project():
    project = request.get_json()
    global count
    project['project_id'] = count
    count += 1
    projects.append(project)
    return Response(json.dumps(project), mimetype='application/json', status=200)


@application.route('/projects/<int:project_id>', methods=['GET'])
def read_project(project_id):
    global projects
    project = [p for p in projects if p['project_id'] == project_id][0]
    return Response(json.dumps(project), mimetype='application/json', status=200)


@application.route('/projects/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    patch = request.get_json()
    global projects
    project = [p for p in projects if p['project_id'] == project_id][0]
    if 'name' in patch and patch['name']:
        project['name'] = patch['name']
    if 'description' in patch and patch['description']:
        project['description'] = patch['description']
    return Response(json.dumps(project), mimetype='application/json', status=200)


@application.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    global projects
    project = [p for p in projects if p['project_id'] == project_id][0]
    projects.remove(project)
    return Response(json.dumps(project), mimetype='application/json', status=200)


def get_username(request):
    token = request.headers['authorization'][7:]
    claims = jwt.get_unverified_claims(token)
    return claims['cognito:username']


def add_sample_projects(session, username):
    swiv = Project(name='Star Wars: Episode IV', description='A New Hope', owner=username)
    swv = Project(name='Star Wars: Episode V', description='The Empire Strikes Back', owner=username)
    swvi = Project(name='Star Wars: Episode VI', description='Return of the Jedi', owner=username)
    session.add(swiv)
    session.add(swv)
    session.add(swvi)
    session.commit()


if __name__ == '__main__':
    flaskrun(application)
