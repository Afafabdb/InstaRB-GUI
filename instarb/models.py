from instarb import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(30), nullable=False, default='default_profile_pic.jpg')
    password = db.Column(db.String(60), nullable=False)
    userlogs = db.relationship('UserLogs', backref='userrun', lazy=True)
    userinstagramaccounts = db.relationship('UserInstagramAccounts',backref='userinstaaccounts', lazy=True)
    toolsettings = db.relationship('UserToolSettings', backref='usertoolsettings', lazy = True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class UserInstagramAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    insta_name = db.Column(db.String(30),nullable=False)
    insta_username = db.Column(db.String(30), nullable=False)
    insta_password = db.Column(db.String(50), nullable=False)
    insta_profile_pic = db.Column(db.String(30), nullable=False, default='default_insta_pic.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    insta_details = db.relationship('UserLogs', backref='userinstaaccount',lazy=True)

    def __repr__(self):
        return f"User('{self.insta_name}','{self.insta_username}','{self.insta_password}','{self.insta_profile_pic}','{self.user_id}')"



class UserLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    task = db.Column(db.String(20), nullable=False)
    date_run = db.Column(db.DateTime(20), nullable=False, default=datetime.utcnow)
    content = db.Column(db.String(2000), nullable=False)
    status = db.Column(db.String(10),nullable=False)
    insta_account = db.Column(db.Integer, db.ForeignKey('user_instagram_accounts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __repr__(self):
        return f"User('{self.title}','{self.task}','{self.status}','{self.date_run}','{self.insta_account}','{self.content}')"




class UserToolSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    live_browser = db.Column(db.String(6), nullable=False, default='True')
    do_like = db.Column(db.String(6), nullable=False, default='True')
    like_randomize = db.Column(db.String(6), nullable=False, default='True')
    like_percentage = db.Column(db.Integer, nullable=False, default=100)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User(Live: '{self.live_browser}','Like: {self.do_like}','Randomize: {self.like_randomize}','Percentage: {self.like_percentage}','User: {self.user_id}')"
