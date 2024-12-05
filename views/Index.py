# views/Index.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User


index = Blueprint('index', __name__, template_folder='templates/login', static_folder='static')

@index.route('/')
def main():
    return render_template('login/login.html')


@index.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        user = User.query.filter_by(username=username).first()
        # check password hash
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username
            session['superuser'] = user.superuser
            return redirect(url_for('servers.index'))
        else:
            flash('Invalid credentials')
            return render_template('login/login.html')

    return render_template('login/login.html')


@index.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = None
    session['superuser'] = False
    session.clear()
    return redirect(url_for('index.main'))