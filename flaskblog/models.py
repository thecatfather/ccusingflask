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
    liked = db.relationship('PostLike',foreign_keys='PostLike.user_id',backref='user', lazy='dynamic')
    #def __repr__(self):
    #   return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')

class Category(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False,primary_key=True)
    num_acts = db.Column(db.Integer, nullable=True)
    posts = db.relationship('Post', backref='cat', lazy=True)
    def __init__(self, name):
        self.name = name

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('name',)

    #def __repr__(self):
    #   return f"Category('{self.name}', '{self.num_acts}')"

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_name = db.Column(db.Integer, db.ForeignKey('category.name'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    upvotes = db.relationship('PostLike', backref='post', lazy='dynamic')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}','{self.content}','{self.image_file}')"

    def __init__(self,id,content,user_id, cat_name):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.cat_name = cat_name
        

class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'content', 'user_id', 'cat_name',)

