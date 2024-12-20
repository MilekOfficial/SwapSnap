from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
import logging

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long"),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@auth_bp.route('/auth')
def auth():
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template('auth.html', login_form=login_form, register_form=register_form)

@auth_bp.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Add your user validation logic here
        user = User(form.username.data)
        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('index'))
    flash('Invalid username or password.', 'error')
    return redirect(url_for('auth.auth'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
