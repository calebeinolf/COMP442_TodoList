from __future__ import annotations
import os
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

from datetime import date, time

# general use cases:
# date(year,month,day)
# time(hour,minute)

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
if os.path.exists(pepperfile):
    with open(pepperfile, "rb") as fin:
        pepper_key = fin.read()

# generate our own pepper and write it to the file if the file didn't exist
# or if the file was empty
if not os.path.exists(pepperfile) or not pepper_key:
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

# =================================================================================


# Create database models
class User(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode, nullable=False, unique=True)
    # if we don't need users' emails we shouldn't store them
    # email = db.Column(db.Unicode, nullable=False, unique=True)
    password_hash = db.Column(db.LargeBinary)  # hash is a binary attribute

    tasklists = db.relationship("TaskList", backref="user")

    tasks = db.relationship("Task", backref="user")

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

    def __init__(self, username, password):
        self.username = username
        # self.email = email
        # should call the password setter resulting in a hash for us
        self.password = password
        # don't have to specify values for vars that are assigned db.relationship


# =================================================================================

# define a join table to associate tasks with multiple lists and lists with multiple tasks
# each row will have a tasklistid and a taskid
# class TaskToList(db.Model):
# __tablename__ = "TasksToLists"
# id = db.Column(db.Integer,primary_key=True)
# tlname = db.Column(db.Unicode, db.ForeignKey("TaskLists.name"))
# taskid = db.Column(db.Integer, db.ForeignKey("Tasks.id"))

TasksToTaskLists = db.Table(
    "TasksToTaskLists",
    db.Column("tlname", db.Unicode, db.ForeignKey("TaskLists.name"), nullable=False),
    db.Column("taskid", db.Integer, db.ForeignKey("Tasks.id"), nullable=False),
)

# =================================================================================

# Actually, I don't think this function is necessary as we can restrict users from
# entering duetime without a duedate in other ways
# define a default function for duetime so that duedate must be non-null
# in order for duetime to be non-null
# def duetimedefault(context):
# force duetime to only be non-null when duedate is non-null
# if not context.get_current_parameters()["duedate"]:
# return None
# else:
# return context.get_current_parameters()["duetime"]


class Task(db.Model):
    __tablename__ = "Tasks"

    # -----------------------------------------------------
    # non-nullable attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False, unique=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    starred = db.Column(db.Boolean, nullable=False, default=False)

    # -----------------------------------------------------
    # optional attributes
    progressnotes = db.Column(db.Unicode, nullable=True)
    duedate = db.Column(db.Date, nullable=True)
    # duedate MUST have a value in order for there to be a duetime
    # enforce this through forms and the way we present options to the user ->
    # the duetime field should only become visible when a duedate has been selected
    duetime = db.Column(db.Time, nullable=True) #default=duetimedefault, onupdate=duetimedefault

    # should be a value in range [1,10] if not null
    priority = db.Column(db.Integer, nullable=True)
    generalnotes = db.Column(db.Unicode, nullable=True)
    userid = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    # now we have a list of subtasks which can refer to their task through the task var
    subtasks = db.relationship("Subtask", backref="task")
    tasklists = db.relationship(
        "TaskList", secondary=TasksToTaskLists, back_populates="tasks"
    )

    # def __init__(self,name,userid=None,complete=False,progressnotes="",duedate=None,duetime=None,priority=None,generalnotes="",user=None):
    # self.name=name
    # self.userid=userid
    # self.complete=complete
    # self.progressnotes=progressnotes
    # self.duedate=duedate
    # self.duetime=duetime
    # self.priority=priority
    # self.generalnotes=generalnotes
    # NOTE:user should never be None
    # if not user: raise ValueError("A task MUST be associated with a user")
    # self.user = user


# =================================================================================


