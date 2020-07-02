import os
import logging
from datetime import datetime
import json
from flask import Flask, Response, request, send_from_directory, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from jose import jwt
from dotenv import load_dotenv

from seed_data import projects_data

logging.basicConfig(filename='pytrack.log', level=logging.DEBUG)
load_dotenv()
app = Flask(__name__)
cors = CORS(app)
pytrack_db = os.environ.get('PYTRACK_DB')
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
                              backref=db.backref('issues', lazy=True, cascade="all,delete,delete-orphan"))

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


@app.route('/')
def hello():
    return 'Hello!'


@app.route('/time')
def path():
    return str(datetime.now())


@app.route('/projects')
def get_projects():
    username = get_username(request)

    _projects = Project.query.filter(Project.owner == username).order_by(Project.id).all()

    if len(_projects) == 0:
        add_sample_projects(db.session, username)
        _projects = Project.query.filter(Project.owner == username).order_by(Project.id).all()

    result = projects_schema.dump(_projects)

    return Response(json.dumps(result), mimetype='application/json',
                    status=200)


@app.route('/projects', methods=['POST'])
def create_project():
    username = get_username(request)

    body = request.get_json()
    data = project_schema.load(body)
    project = Project(name=data['name'], description=data['description'], owner=username)
    db.session.add(project)
    db.session.commit()

    result = project_schema.dump(Project.query.get(project.id))
    return Response(json.dumps(result), mimetype='application/json',
                    status=200)


@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    username = get_username(request)
    project = Project.query.get(project_id)
    if project.owner == username:
        result = project_schema.dump(project)
        db.session.delete(project)
        db.session.commit()
        return Response(json.dumps(result), mimetype='application/json', status=200)
    else:
        abort(403)


@app.route('/projects/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    username = get_username(request)
    project = Project.query.get(project_id)
    if project.owner == username:
        body = request.get_json()
        data = project_schema.load(body)
        project.name = data['name']
        project.description = data['description']
        db.session.commit()
        result = project_schema.dump(project)
        return Response(json.dumps(result), mimetype='application/json', status=200)
    else:
        abort(403)


@app.errorhandler(Exception)
def all_exception_handler(error):
    logging.error(error)
    return 'Error', 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_username(request):
    token = request.headers['authorization'][7:]
    claims = jwt.get_unverified_claims(token)
    return claims['cognito:username']


def add_sample_projects(session, username):
    for project_data in projects_data:
        name = truncate(project_data['name'], 40)
        description = truncate(project_data['description'], 90)
        project = Project(name=name, description=description, owner=username)
        for (i, issue_data) in enumerate(project_data['issues']):
            title = truncate(issue_data['title'], 40)
            description = truncate(issue_data['description'], 90)

            if i == 0:
                status = 0
                index = 0
            elif i < 3:
                status = 1
                index = i - 1
            elif i < 5:
                status = 2
                index = i - 3
            else:
                status = 3
                index = i - 5

            issue = Issue(title=title, description=description, project=project, type=0, assignee='', storypoints=3,
                          status=status, priority=0, index=index)
            session.add(issue)
        session.add(project)
    session.commit()


def truncate(text, length):
    return text if len(text) < length else text[:length] + '…'


# if __name__ == '__main__':
#     app.run()
