from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog import ma


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    #image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    #def __repr__(self):
    #   return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    num_acts = db.Column(db.Integer, nullable=True)
    posts = db.relationship('Post', backref='cat', lazy=True)
    def __init__(self, name):
        self.name = name

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('name',)

    #def __repr__(self):
    #   return f"Category('{self.name}', '{self.num_acts}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    upvotes = db.Column(db.Integer)
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}','{self.content}','{self.image_file}')"


