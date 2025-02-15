from marshmallow import Schema, fields, validates_schema, ValidationError
from flask_login import UserMixin
from datetime import datetime, timezone

class User(UserMixin):
    def __init__(self, id):
        self.id = str(id)

class LoginSchema(Schema):
    username = fields.String()
    password = fields.String()
    remember = fields.Boolean()

    @validates_schema
    def validate_credentials(self, data, **kwargs):
        if not data.get('username'):
            raise ValidationError('Username is required')
        
        if not data.get('password'):
            raise ValidationError('Password is required')
        
        if len(data.get('password')) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not data.get('username').isalnum():
            raise ValidationError('Username must contain only letters and numbers')
        
        from db import client
        from werkzeug.security import check_password_hash

        user = client.db.users.find_one({'username': data['username']})

        if not user:
            raise ValidationError('Invalid username')
        
        if not check_password_hash(user['password'], data['password']): 
            raise ValidationError('Invalid password')

class RegisterSchema(LoginSchema):
    email = fields.String()
    repassword = fields.String()

    @validates_schema
    def validate_credentials(self, data, **kwargs):
        if not data.get('username'):
            raise ValidationError('Username is required')
        
        if not data.get('password'):
            raise ValidationError('Password is required')
        
        if not data.get('email'):
            raise ValidationError('Email is required')
        
        if len(data.get('password')) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not data.get('username').isalnum():
            raise ValidationError('Username must contain only letters and numbers')
        
        if data.get('password') != data.get('repassword'):
            raise ValidationError('Password does not match')
        
        from db import client

        user = client.db.users.find_one({'username': data['username']})

        if user:
            raise ValidationError('Username already exists')
        
        mail = client.db.users.find_one({'email': data['email']})

        if mail:
            raise ValidationError('Email already exists')
        
class UrlSchema(Schema):
    user_id = fields.String(required=True)
    original = fields.String(required=True) 
    shorted = fields.String(dump_only=True)
    click_count = fields.Integer(missing=0)
    created_at = fields.DateTime(dump_only=True, missing=datetime.now(timezone.utc))
    expire_date = fields.Date(required=False)
    last_clicked_at = fields.DateTime(required=False)


