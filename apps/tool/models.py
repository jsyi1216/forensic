from mongoengine import Document, fields, DictField

class Predict(Document):
    inputs = fields.ListField()
    preprocessings = fields.ListField()

class Model(Document):
    name = fields.StringField(required=True)
    group = fields.StringField(required=True)
    klass = fields.StringField(required=True)
    algorithm = fields.StringField(required=True)
    accuracy = fields.DictField(required=True)
    hyperparameters = fields.DictField(required=True)
    dataset = fields.DictField(required=True)
    inputformat = fields.StringField(required=True)
    default = fields.StringField(required=True)
    active = fields.StringField(required=True)
    description = fields.StringField(required=True)
    user = fields.DictField(required=True)
    createdate = fields.StringField(required=True)
    modifieddate = fields.StringField(required=True)

class Preprocessing(Document):
    code = fields.IntField(required=True)
    desc = fields.StringField(required=True)
    createdate = fields.StringField(required=True)
    modifieddate = fields.StringField(required=True)
