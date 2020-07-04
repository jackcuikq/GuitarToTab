import os
import secrets
from PIL import Image
from guitartotab.models import User, Tab
from flask import render_template, url_for, flash, redirect, request, abort
from guitartotab import app, db, bcrypt
from guitartotab.forms import RegistrationForm, LoginForm, UpdateAccountForm, TabForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    tabs = Tab.query.all()
    return render_template('home.html', title='Home', tabs=tabs)


@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()    
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account info has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/tab/new', methods=['GET', 'POST'])
@login_required
def new_tabs():
    form = TabForm()
    if form.validate_on_submit():
        tab = Tab(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(tab)
        db.session.commit()
        return redirect(url_for('home'))
        
    return render_template('create_tab.html', title='New Tab', form=form, legend='New Tab')


@app.route('/tab/<int:tab_id>')
def tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)
    return render_template('tab.html', title=tab.title, tab=tab)


@app.route('/tab/<int:tab_id>/update', methods=['GET', 'POST'])
@login_required
def update_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)

    form = TabForm()
    if form.validate_on_submit():
        tab.title = form.title.data
        tab.content = form.content.data
        db.session.commit()
        flash('Your tab has been updated!', 'success')
        return redirect(url_for('tab', tab_id=tab.id))

    elif request.method == 'GET':
        form.title.data = tab.title
        form.content.data = tab.content

    return render_template('create_tab.html', title='Update Tab', form=form, legend='Update Tab')


@app.route('/tab/<int:tab_id>/delete', methods=['POST'])
@login_required
def delete_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)

    db.session.delete(tab)
    db.session.commit()
    flash('Your tab has been deleted!', 'success')
    return redirect(url_for('home'))
