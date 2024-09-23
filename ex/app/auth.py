from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from functools import wraps

from app import app, db
from .models import User
from query import queries

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manage(app):
    login_manager = LoginManager()

    login_manager.init_app(app)

    login_manager.login_view = 'index'
    login_manager.login_message = 'Доступ к данной странице есть только у авторизованных пользователей'
    login_manager.login_message_category = 'warning'

    login_manager.user_loader(load_user)


def load_user(user_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = 'SELECT * FROM Users WHERE UserID=%s'
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()
            print(user_data)
            if user_data:
                return User(user_data.UserID, user_data.Login, user_data.RoleID)
    except:
        db.connect().rollback()
        print("ошибка при загрузки пользователя")
    return None


def checkRole(action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            user = None
            print(user_id)
            if user_id:
                user = load_user(user_id)
            if current_user.can(action,record=user):
                return f(*args, **kwargs)
            flash("У вас недостаточно прав для выполнения данного действия", "danger")
            return redirect(url_for("index"))
        return wrapper
    return decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    user_data = {}
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        remember = request.form.get("remember")

        user_data['login'] = login
        user_data['password'] = password
        user_data['remember'] = remember
        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                query = 'SELECT * FROM Users WHERE Login=%s AND PasswordHash=SHA2(%s,256)'
                print("я тут")
                cursor.execute(query, (login, password))
                print("я тут")
                user_data = cursor.fetchone()
                print("я тут")
                print(user_data)
                if user_data:
                    print("вот данные", user_data)
                    user = User(user_data.UserID, user_data.Login, user_data.RoleID)
                    print("я тут")
                    login_user(user, remember=remember)
                    print("я тут")
                    flash('Вы успешно прошли аутентификацию', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Неверные логин или пароль', 'danger')
        except:
            db.connect().rollback()
            print("ошибка при авторизации")

    return render_template('login.html', user=user_data)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))