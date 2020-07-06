import os
import logging
from datetime import datetime
import json
from flask import Response, request, send_from_directory, abort
from sqlalchemy import and_

from model.issue import Issue
from rest.root import app, db
from model.project import Project
from schema.project import ProjectSchema
from schema.issue import IssueSchema
from rest.auxiliary import get_username, add_sample_projects, update_indices

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)


@app.route('/')
def hello():
    return 'Hello!'


@app.route('/time')
def time():
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


@app.route('/projects/<int:project_id>/issues')
def get_issues(project_id):
    username = get_username(request)

    project = Project.query.filter(and_(Project.owner == username, Project.id == project_id)).first()

    result = issues_schema.dump(project.issues)

    return Response(json.dumps(result), mimetype='application/json',
                    status=200)


@app.route('/projects/<int:project_id>/issues/<int:issue_id>', methods=['PATCH'])
def update_issue(project_id, issue_id):
    username = get_username(request)
    project = Project.query.get(project_id)
    if project.owner == username:

        body = request.get_json()
        data = issue_schema.load(body)
        issue = [i for i in project.issues if i.id == issue_id][0]  # project.issues.filter(Issue.id == issue_id)
        status_changed = issue.status != data['status']
        index_changed = issue.index != data['index']
        move_request = status_changed or index_changed

        if move_request:
            update_indices(data['status'], data['index'], issue, project.issues)
        else:
            issue.title = data['name']
            issue.description = data['description']
            issue.type = data['type']
            issue.assignee = data['assignee']
            issue.storypoints = data['storypoints']
            issue.priority = data['priority']

        db.session.commit()
        result = issue_schema.dump(issue)
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


# if __name__ == '__main__':
#     app.run()
