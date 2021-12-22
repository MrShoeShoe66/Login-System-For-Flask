# Imports

from flask import Flask,render_template,request,redirect
from flask_login import login_required, current_user, login_user, logout_user, UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Main App Setup

app = Flask(__name__)
app.secret_key = 'cange this if you want this to be sucure'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Login + Database

login = LoginManager()
db = SQLAlchemy()

# User class, For Creating Users

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
# User Loader For Login

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

# Login and Database prep

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

# Database Setup

@app.before_first_request
def create_all():
    db.create_all()

# Defalt 'home' page

@app.route('/')
def home():
    return render_template('home.html')

# 'Blog' or Dashboard

@app.route('/blogs')
@login_required
def blog():
    return render_template('blog.html')
 
# Login User

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/blogs')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/blogs')
     
    return render_template('login.html')

# Register User

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/blogs')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# Logout User
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/blogs')

# Runing The App

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=80)