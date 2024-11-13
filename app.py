from __future__ import annotations
import os
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

# local imports
from hashing_examples import UpdatedHasher
from loginforms import RegisterForm, LoginForm

# =================================================================================
# Identify necessary files
# =================================================================================

scriptdir = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(scriptdir, "todo.sqlite3")
pepperfile = os.path.join(scriptdir, "pepper.bin")

# =================================================================================
# Set up hasher
# =================================================================================

# open and read the contents of the pepper file into your pepper key
# NOTE: you should really generate your own and not use the one from the starter
with open(pepperfile, "rb") as fin:
    pepper_key = fin.read()

# generate our own pepper and write it to the file if the file was empty
if not pepper_key:
    pepper_key = UpdatedHasher.random_pepper()
    with open(pepperfile, "wb") as fout:
        fout.write(pepper_key)

# create a new instance of UpdatedHasher using that pepper key
pwd_hasher = UpdatedHasher(pepper_key)

# =================================================================================
# Configure the Flask Application
# =================================================================================

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["SECRET_KEY"] = "droporangemineorate"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbfile}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Prepare and connect the LoginManager to this app
login_manager = LoginManager()
login_manager.init_app(app)
# function name of the route that has the login form (so it can redirect users)
login_manager.login_view = "get_login"  # type: ignore
login_manager.session_protection = "strong"


# function that takes a user id and returns that user from the database
@login_manager.user_loader
def load_user(uid: int) -> User | None:
    return User.query.get(int(uid))


# =================================================================================
# Database Setup
# =================================================================================

# Getting the database object handle from the app
db = SQLAlchemy(app)


# Create database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary)  # hash is a binary attribute

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("password is a write-only attribute")

    @password.setter
    def password(self, pwd: str) -> None:
        self.password_hash = pwd_hasher.hash(pwd)

    # add a verify_password convenience method
    def verify_password(self, pwd: str) -> bool:
        return pwd_hasher.check(pwd, self.password_hash)


# remember that all database operations must occur within an app context
# we'll want to get rid of drop_all() + create_all() in the future
with app.app_context():
    db.drop_all()
    db.create_all()  # this is only needed if the database doesn't already exist

# =================================================================================
# Route Handlers
# =================================================================================


@app.get("/register/")
def get_register():
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.post("/register/")
def post_register():
    form = RegisterForm()
    if form.validate():
        # check if there is already a user with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if the email address is free, create a new user and send to login
        if user is None:
            user = User(
                name=form.name.data, email=form.email.data, password=form.password.data
            )  # type:ignore
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("get_login"))
        else:
            # if the user already exists
            # flash a warning message and redirect to get registration form
            flash("There is already an account with that email address")
            return redirect(url_for("get_register"))
    else:
        # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("get_register"))


@app.get("/login/")
def get_login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.post("/login/")
def post_login():
    form = LoginForm()
    if form.validate():
        # try to get the user associated with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if this user exists and the password matches
        if user is not None and user.verify_password(form.password.data):
            # log this user in through the login_manager
            login_user(user)
            # redirect the user to the page they wanted or the home page
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("index")
            return redirect(next)
        else:
            # if the user does not exist or the password is incorrect
            # flash an error message and redirect to login form
            flash("Invalid email address or password")
            return redirect(url_for("get_login"))
    else:
        # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("get_login"))


@app.get("/")
def index():
    return render_template("index.html", current_user=current_user)


@app.get("/logout/")
@login_required
def get_logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("index"))
