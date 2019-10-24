from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blogpost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    post = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blogpost', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/all')
def home():
    users = User.query.all()
    return render_template('home.html', users=users)


@app.route('/newpost')
def newpost():
    return render_template('newpost.html')


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'all']
    print(session)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(
            username=username).first()
        users_password = User.query.filter_by(
            password=password).first()
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        if not users_password:
            return render_template('login.html', password_error="Your username or password was incorrect.")
        if not username_error and not password_error:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')

    return render_template('login.html')


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ""
        password_error = ""
        verify_error = ""

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:

            # this is for the username error
            if not 20 >= len(username) >= 3 or " " in username:
                username_error = "Please enter a username between 3-20 characters. Make sure it doens't include any spaces!"

        # this is for the password error
            if not 20 >= len(password) >= 3 or " " in password:
                password_error = "Please enter a password between 3-20 characters. Make sure it doesn't include any spaces!"

        # this if for the password verify error
            if verify != password:
                verify_error = "Passwords need to match!"

        # this is for all the errors together
            if not username_error and not password_error and not verify_error:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost?username='+str(username))
            else:
                return render_template('signup.html', username=username, username_error=username_error, password=password, password_error=password_error, verify_error=verify_error)
    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/index')
def index():
    user_id = request.args.get('userid')
    if user_id:
        owner = User.query.filter_by(id=user_id).first()
        posts = Blogpost.query.filter_by(owner=owner)
        return render_template('index.html', posts=posts)
    else:
        posts = Blogpost.query.all()
        return render_template('index.html', posts=posts)


@app.route('/detail')
def detail():
    post_id = request.args.get('id')
    mypost = Blogpost.query.get(post_id)
    return render_template('post.html', post=mypost)


@app.route('/add-post', methods=['POST'])
def addpost():
    if request.method == "POST":
        title = request.form['title']
        post = request.form['post']
        title_error = ''
        post_error = ''

        if not title:
            title_error = "Please enter a title."
        if not post:
            post_error = "Please enter some text."
        if not title_error and not post_error:
            owner = User.query.filter_by(username=session['username']).first()
            newpost = Blogpost(title, post, owner)
            db.session.add(newpost)
            db.session.commit()
            return redirect('/index')
        else:
            return render_template('newpost.html', title_error=title_error, post_error=post_error)


    # it only runs when we run main.py directly
if __name__ == '__main__':
    app.run()
    # app.run(debug=True)
