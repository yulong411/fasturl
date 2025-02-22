from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from db import client 
from bson import ObjectId

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Handle user dashboard: display user's username, show collection of urls & analytics
    """
    username = client.db.users.find_one({'_id': ObjectId(current_user.id)})['username']
    url_data = client.db.urls.find({'user_id': current_user.id})

    return render_template('dashboard.html', username=username, url_data=url_data)

@bp.route('/')
def index():
    shorted_url = request.args.get('shorted_url')
    return render_template('index.html', shorted_url=shorted_url)