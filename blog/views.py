from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Post, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from .app import db, app
from flask_login import login_user, login_required, logout_user, current_user
import psycopg2
import psycopg2.extras
from flask_socketio import SocketIO, send
from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm


flask_change_password = ChangePassword(min_password_length=10, rules=dict(long_password_override=2))
flask_change_password.init_app(app)
socketio = SocketIO(app, cors_allowed_origins='*')
views = Blueprint('views', __name__)
conn = psycopg2.connect(dbname="database", user="postgres", password="Classname4444", host="localhost")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@views.route('/')
@login_required
def home():
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    return render_template("home.html", user=current_user, posts=posts)


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))


@views.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)


@views.route('/reset_password', methods=['GET', 'POST'])
@login_required
def page_change_password():
    title = 'Reset Password'
    first_name = request.form.get('firstName')
    form = ChangePasswordForm(username=first_name, changing=True, title=title)
    if form.validate_on_submit():
        valid = flask_change_password.verify_password_change_form(form)
        if valid:
            flash('Password changed!', category='success')
            return redirect(url_for('views.home', title='changed', new_password=form.password.data))
        else:
            flash('Password not changed!', category='error')
            return redirect(url_for('page_change_password'))
    password_template = flask_change_password.change_password_template(form, submit_text='Change')
    return render_template('reset_password.html', password_template=password_template, title=title, form=form, user=current_user)


@views.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        title = request.form.get('title')
        data = request.form.get('data')

        new_post = Post(title=title, data=data)
        db.session.add(new_post)
        db.session.commit()
        flash('Post published!', category='success')
        return redirect(url_for('views.home'))
    return render_template("post.html", user=current_user, posts=post)


@views.route('/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post_detail = Post.query.filter_by(id=post_id).one()
    if request.method == 'POST':
        data = request.form.get('data')

        new_comment = Comment(data=data)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added", category='success')
    cursor.execute("SELECT * FROM comment")
    comment = cursor.fetchall()
    return render_template("post_detail.html", post=post_detail, user=current_user, comments=comment)


@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)


@views.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    return render_template("chat.html", user=current_user)

