from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blogpost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    post = db.Column(db.String(5000))

    def __init__(self, title, post):
        self.title = title
        self.post = post


@app.route('/blog', methods=['POST', 'GET'])
def index():
    post_id = str(request.args.get('id'))
    mypost = Blogpost.query.get(post_id)
    posts = Blogpost.query.all()
    return render_template('index.html', posts=posts, mypost=mypost)


@app.route('/newpost')
def newpost():
    return render_template('newpost.html')


@app.route('/add-post', methods=['POST'])
def addpost():
    if request.method == "POST":
        title = request.form['title']
        post = request.form['post']
        title_error = ''
        post_error = ''

        if not title:
            title_error = "please enter a title."
        if not post:
            post_error = "please enter some text."
        if not title_error and not post_error:
            newpost = Blogpost(title=title, post=post)
            db.session.add(newpost)
            db.session.commit()
            return redirect('/blog?id={0}'.format(newpost.id))
        else:
            return render_template('newpost.html', title_error=title_error, post_error=post_error)


# todo: write the individual-post @app.route. (hint: /blog?id={} )
# @app.route('/blog?id={}', methods=['POST', 'GET'])
# def indiv_post():
#     if request.method == "POST":
#         return redirect('/blog?id={}')


# it only runs when we run main.py directly
if __name__ == '__main__':
    app.run()
    # app.run(debug=True)
