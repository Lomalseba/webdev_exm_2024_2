from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user, logout_user, login_manager
from app import app
from .models import User

@app.route('/')
def index():
    return render_template('index.html')
