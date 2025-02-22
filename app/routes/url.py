from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import current_user
bp = Blueprint('url', __name__)

from db import client, ReturnDocument
from datetime import datetime, timezone
from ..models import UrlSchema, ValidationError
from ..utils import Base62

def get_next_id():
    if 'counter' not in client.db.list_collection_names():
        client.db.counter.insert_one({"_id": "url_id", "seq": 0})
   
    counter = client.db.counter.find_one_and_update({"_id": "url_id"}, {"$inc": {"seq": 1}}, return_document=ReturnDocument.AFTER)
    
    return counter["seq"] if counter else 1

@bp.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.form.to_dict()
  
    if current_user.is_authenticated: 
        user_id = getattr(current_user, "id", None)
        data['user_id'] = user_id
    
    
    try: 
        valid_data = UrlSchema().load(data)
    except ValidationError as err: 
        flash(err.messages)
        return redirect(url_for('main.index'))
    
    url_id = get_next_id()

    client.db.urls.insert_one({
        "user_id": valid_data.get('user_id'),
        "url": valid_data.get('url'),
        "shorted_code": Base62().encode(url_id),
        "expire_date": valid_data.get('expire_date'),
        "created_at": valid_data.get('created_at'),
        "click_count": valid_data.get('click_count'),
        "last_clicked_at": valid_data.get('last_clicked_at')
    })

    return redirect(url_for('main.index', shorted_url=Base62().encode(url_id))) 
    

@bp.route('/<shorted_code>', methods=['GET'])
def redirect_url(shorted_code):
    url = client.db.urls.find_one({"shorted_code": shorted_code})

    if not url:
        flash("URL not found")
        return redirect(url_for('main.index')) 
    
    client.db.urls.update_one({"shorted_code": shorted_code}, {"$inc": {"click_count": 1}, "$set": {"last_clicked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}})

    return redirect(url["url"])