from flask import Blueprint, flash, render_template, request, url_for, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

from ..models import LoginSchema, RegisterSchema, User, ValidationError
from db import client
from bson import ObjectId

login_manager = LoginManager() 
login_manager.login_view = 'auth.login'
 
@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database.
    """
    user = client.db.users.find_one({"_id": ObjectId(user_id)})
    return User(user['_id']) if user else None

def handle_validate_data(schema, data, view):
    """
    Handle validation of data using a Marshmallow schema.
    """
    try: 
        schema().load(data)
    except ValidationError as err: 
        return err.messages


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    """
    if request.method == 'POST': 
        register_data = request.form.to_dict()
        error = handle_validate_data(RegisterSchema, register_data, 'auth.register')
        
        if error:
            flash(error)
            return redirect(url_for('auth.register'))
        
        client.db.users.insert_one({
            'username': register_data['username'],
            'password': generate_password_hash(register_data['password']),
            'email': register_data['email']
        })

        return redirect(url_for('auth.login'))
    elif request.method == 'GET':
        return render_template('auth/register.html')            


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    """
    if request.method == 'POST': 
        login_data = request.form.to_dict()
        error = handle_validate_data(LoginSchema, login_data, 'auth.login')

        if error:
            flash(error)
            return redirect(url_for('auth.login'))

        user = client.db.users.find_one({'username': login_data['username']})
        if user and check_password_hash(user['password'], login_data['password']):
            remember = login_data.get('remember', False)
            login_user(User(user['_id']), remember=remember)
            return redirect(url_for('main.dashboard'))
        
    elif request.method == 'GET':
        return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout.
    """
    logout_user()
    return redirect(url_for('auth.login'))