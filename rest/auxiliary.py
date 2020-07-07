from random import randrange
from jose import jwt

from model.project import Project
from model.issue import Issue
from rest.seed_data import projects_data


def get_username(request):
    return 'eozgit'
    token = request.headers['authorization'][7:]
    claims = jwt.get_unverified_claims(token)
    return claims['cognito:username']


def update_indices(status, index, issue, issues):
    status_changed = issue.status != status
    index_changed = issue.index != index
    if status_changed:
        to_update = [i for i in issues if i.status == issue.status and i.index > issue.index]
        for i in to_update:
            i.index -= 1
        to_update = [i for i in issues if i.status == status and i.index >= index]
        for i in to_update:
            i.index += 1
        issue.status = status
    elif index_changed:
        up = index < issue.index
        if up:
            to_update = [i for i in issues if
                         i.status == issue.status and issue.index > i.index >= index]
            for i in to_update:
                i.index += 1
        else:
            to_update = [i for i in issues if
                         i.status == issue.status and index >= i.index > issue.index]
            for i in to_update:
                i.index -= 1
    issue.index = index


def add_sample_projects(session, username):
    for project_data in projects_data:
        name = truncate(project_data['name'], 40)
        description = truncate(project_data['description'], 90)
        project = Project(name=name, description=description, owner=username)
        issues = project_data['issues']
        count = len(issues)
        for (i, issue_data) in enumerate(issues):
            title = truncate(issue_data['title'], 40)
            description = truncate(issue_data['description'], 90)

            if i < count * .1:
                status = 3
                index = 0
            elif i < count * .3:
                status = 2
                index = i - 1
            elif i < count * .6:
                status = 1
                index = i - 3
            else:
                status = 0
                index = i - 5

            issue = Issue(title=title, description=description, project=project, type=get_type(), assignee='',
                          storypoints=get_storypoints(), status=status, priority=get_priority(), index=index)
            session.add(issue)
        session.add(project)
    session.commit()


def get_type():
    r = randrange(8)
    if r < 5:
        return 0
    elif r < 7:
        return 1
    else:
        return 2


def get_storypoints():
    fibonacci = [1, 2, 3, 5, 8, 13, 21]
    r = randrange(21)
    for i, f in enumerate(fibonacci):
        if r < f:
            return fibonacci[len(fibonacci) - i - 1]


def get_priority():
    r = randrange(10)
    if r < 1:
        return 0
    elif r < 3:
        return 1
    elif r < 7:
        return 2
    elif r < 9:
        return 3
    else:
        return 4


def truncate(text, length):
    return text if len(text) < length else text[:length] + '…'
