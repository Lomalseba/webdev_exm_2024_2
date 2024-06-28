import os
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import url_for
from app import db, app
from users_policy import UsersPolicy
from sqlalchemy.sql import func


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.title


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_administrator(self):
        return self.role_id == app.config['ADMINISTRATOR_ROLE']

    @property
    def is_moderator(self):
        return self.role_id == app.config['MODERATOR_ROLE']

    def can(self, action, record=None):
        users_policy = UsersPolicy(record)
        method = getattr(users_policy, action, None)
        if method:
            return method()
        return False

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    # def can_write_review(self, book_id):
    #     return db.session.query(Review).filter(Review.user_id == self.id, Review.book_id == book_id).count() == 0

    def __repr__(self):
        return '<User %r>' % self.login

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publish = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.String(200), db.ForeignKey('covers.id'), nullable=False)

    @property
    def genres(self):
        books_genres = db.session.execute(db.Select(Book_To_Genre).filter_by(book_id=self.id)).all()
        genres = []
        for book_genre in books_genres:
            genre = db.session.execute(db.select(Genre).filter_by(id=book_genre[0].genre_id)).scalar()
            genres.append(genre.title)
        return genres

    @property
    def cover(self):
        return db.session.query(Cover).filter_by(id=self.cover_id).first()

    def __repr__(self):
        return '<Book %r>' % self.title


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.title


class Book_To_Genre(db.Model):
    __tablename__ = 'books_to_genres'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)

class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.String(250), primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    MIME_type = db.Column(db.String(250), nullable=False)
    MD5_hash = db.Column(db.String(150), nullable=False)

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('cover', cover_id=self.id)

    def __repr__(self):
        return '<Cover %r>' % self.file_name