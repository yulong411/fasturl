from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Handle user dashboard: display user's username, show collection of urls & analytics
    """
    from db import client 
    from bson import ObjectId
    username = client.db.users.find_one({'_id': ObjectId(current_user.id)})['username']

    return render_template('dashboard.html', username=username)