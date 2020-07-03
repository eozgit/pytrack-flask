from rest.root import db


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