class Subtask(db.Model):
    __tablename__ = "Subtasks"
    name = db.Column(db.Unicode, primary_key=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    taskid = db.Column(db.Integer, db.ForeignKey("Tasks.id"), nullable=False)

    # def __init__(self,name,taskid,complete=False):
    # self.name=name
    # self.taskid=taskid
    # self.complete=complete


# =================================================================================


class TaskList(db.Model):
    __tablename__ = "TaskLists"
    name = db.Column(db.Unicode, primary_key=True)
    tasks = db.relationship(
        "Task", secondary=TasksToTaskLists, back_populates="tasklists"
    )
    userid = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    def appendtask(self, task):
        self.tasks.append(task)

    # def __init__(self,name,userid=None,user=None):
    # self.name=name
    # self.userid=userid
    # if not user: raise ValueError("A TaskList must be associated with a User")


# =================================================================================

# remember that all database operations must occur within an app context
# we'll want to get rid of drop_all() + create_all() in the future
with app.app_context():
    db.drop_all()
    db.create_all()  # this is only needed if the database doesn't already exist

    nk = User("natekuhns", "swink123")
    ce = User("calebeinolf", "boink123")
    dlr = User("davidleroux", "dook1234")

    db.session.add_all((nk, ce, dlr))

    nktask1 = Task(
        name="W project checkpoint",
        complete=1,
        # User.query.filter_by(username="natekuhns").first().id,
        duedate=date(2024, 11, 15),
        duetime=time(23, 59),
        priority=1,
        user=nk,
    )
    nktask2 = Task(name="", duetime=time(23, 59), user=nk)

    nktask3 = Task(name="task3", user=nk)

    db.session.add_all((nktask1, nktask2, nktask3))

    nktst1 = Subtask(name="sub1", task=nktask3)

    db.session.add(nktst1)

    natewebtl = TaskList(name="Web", user=nk)

    db.session.add(natewebtl)

    natewebtl.appendtask(nktask1)

    db.session.commit()

# =================================================================================
# Route Handlers
# =================================================================================

# =================================================================================
# Register
@app.get("/register/")
def get_register():
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.post("/register/")
def post_register():
    form = RegisterForm()
    if form.validate():
        # check if there is already a user with this username
        user = User.query.filter_by(username=form.username.data).first()
        # if the username is free, create a new user and send to login
        if user is None:
            # user = User(
            # username=form.username.data, email=form.email.data, password=form.password.data
            # )  # type:ignore
            user = User(form.username.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("get_login"))
        else:
            # if the user already exists
            # flash a warning message and redirect to get registration form
            flash("There is already an account with that username")
            return redirect(url_for("get_register"))
    else:
        # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("get_register"))


# =================================================================================
# Log in and out
@app.get("/login/")
def get_login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.post("/login/")
def post_login():
    form = LoginForm()
    if form.validate():
        # try to get the user associated with this username
        user = User.query.filter_by(username=form.username.data).first()
        # if this user exists and the password matches
        if user is not None and user.verify_password(form.password.data):
            # log this user in through the login_manager
            login_user(user)
            # redirect the user to the page they wanted or the home page
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("index")
            print("store to cookies:" + form.username.data)
            session["username"] = form.username.data
            return redirect(next)
        else:
            # if the user does not exist or the password is incorrect
            # flash an error message and redirect to login form
            flash("Invalid username or password")
            return redirect(url_for("get_login"))
    else:
        # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("get_login"))

@app.get("/logout/")
@login_required
def get_logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("index"))


# =================================================================================
# Home Page
@app.get("/")
def index():
    username: str = str(session.get("username"))
    # check if the user is logged in using the session
    user_usernames = User.query.with_entities(User.username).all()
    user_usernames_list = [username[0] for username in user_usernames]
    print(user_usernames_list)

    if username in user_usernames_list:
        print("USERNAME: " + username)
        tasks = Task.query.join(User).filter(User.username == username).all()

        for task in tasks:
            print(task.name)
        return render_template("index.html", current_user=current_user, tasks=tasks)
    else:
        flash("Please login")
        return redirect(url_for("get_login"))

# =================================================================================
# Creating Task Lists
def populatetltaskchoices():
    # current_user is of type User -> sweet
    # get the tasks for the current user
    tasks = Task.query.filter_by(user=current_user).all()
    return [(task.id,task.name) for task in tasks]

# when the user clicks the button to add task list, a post request will be sent to
# the server
@app.post("/")
