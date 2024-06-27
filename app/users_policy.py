from flask_login import current_user
from app import app

class UsersPolicy:
    def __init__(self, record):
        self.record = record

    def book_delete(self):
        return current_user.is_administrator

    def book_create(self):
        return current_user.is_administrator

    def book_edit(self):
        return current_user.is_moderator or current_user.is_administrator