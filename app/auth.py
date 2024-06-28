from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from app import db as db
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Необходимо выполнить вход'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    return user

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        remember_me = request.form.get("remember_me")
        if login and password:
            user = User.query.filter_by(login=login).first()
            if user and user.check_password(password):
                login_user(user, remember=remember_me)
                flash("успешно", "success")
                next = request.args.get("next")
                return redirect(next or url_for("index"))
        flash("Пользователь не найден", "danger")
    return render_template("auth/login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Функция проверки прав
def check_rights(action):
    def decor(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            user = None
            if user_id:
                user = load_user(user_id)
            if not current_user.can(action, user):
                flash("У вас недостаточно прав для выполнения данного действия", "warning")
                return redirect(url_for("index"))
            return function(*args, **kwargs)
        return wrapper
    return decor