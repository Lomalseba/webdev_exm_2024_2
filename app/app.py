from flask import Flask, render_template, request, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flaskext.markdown import Markdown

app = Flask(__name__)
application = app
# Markdown(app)

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from books import bp as books_bp

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)


init_login_manager(app)

from models import Book, Cover


@app.route('/')
def index():
        books = Book.query.all()
        return render_template('index.html', books=books)


@app.route('/covers/<cover_id>')
def cover(cover_id):
    img = db.get_or_404(Cover, cover_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], img.storage_filename)

