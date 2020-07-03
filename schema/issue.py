from marshmallow import Schema, fields

from schema.project import ProjectSchema


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
    project = fields.Nested(ProjectSchema, load_only=True)
