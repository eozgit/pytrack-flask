import os
from datetime import datetime
import json
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import psycopg2
from jose import jwt

app = Flask(__name__)
pytrack_db = os.environ.get("PYTRACK_DB")
app.config['SQLALCHEMY_DATABASE_URI'] = pytrack_db
db = SQLAlchemy(app)


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


@app.route("/")
def hello():
    return "Hello!"


@app.route('/time')
def path():
    return str(datetime.now())


@app.route("/connect")
def postgres_test():
    try:
        conn_str = os.environ.get("PYTRACK_DB")
        conn = psycopg2.connect(conn_str + " connect_timeout=1")
        conn.close()
    except psycopg2.OperationalError:
        return 'Connection failed.'
    else:
        return 'Connected.'


@app.route("/projects")
def get_projects():
    username = get_username(request)

    _projects = Project.query.filter(Project.owner == username).all()

    if len(_projects) == 0:
        add_sample_projects(db.session, username)
        _projects = Project.query.filter(Project.owner == username).all()

    result = projects_schema.dump(_projects)

    return Response(json.dumps(result), mimetype='application/json', status=200)


def get_username(request):
    token = request.headers['authorization'][7:]
    claims = jwt.get_unverified_claims(token)
    return claims['cognito:username']


def add_sample_projects(session, username):
    swiv = Project(name='Star Wars: Episode IV',
                   description='A New Hope', owner=username)
    swv = Project(name='Star Wars: Episode V',
                  description='The Empire Strikes Back', owner=username)
    swvi = Project(name='Star Wars: Episode VI',
                   description='Return of the Jedi', owner=username)
    session.add(swiv)
    session.add(swv)
    session.add(swvi)
    session.commit()
