from jose import jwt

from model.project import Project
from model.issue import Issue
from rest.seed_data import projects_data


def get_username(request):
    return 'eozgit'
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
