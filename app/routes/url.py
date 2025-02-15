from flask import Blueprint

bp = Blueprint('url', __name__)

@bp.route('/shorten', methods=['POST'])
def shorten_url():
    # Logic to shorten the URL
    pass

@bp.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    # Logic to redirect to the original URL
    pass