#!flask/bin/python
import datetime
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun

application = Flask(__name__)

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


@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/projects', methods=['GET'])
def list_projects():
    return Response(json.dumps(projects), mimetype='application/json', status=200)


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


if __name__ == '__main__':
    flaskrun(application)
