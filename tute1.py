from flask import Flask, render_template,request ,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from werkzeug import secure_filename
import  json
import math
import os
# send mail function

with open("config.json","r") as p:
    parm = json.load(p)["parm"]
local_server = True

app = Flask(__name__)
app.secret_key = 'super-secreat-key'
app.config["Upload_folder"] = parm["file_location"]
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = parm["local_uri"] # ye ek tala type h is me hm apne data base ki entry krne pdte h
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = parm["prod_uri"]
db = SQLAlchemy(app)
app.config.update(dict(MAIL_SERVER = "smtp.gmail.com",
                  MAIL_PORT = '465',
                  MAIL_USE_SSL = True,
                  MAIL_USER = parm['gmail_user'],
                  MAIL_PAS = parm['gmail_pas']))
mail = Mail(app)

class Conteact(db.Model): # ye ek class ye data base ko define kre ge

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)



class Post(db.Model):  # ye ek class ye data base ko define kre ge

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    tegline = db.Column(db.String(120), nullable=False)
    contant= db.Column(db.String(5000), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=False)

# @app.route("/")
# def home():
#     return "Hlo i "

@app.route("/")
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts)/int(parm["no_of_post"]))
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(parm['no_of_post']):(page-1)*int(parm["no_of_post"])+int(parm["no_of_post"])]
    if (page==1):
        next = "/?page="+str(page+1)
        prve = "#"
    elif (page==last):
        next = "#"
        prve = "/?page=" + str(page - 1)
    else:
        next = "/?page=" + str(page +1)
        prve = "/?page=" + str(page -1)

    return render_template("index.html",parm = parm,posts = posts, next = next,prve =  prve)

# @app.route("/index.html")
# def index():
#     return render_template("index.html" ,parm = parm)




@app.route("/about")
def about():
    return render_template("about.html" ,parm = parm)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/deshboard")

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == parm['user_id']):
        post = Post.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/deshboard")



@app.route("/deshboard", methods = ['GET','POST'])
def login():
    if ('user'in session and session['user']==parm['user_id']):
        posts= Post.query.all()
        return render_template("deshboard.html",parm = parm , posts = posts)
    if request.method=="POST":
         username = request.form.get("uname")
         userpass = request.form.get("upass")
         if username ==parm['user_id'] and userpass ==parm['password']:
             session['user']= username
             posts=Post.query.all()
             return render_template("deshboard.html" ,parm = parm, posts = posts)



    return render_template("login.html" ,parm = parm)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == parm['user_id']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tegline = request.form.get('tegline')
            slug  = request.form.get('slug')
            contant = request.form.get('contant')
            img_file  = request.form.get('img_file')
            date = datetime.now()

            if sno=='O':
                post = Post(title = box_title, tegline =tegline , slug = slug, contant = contant, img_file = img_file, date = date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno = sno).first()
                post.title = box_title
                post.tegline = tegline
                post.slug  = slug
                post.contant = contant
                post.img_file = img_file
                post.date = date
                db.session.add(post)
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Post.query.filter_by(sno=sno).first()
        return render_template("edit.html", parm = parm, post = post,sno = sno )

@app.route("/contact", methods = ['GET', 'POST'])
def contect():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Conteact(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[parm['gmail_user']],
                          body=message + "\n" + phone)
    return render_template('contect.html',parm = parm)



@app.route("/uploader",methods = ['POST','GET'])
def uploader():
    if ('user' in session and session['user'] == parm['user_id']):
        if request.method =="POST":
            f = request.files['file1']
            f.save(os.path.join(app.config["Upload_folder"],secure_filename(f.filename)))
            return "Uploaded  successfully"




@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parm=parm, post=post )

app.run(debug=True)
