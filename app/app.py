from flask import Flask, render_template, request, send_from_directory, flash
from sqlalchemy import MetaData, func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from math import ceil
# from flaskext.markdown import Markdown

app = Flask(__name__)
application = app
# Markdown(app)

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
# from books import bp as books_bp
# from reviews import bp as reviews_bp

app.register_blueprint(auth_bp)
# app.register_blueprint(books_bp)
# app.register_blueprint(reviews_bp)

init_login_manager(app)

# from models import Book, Cover


@app.route('/')
def index():
    try:
        # current_page = request.args.get('page', 1, type=int)
        # books_offset = app.config['BOOKS_ON_INDEX_PAGE'] * (current_page - 1)

        # books = db.session.execute(
        #     db.select(Book).order_by(Book.year.desc()).limit(app.config['BOOKS_ON_INDEX_PAGE']).offset(
        #         books_offset)).scalars()
        #
        # book_count = db.session.query(func.count(Book.id)).scalar()
        # pages = ceil(book_count / app.config['BOOKS_ON_INDEX_PAGE'])
        #
        # if pages == 0:
        #     pages = 1

        return render_template(
            'index.html'
            # books=books,
            # page=current_page,
            # page_count=pages
        )
    except:
        flash("Ошибка при загрузке", 'danger')
        return render_template(
            'index.html',
            books=[],
            page=1,
            pages=1
        )


# @app.route('/covers/<cover_id>')
# def cover(cover_id):
#     img = db.get_or_404(Cover, cover_id)
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                img.storage_filename)