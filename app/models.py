from marshmallow import Schema, fields, validates_schema, ValidationError
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from requests import head, ConnectionError, Timeout, RequestException
from db import client
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id):
        self.id = str(id)

class LoginSchema(Schema):
    username = fields.String()
    password = fields.String()
    remember = fields.Boolean()

    @validates_schema
    def validate_credentials(self, data, **kwargs):
        username = data.get('username')
        password = data.get('password')

        if not username:
            raise ValidationError('Username is required')
        
        if not username.isalnum():
            raise ValidationError('Username must contain only letters and numbers')
        
        if not password:
            raise ValidationError('Password is required')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        user = client.db.users.find_one({'username': username})

        if not user:
            raise ValidationError('Invalid username')   
        elif not check_password_hash(user['password'], password): 
            raise ValidationError('Invalid password')

class RegisterSchema(LoginSchema):
    email = fields.String()
    repassword = fields.String()

    @validates_schema
    def validate_credentials(self, data, **kwargs):
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username:
            raise ValidationError('Username is required')
        
        if not password:
            raise ValidationError('Password is required')
        
        if not email:
            raise ValidationError('Email is required')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not username.isalnum():
            raise ValidationError('Username must contain only letters and numbers')
        
        if password != data.get('repassword'):
            raise ValidationError('Password does not match')
        
        from db import client

        user = client.db.users.find_one({'username': username})

        if user:
            raise ValidationError('Username already exists')
        
        is_email_exist = client.db.users.find_one({'email': email})

        if is_email_exist:
            raise ValidationError('Email already exists')
        
class UrlSchema(Schema):
    user_id = fields.String()
    url = fields.String() 
    shorted_code = fields.String()
    click_count = fields.Integer(missing=0)
    created_at = fields.DateTime(missing=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    expire_date = fields.DateTime()
    last_clicked_at = fields.DateTime()

    @validates_schema
    def validate_url(self, data, **kwargs):
        url = data.get('url')
        shorted_code = data.get('shorted_code')

        if not url: 
            raise ValidationError('Missing data')

        from .utils import UrlRegex 
        if not UrlRegex().validate_url(url): 
            raise ValidationError('Invalid URL')

        try: 
            response = head(url, timeout=5)
            if response.status_code not in (200, 301, 302): 
                raise ValidationError('URL is not working')
        except ConnectionError: 
            raise ValidationError('URL unreachable')
        except Timeout: 
            raise ValidationError('URL timed out')
        except RequestException as err: 
            raise ValidationError(err)
        
        user_id = data.get('user_id')

        if not user_id:
            data['expire_date'] = data.get('created_at') + timedelta(days=7)
        else: 
            data['expire_date'] = None