from marshmallow import Schema, fields


class ProjectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    owner = fields.Str(dump_only=True)