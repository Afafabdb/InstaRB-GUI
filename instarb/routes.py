import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request
from instarb.models import User, UserLogs, UserInstagramAccounts, UserToolSettings 
from instarb.forms import RegistrationForm, LoginForm, UpdateAccountForm, AccountUsers,\
                             UpdateInstagramAccountForm,AutoLikerForm, SettingsForm
from instarb import app, db, bcrypt, cipher_suite
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_, desc
from instarb.instabot import run_instarb_auto_liker

@app.route('/index')
def home_page():
    return render_template('home_page.html', title='Home')

@app.route('/')
@app.route('/auto_liker', methods=['GET','POST'])
@login_required
def auto_liker():
    form = AutoLikerForm()
    form.insta_account.choices = [(user.id, user.insta_name)for user in UserInstagramAccounts.query.filter_by(user_id=current_user.id).all()]
    if form.insta_account.choices == []:
        flash('Please add Instagram accounts to run Auto Liker','warning')
    if form.validate_on_submit():
        task = 'AutoLiker'
        content = form.list_of_urls.data
        user_id = current_user.id
        insta_account_id = form.insta_account.data

        status = run_instarb_auto_liker(user_id, insta_account_id, content)
        log = UserLogs(title=form.title.data, task=task, content=content, insta_account=form.insta_account.data, status=status, user_id=current_user.id)


        db.session.add(log)
        db.session.commit()
        flash('Added AutoLiker task. Please check logs for more information','success')
        return redirect(url_for('auto_liker'))
        
    return render_template('auto_liker.html', title='Auto Liker', form=form)





@app.route('/acc_settings', methods=['GET','POST'])
@login_required
def acc_settings():
    tool_settings = UserToolSettings.query.filter_by(user_id = current_user.id).first()
    form = SettingsForm()
    if request.method == 'POST':
    # if form.validate_on_submit():
        tool_settings.live_browser = form.live_browser.data
        tool_settings.do_like = form.do_like.data
        tool_settings.like_randomize = form.like_randomize.data
        tool_settings.like_percentage = form.like_percentage.data
        db.session.commit()
        flash('Tool settings updated successfully','success')
        return redirect('acc_settings')

    elif request.method == 'GET':
        form.live_browser.data = tool_settings.live_browser
        form.do_like.data = tool_settings.do_like
        form.like_randomize.data = tool_settings.like_randomize
        form.like_percentage.data = tool_settings.like_percentage
    
    return render_template('acc_settings.html', title='Settings', form=form)

def save_picture(form_picture, current_img_file=None):
    random_hex = secrets.token_hex(16)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics/'+picture_filename)
    # resize by aspect ration
    image = Image.open(form_picture)
    width  = image.size[0]
    height = image.size[1]

    if width > height:
        difference = width - height
        offset     = difference / 2
        resize     = (offset, 0, width - offset, height)
    else:
        difference = height - width
        offset     = difference / 2
        resize     = (0, offset, width, height - offset)

    thumb = image.crop(resize).resize((200, 200), Image.ANTIALIAS)
    thumb.save(picture_path)
    # end of resize by aspect ration
    if current_img_file != 'default_profile_pic.jpg' and current_img_file != None:
        current_image = os.path.join(app.root_path, 'static/profile_pics/'+current_img_file)
        os.remove(current_image)
    return picture_filename


@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_file = save_picture(form.picture.data, current_user.image_file)
            current_user.image_file = image_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)

    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auto_liker'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Login successful','success')
            return redirect(next_page) if next_page else redirect(url_for('auto_liker'))
        else:
            flash(f'Login unsuccessful. Please check Email and Password','danger')
    return render_template('login.html', title='Login',form=form)


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auto_liker'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        user=User.query.filter_by(username=form.username.data).first()
        user_settings = UserToolSettings(user_id=user.id)
        db.session.add(user_settings)
        db.session.commit()
        flash(f'Account created for { form.username.data }!. Please login to continue','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def instagram_password_encryption(form_password):
    encoded_password = cipher_suite.encrypt(bytes(form_password, encoding='utf-8'))
    return encoded_password


@app.route('/acc_users')
@login_required
def acc_users():
    insta_users = UserInstagramAccounts.query.filter_by(user_id=current_user.id).all()
    return render_template('acc_users.html', title='Instagram Accounts', insta_users=insta_users)


@app.route('/acc_users/newuser', methods=['GET','POST'])
@login_required
def new_user():
    form = AccountUsers()
    if form.validate_on_submit():
        if form.profile_pic.data:
            profile_pic = save_picture(form.profile_pic.data)
        else:
            profile_pic = 'default_insta_pic.jpg'
        encoded_password = instagram_password_encryption(form.password.data)
        insta = UserInstagramAccounts(insta_name=form.name.data, insta_username=form.username.data,
                                        insta_password=encoded_password, insta_profile_pic= profile_pic, user_id=current_user.id)
        db.session.add(insta)
        db.session.commit()
        flash('Instagram account added successfully','success')       
        return redirect(url_for('acc_users')) 
    return render_template('create_user.html',title='Add Instagram User Accoount',form=form)


@app.route('/acc_users/<int:insta_id>/edit', methods=['GET','POST'])
@login_required
def edit_user(insta_id):
    form = UpdateInstagramAccountForm()
    insta_details = UserInstagramAccounts.query.get_or_404(insta_id)
    if insta_details.userinstaaccounts != current_user:
        abort(403)
    if form.validate_on_submit():
        insta_details.insta_username = form.username.data
        insta_details.insta_password = instagram_password_encryption(form.password.data)
        if form.profile_pic.data:
            insta_details.insta_profile_pic = save_picture(form.profile_pic.data)
        db.session.commit()
        flash(f'{insta_details.insta_name} Instagram account updated successfully','success')
        
    return render_template('edit_insta_user.html', insta_details=insta_details, title='Edit Instagram Account', form=form)
    

@app.route('/acc_users/<int:insta_id>/delete', methods=['POST'])
@login_required
def delete_user(insta_id):
    insta_details = UserInstagramAccounts.query.get_or_404(insta_id)
    
    if insta_details.userinstaaccounts != current_user:
        abort(403) 
    
    user_logs = UserLogs.query.filter_by(insta_account=insta_id).first()
    if user_logs:
        flash('Account cannot be deleted when there is logs associated with this account','warning')
    else:
        db.session.delete(insta_details)
        db.session.commit()
        flash('Instagram account deleted successfully','success')
    return redirect(url_for('acc_users'))

@app.route('/acc_logs')
@login_required
def acc_logs():
    # user_logs=db.session.query(UserLogs, UserInstagramAccounts).filter(and_(UserLogs.user_id==current_user.id, UserLogs.user_id==UserInstagramAccounts.user_id))
    user_logs=UserLogs.query.filter_by(user_id=current_user.id).order_by(UserLogs.date_run.desc())
    return render_template('acc_logs.html',user_logs=user_logs, title='Logs')


@app.route('/acc_logs/<int:log_id>')
@login_required
def user_run_log(log_id):
    user_log = UserLogs.query.get_or_404(log_id)
    return render_template('user_run_log.html', title=user_log.title, user_log=user_log)


@app.route('/acc_logs/<int:insta_id>/insta_user')
@login_required
def insta_user_run_log(insta_id):
    insta_user_logs = UserLogs.query.filter_by(insta_account= insta_id).order_by(UserLogs.date_run.desc())

    return render_template('insta_user_run_log.html', title=f'Logs from {insta_user_logs[0].userinstaaccount.insta_username}', insta_user_logs=insta_user_logs)