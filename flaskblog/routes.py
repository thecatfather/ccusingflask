import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort ,jsonify
from flaskblog import app, db, bcrypt, ma
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm ,CategoryForm
from flaskblog.models import User, Post, Category, UserSchema ,CategorySchema,PostSchema
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename
from sqlalchemy import select, func
from datetime import datetime


def save_picture(form_picture):
    print("hihihihi")
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn)
    print('PATH     ',os.path.join(app.root_path))

    #output_size = (125, 125)
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    cat_names = db.session.query(Category.name)
    l = cat_names.all()
    #print(l[0][0])
    l=[str(x[0]) for x in l]
    #print(l)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=post,option_list = l,current_user=current_user)


@app.route("/category/<string:cat>")
def category(cat):
    print(cat)
    print(type(cat))
    filtered = Post.query.filter(Post.cat_name == cat).order_by(Post.date_posted.desc()).all()
    #print("this is filtered",filtered[0].image_file)
    image_list=[i.image_file for i in filtered]
    content_list=[i.content for i in filtered]
    id_list=[i.id for i in filtered]
    likes_list=[i.upvotes for i in filtered]
    #print(likes_list[0])
    return render_template('category.html',current_user= current_user,image_list=image_list,content_list=content_list,category=cat, leng = len(image_list),id_list=id_list , likes_list= likes_list,post =filtered)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))




@app.route("/account", methods=['GET', 'POST'])
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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



#class UploadForm(Form):
   #file = FileField()
@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)

@app.route("/post/new_cat", methods=['GET', 'POST'])
@login_required
def new_cat():

    form = CategoryForm()
    
    if form.validate_on_submit():
        cat = Category(form.name.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('home'))


    return render_template('add_category.html',form=form ,legend='New Category')

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    #form2 = UploadForm()
    cat_names = db.session.query(Category.name)
    l = cat_names.all()
    #print(l[0][0])
    l=[str(x[0]) for x in l]
    print(l)
    form.category.choices = [ (i,i) for i in l]
    #l= Category.query.all()
    #prin
    if form.validate_on_submit():
        print("PICC ",form.picture.data)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        print(picture_file)
        post = Post( content=form.content.data, author=current_user, cat_name = form.category.data , image_file = picture_file)
        print("picture of data ", form.picture.data  )

        db.session.add(post)
        db.session.commit()


        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post', option_list = l)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

category_schema = CategorySchema(strict=True)
categories_schema = CategorySchema(many=True, strict=True)

post_schema = PostSchema(strict=True)
posts_schema = PostSchema( many=True,strict=True)

@app.route("/api/v1/users", methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']
    email = "default@default.com"
    print('user is = ' , username)
    new_user = User(username,email,password)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)



@app.route('/api/v1/users', methods=['GET'])
def get_users():
  all_users = User.query.all()
  result = users_schema.dump(all_users)
  return jsonify(result.data)

@app.route('/api/v1/users/<id>', methods=['DELETE'])
def delete_product(id):
  user = User.query.get(id)
  db.session.delete(user)
  db.session.commit()

  return user_schema.jsonify(user)

@app.route("/api/v1/categories", methods=['POST'])
def add_category():
    name = request.json
    #num_acts = request.json['num_acts']
    #email = "default@default.com"
    #print('user is = ' , username)
    new_category = Category(name[0])

    db.session.add(new_category)
    db.session.commit()

    return category_schema.jsonify(new_category)

@app.route("/api/v1/categories", methods=['GET'])
def get_categories():
    all_users = Category.query.all()
    result = categories_schema.dump(all_users)
    return jsonify(result.data)

@app.route("/api/v1/categories/<category_name>", methods=['DELETE'])
def delete_category(category_name):
    #print(category_name)
    category = Category.query.get(category_name)
    print(category)
    db.session.delete(category)
    db.session.commit()
    return category_schema.jsonify(category)  
      
@app.route("/api/v1/acts", methods=['POST'])
def upload_acts():
    id1 = request.json['actId']
    userid = request.json['userid']
    content = request.json['caption']
    cat_name = request.json['categoryName']

    post=Post(id1,content,userid,datetime.utcnow(),cat_name, 0)
    db.session.add(post)
    db.session.commit()
    return post_schema.jsonify(post)  

@app.route("/api/v1/categories/<categoryName>/acts", methods=['GET'])
def get_acts(categoryName):
    cate=db.session.query(Post).filter_by(cat_name=categoryName).all()
    return posts_schema.jsonify(cate)

@app.route("/api/v1/categories/<categoryName>/acts/size", methods=['GET'])
def get_no_of_acts(categoryName):
    c=db.session.query(Post).filter_by(cat_name=categoryName).all()
    l = len(c)
    return "[" +str(l) + "]"
@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():
    actid = request.json
    print(actid[0])
    #id = Post(actid[0])
    #print(id)
    up = Post.query.get(actid[0])
    up.n_upvotes = up.n_upvotes + 1
    db.session.commit()
    return post_schema.jsonify(up)

@app.route("/api/v1/acts/<actId>",methods=['DELETE'])
def del_act(actId):
    act = Post.query.get(actId)
    db.session.delete(act)
    db.session.commit()
    return post_schema.jsonify(act)

'''@app.route("/api/v1/categories/<categoryName>/acts?start=<startRange>&end=<endRange>",methods=['GET'])
def range_acts(categoryName,startRange,endRange):
    print("hihihihihihihihihihihihihih")
    c=db.session.query(Post).filter_by(cat_name=categoryName).all()
    print("hihihihihihihihihihihihihih",c)
    #return "1"'''







