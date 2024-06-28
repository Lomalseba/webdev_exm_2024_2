import os

SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'sqlite:///local_database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

USER_ROLE = 1
MODERATOR_ROLE = 2
ADMINISTRATOR_ROLE = 3


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

