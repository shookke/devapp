import os
import time
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_security.utils import hash_password
from flask_admin import helpers as admin_helpers
from app import app, db, user_datastore, security, admin
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ContainerForm, EditContainerForm, UploadForm
from app.models import User, Container
from app.job import build_job
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    containers = Container.query.all()
    return render_template('index.html', title='Home', containers=containers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('manager'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('manager')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('manager'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.token = form.token.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.token.data = current_user.token
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/manager',  methods=['GET', 'POST'])
@login_required
def manager():
    containers = Container.query.all()
    return render_template('manager.html', title='Manager', containers=containers)

@app.route('/container/<container>')
@login_required
def container(container):
    container = Container.query.get(int(container))
    return render_template('container.html', title='Container', container=container)


@app.route('/manager/container/<container>', methods=['GET', 'POST'])
@login_required
def edit_container(container):
    container = Container.query.get(int(container))
    form = EditContainerForm(container.name)
    if form.validate_on_submit():
        container.name = form.name.data
        container.url = form.url.data
        container.status = form.status.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('manager'))
    elif request.method == 'GET':
        form.name.data = container.name
        form.url.data = container.url
    return render_template('edit_container.html', title='Edit Container',
                           form=form, container=container.id)

@app.route('/manager/container/remove/<container>', methods=['POST'])
@login_required
def remove_container(container):
    timeout = 3
    container = Container.query.get(int(container))
    if container is not None:
        while timeout != 0:
            container = Container.query.get(container.id)
            if container.status == None:
                db.session.delete(container)
                db.session.commit()
                return jsonify({'status': 'Container successfully removed.'})
            if container.status == 'ERROR':
                return jsonify({'status': 'Error'})
            if container.status == 'DOWN':
                db.session.delete(container)
                db.session.commit()
                return jsonify({'status': 'Container successfully removed.'})
            if container.status == 'SUCCESS':
                build_job('down-container', container.id)
                continue
            time.sleep(5)
            timeout -= 1
        return jsonify({'status': 'No such container exists.'})

@app.route('/manager/<job>/<container>',  methods=['POST'])
@login_required
def build_container(job, container):
    return build_job(job, container)

@app.route('/new_container', methods=['GET', 'POST'])
def new_container():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ContainerForm()
    if form.validate_on_submit():
        container = Container(name=form.name.data,
                              database=form.database.data,
                              db_user=form.db_user.data,
                              db_pw=form.db_pw.data,
                              prefix=form.prefix.data,
                              url=form.url.data)
        db.session.add(container)
        db.session.commit()
        flash('Container Created')
        return redirect(url_for('manager'))
    return render_template('new_container.html', title='New Container', form=form)

@app.route('/db_upload/<directory>', methods=['GET', 'POST'])
@login_required
def db_upload(directory):
    form = UploadForm()
    if form.validate_on_submit():
        sql_data = request.FILES[form.sql.name].read()
        open(os.path.join(UPLOAD_PATH, directory, form.sql.data), 'w').write(sql_data)
        flash('File has been imported')
        return redirect(url_for('manager'))
    return render_template('db_upload.html', title='Upload', form=form)

@app.route('/db_backup/<container>', methods=['POST'])
@login_required
def db_backup(container):
    return build_job('db-backup', container)

@app.route('/hosts')
def hosts():
    response = {'Add': [], 'Remove': []}
    hosts = Container.query.filter_by(status='SUCCESS')
    remove = Container.query.filter_by(status='DOWN')
    for host in hosts:
        response['Add'].append({'Address': app.config['HOST_ADDRESS'], 'URL': host.url, 'Name': host.url[:-4]})
    for item in remove:
        response['Remove'].append({ 'URL': item.url })
    return jsonify(response)