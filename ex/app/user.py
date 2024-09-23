from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import current_user, login_required

from app import app, db
from query import queries
from .auth import checkRole

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/reviews/', methods=['GET', 'POST'])
def user_reviews():
    all_user_reviews = {}
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = queries["SELECT_ALL_USER_REVIEWS"]
            print(current_user.id)
            cursor.execute(query, (current_user.id, ))
            all_user_reviews = cursor.fetchall()
            print(all_user_reviews)
    except:
        db.connect().rollback()
        print("ошибка в получении всех отзывов")
    return render_template("user_reviews.html", all_user_reviews=all_user_reviews)

