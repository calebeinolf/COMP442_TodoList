# pip install assemblyai
from __future__ import annotations
import os
import json
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user
from flask_cors import CORS, cross_origin

from datetime import date, time
from datetime import datetime

# general use cases:
# date(year,month,day)
# time(hour,minute)

# local imports
from hashing_examples import UpdatedHasher
from loginforms import RegisterForm, LoginForm
from taskandtasklistforms import (
    TaskCreationForm,
    TaskListCreationForm,
    SubtaskCreationForm,
    TaskDeletionForm,
    TaskListDeletionForm,
    SubtaskDeletionForm,
)

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
# CORS(app, support_credentials=True)
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
    themecolor = db.Column(db.Unicode, default="#2662cb")
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
# tlname = db.Column(db.Unicode, db.ForeignKey("TaskLists.id"))
# taskid = db.Column(db.Integer, db.ForeignKey("Tasks.id"))

TasksToTaskLists = db.Table(
    "TasksToTaskLists",
    db.Column("tlid", db.Unicode, db.ForeignKey("TaskLists.id"), nullable=False),
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # don't want unique because different users could have same names for their tasks
    name = db.Column(db.Unicode, nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    starred = db.Column(db.Boolean, nullable=False, default=False)

    # -----------------------------------------------------
    # optional attributes
    progressnotes = db.Column(db.Unicode, nullable=True)
    # duedate = db.Column(db.Date, nullable=True)
    duedate = db.Column(db.Integer, nullable=True)

    # duedate MUST have a value in order for there to be a duetime
    # enforce this through forms and the way we present options to the user ->
    # the duetime field should only become visible when a duedate has been selected
    duetime = db.Column(
        db.Time, nullable=True
    )  # default=duetimedefault, onupdate=duetimedefault

    # should be a value in range [1,10] if not null
    priority = db.Column(db.Integer, nullable=True)
    generalnotes = db.Column(db.Unicode, nullable=True)
    userid = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    # now we have a list of subtasks which can refer to their task through the task var
    subtasks = db.relationship("Subtask", backref="task")
    tasklists = db.relationship(
        "TaskList", secondary=TasksToTaskLists, back_populates="tasks"
    )

    def __eq__(self, othertask):
        return isinstance(othertask, Task) and self.id == othertask.id

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

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "duedate": self.duedate,
            "complete": self.complete,
            "starred": self.starred,
        }

    def from_json(json):
        return Task(
            name=json["name"],
            duedate=json["duedate"],
            complete=json["complete"],
            starred=json["starred"],
            userid=current_user.id,
        )


# =================================================================================


class Subtask(db.Model):
    __tablename__ = "Subtasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    taskid = db.Column(db.Integer, db.ForeignKey("Tasks.id"), nullable=False)

    # should be a value in range [1,10] if not null
    priority = db.Column(db.Integer, nullable=True)

    def __eq__(self, otherst):
        return isinstance(otherst, Subtask) and self.id == otherst.id

    # def __init__(self,name,taskid,complete=False):
    # self.name=name
    # self.taskid=taskid
    # self.complete=complete


# =================================================================================


class TaskList(db.Model):
    __tablename__ = "TaskLists"
    # need an integer id because we want different users to be able to have
    # task lists with the same name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    tasks = db.relationship(
        "Task", secondary=TasksToTaskLists, back_populates="tasklists"
    )
    userid = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    def appendtask(self, task):
        self.tasks.append(task)

    # define eq function in case we want to compare task lists to see if they're equal
    # (we do want eq because it is called under the hood in the list __contains__
    # method which is being used with Task.tasklists)
    def __eq__(self, othertl):
        return isinstance(othertl, TaskList) and self.id == othertl.id

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
    dlr = User("david", "pass123456")

    db.session.add_all((nk, ce, dlr))

    nktask1 = Task(
        name="W project checkpoint",
        # User.query.filter_by(username="natekuhns").first().id,
        # duedate=date(2024, 11, 20),
        duedate=1732165200000,
        duetime=time(23, 59),
        priority=1,
        user=nk,
    )
    nktask2 = Task(name="othertask", complete=1, duetime=time(23, 59), user=nk)

    nktask3 = Task(name="task3", user=nk)

    nktask4 = Task(name="Christmas!", duedate=1735102800000, user=nk, starred=True)
    nktask5 = Task(name="Christmas Eve", duedate=1735016400000, user=nk, starred=False)

    dtask1 = Task(name="Run Laundry", duedate=date(2024, 11, 2), userid=3)

    ctask1 = Task(name="Run Laundry", duedate=date(2024, 12, 10), userid=2)
    ctask2 = Task(name="Christmas Eve", duedate=date(2024, 12, 24), userid=2)
    ctask3 = Task(name="Christmas", duedate=date(2024, 12, 25), userid=2)

    db.session.add_all(
        (nktask1, nktask2, nktask3, nktask4, nktask5, dtask1, ctask1, ctask2, ctask3)
    )

    nktst1 = Subtask(name="sub1", task=nktask3)

    db.session.add(nktst1)

    natewebtl = TaskList(name="Web", user=nk)
    nateothertl = TaskList(name="Other", user=nk)

    db.session.add_all((natewebtl, nateothertl))

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
            flash("There is already an account with that username.")
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
# Home Page and View
@app.get("/")
@app.get("/index/")
def index():
    # reset current task id and tasks for which subtask deletions are happening
    # in case they have values
    session["deletesubtasksfor"] = []
    session["currenttaskid"] = None
    username: str = str(session.get("username"))
    # check if the user is logged in using the session
    user_usernames = User.query.with_entities(User.username).all()
    user_usernames_list = [username[0] for username in user_usernames]
    print(user_usernames_list)

    if username in user_usernames_list:
        print("USERNAME: " + username)
        tasks = Task.query.join(User).filter(User.username == username).all()

        for task in tasks:
            print(task.duedate)
        print(date.today())
        return render_template(
            "index.html",
            current_user=current_user,
            tasks=tasks,
            current_date=date.today(),
        )
    else:
        flash("Please login")
        return redirect(url_for("get_login"))


@app.get("/viewalltasks/")
def view():
    return render_template(
        "view.html",
        alltasklists=TaskList.query.filter_by(user=current_user).all(),
        alltasks=Task.query.filter_by(user=current_user).all(),
    )


# =================================================================================
# Create Task
def alltlchoices():
    # get all of the current user's task lists
    tasklists = TaskList.query.filter_by(user=current_user).all()
    # tl is both identified by and labeled by name attribute
    return [(tl.id, tl.name) for tl in tasklists]


@app.get("/task/")
def gettaskform():
    taskform = TaskCreationForm()
    taskform.tasklistids.choices = alltlchoices()
    return render_template("genericform.html", form=taskform)


@app.post("/task/")
def posttaskform():
    if (form := TaskCreationForm()).validate():

        # check to make sure there are no subtasks for this task that have the same name
        tasks = Task.query.filter_by(user=current_user).all()
        for t in tasks:
            if t.name == form.name.data:
                flash(
                    f"Error, cannot have multiple tasks with the same name. There is already a task named {t.name}."
                )
                return redirect(url_for("gettaskform"))

        # we populate subtasks after form submission
        newtask = Task(
            name=form.name.data,
            complete=form.complete.data,
            starred=form.starred.data,
            progressnotes=form.progressnotes.data,
            duedate=form.duedate.data,
            duetime=form.duetime.data,
            priority=form.priority.data,
            generalnotes=form.generalnotes.data,
            user=current_user,
        )

        # add a db tasklist to the task for each of the names in tasklistids
        # each task added must belong to the current user
        for tasklistid in form.tasklistids.data:
            # print(f"attempting to add {TaskList.query.filter_by(user=current_user,id=tasklistid).first()} (filter by current user and task list name)")
            newtask.tasklists.append(
                TaskList.query.filter_by(user=current_user, id=tasklistid).first()
            )
        # add and commit to the database, then we ask if the user would like to add subtasks
        db.session.add(newtask)
        db.session.commit()
        session["currenttaskid"] = newtask.id
        return redirect(url_for("getsubtaskform"))
    # input(f"tasklistids.data: {form.tasklistids.data}. Hit Ctrl-C")
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettaskform"))


# =================================================================================
# Create Subtask


@app.get("/subtask/")
def getsubtaskform():
    form = SubtaskCreationForm()
    return render_template("genericform.html", form=form)


@app.post("/subtask/")
def postsubtaskform():
    if (form := SubtaskCreationForm()).validate():
        if not session.get("currenttaskid"):
            raise ValueError(
                "currenttaskid must be set in the session in order to add a subtask correctly"
            )

        # check to make sure there are no subtasks for this task that have the same name
        subtasks = Subtask.query.filter_by(taskid=session.get("currenttaskid")).all()
        for st in subtasks:
            if st.name == form.name.data:
                flash(
                    f"Error, cannot have multiple subtasks with the same name for a given task. There's already a {st.name} subtask for this task."
                )
                return redirect(url_for("getsubtaskform"))

        newst = Subtask(
            name=form.name.data,
            complete=form.complete.data,
            taskid=session.get("currenttaskid"),
            priority=form.priority.data,
        )

        db.session.add(newst)
        db.session.commit()
        return redirect(url_for("getsubtaskform"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("getsubtaskform"))


# =================================================================================
# Creating Task Lists
def alltaskchoices():
    # current_user is of type User -> sweet
    # get the tasks for the current user
    tasks = Task.query.filter_by(user=current_user).all()
    return [(task.id, task.name) for task in tasks]


# when the user clicks the button to add task list, a post request will be sent to
# the server


@app.get("/tasklist/")
def gettasklistform():
    tlform = TaskListCreationForm()
    tlform.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=tlform)


@app.post("/tasklist/")
def posttasklistform():
    if (form := TaskListCreationForm()).validate():
        # input(f"taskids.data: {form.taskids.data}. Hit Ctrl-C")

        # check to make sure there are no subtasks for this task that have the same name
        tasklists = TaskList.query.filter_by(user=current_user).all()
        for tl in tasklists:
            if tl.name == form.name.data:
                flash(
                    f"Error, cannot have multiple task lists with the same name. There is already a task list named {tl.name}."
                )
                return redirect(url_for("gettasklistform"))

        newtl = TaskList(name=form.name.data, user=current_user)

        # add a db task to the task list for each of the ids in taskids
        # each task added must belong to the current user
        for taskid in form.taskids.data:
            # print(f"attempting to add {Task.query.filter_by(user=current_user,id=taskid).first()} (filter by current user and task list id)")
            newtl.appendtask(Task.query.filter_by(user=current_user, id=taskid).first())
        db.session.add(newtl)
        db.session.commit()
        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettasklistform"))


import chat_gpt
import assemblyai as aai
from config import assemblyAIKey


@login_required
@app.post("/speech_for_gpt/")
def talkToGPT():
    file = request.files["file"]
    file.save("client_side_audio.webm")

    aai.settings.api_key = assemblyAIKey
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe("client_side_audio.webm")
    # transcript = transcriber.transcribe("./my-local-audio-file.wav")

    question = transcript.text

    print(question)
    chatGpt = chat_gpt.Chat_GPT()
    response: chat_gpt.Chat_GPT_Response = chatGpt.newAsk(question, [], [])
    addGPTResponse(response)

    for tasklist in response.tasklists:
        dbTasklist: TaskList = TaskList.query.filter_by(
            name=tasklist.name, userid=current_user.id
        ).first()
        tasklist.id = dbTasklist.id

    for subtask in response.subtasks:
        dbParentTask: Task = Task.query.filter_by(
            name=subtask.parenttaskname, userid=current_user.id
        ).first()
        dbSubtask: Subtask = Subtask.query.filter_by(
            name=subtask.name, taskid=dbParentTask.id
        )
        subtask.id = dbSubtask.id

    for task in response.tasks:
        dbTask: Task = Task.query.filter_by(
            name=task.name, userid=current_user.id
        ).first()
        task.id = dbTask.id

    return jsonify({"status": "success", "GPTResponse": response.toDict()})


@login_required
@app.get("/askChatGPT/")
def askGPT():
    question: str = request.args.get("question")
    types = request.args.get("types")
    print(types)
    actualTypes = [item.strip() for item in types.split(",")]

    chatGpt = chat_gpt.Chat_GPT()
    response: chat_gpt.Chat_GPT_Response = chatGpt.newAsk(question, [], [])

    addGPTResponse(response)

    for tasklist in response.tasklists:
        dbTasklist: TaskList = TaskList.query.filter_by(
            name=tasklist.name, userid=current_user.id
        ).first()
        tasklist.id = dbTasklist.id

    for subtask in response.subtasks:
        dbParentTask: Task = Task.query.filter_by(
            name=subtask.parenttaskname, userid=current_user.id
        ).first()
        dbSubtask: Subtask = Subtask.query.filter_by(
            name=subtask.name, taskid=dbParentTask.id
        )
        subtask.id = dbSubtask.id

    for task in response.tasks:
        dbTask: Task = Task.query.filter_by(
            name=task.name, userid=current_user.id
        ).first()
        task.id = dbTask.id

    return jsonify({"status": "success", "GPTResponse": response.toDict()})


def addGPTResponse(response: chat_gpt.Chat_GPT_Response):
    for tasklist in response.tasklists:
        t: TaskList = TaskList(name=tasklist.name, userid=current_user.id)
        db.session.add(t)
    db.session.commit()

    for task in response.tasks:
        db.session.add(
            Task(
                name=task.name,
                starred=task.starred,
                duedate=datetime.strptime(task.duedate, "%Y-%m-%d,%H:%M"),
                priority=task.priority,
                userid=current_user.id,
            )
        )
    db.session.commit()

    for subtask in response.subtasks:
        taskid = Task.query.filter(Task.name == subtask.parenttaskname).first().id
        db.session.add(
            Subtask(name=subtask.name, priority=subtask.priority, taskid=taskid)
        )
    db.session.commit()


# =================================================================================
# Deleting Tasks, Subtasks, and Task Lists
# =================================================================================

# =================================================================================
# Task Deletion Form


@app.get("/taskdelete/")
def gettaskdeletion():
    form = TaskDeletionForm()
    form.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=form)


@app.post("/taskdelete/")
def posttaskdeletion():
    if (form := TaskDeletionForm()).validate():

        for taskid in form.taskids.data:
            deletetask(taskid)

        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettaskdeletion"))


# =================================================================================
# Subtask Deletion Form
@app.get("/tasksforsubtaskdelete/")
def gettasksforsubtaskdeletion():
    # can reuse the TaskDeletion form with a different title here
    form = TaskDeletionForm()
    form.title = "Tasks for Subtask Deletion"
    form.submit.label.text = "Delete Subtasks For These"
    form.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=form)


@app.post("/tasksforsubtaskdelete/")
def posttasksforsubtaskdeletion():
    if (form := TaskDeletionForm()).validate():

        # make a list of tasks for which we will delete subtasks
        session["deletesubtasksfor"] = []
        for taskid in form.taskids.data:
            session["deletesubtasksfor"].append(taskid)

        return redirect(url_for("getsubtaskdeletion"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettasksforsubtaskdeletion"))


def subtaskdeletionchoices():
    if not session.get("deletesubtasksfor"):
        raise ValueError(
            "deletesubtasksfor must be set in the session in order to delete subtasks correctly"
        )
    choices = []
    for taskid in session.get("deletesubtasksfor"):
        # append all subtasks for each of the tasks we're deleting subtasks for
        task = Task.query.filter_by(id=taskid).first()
        choices += [
            (subtask.id, f"{task.name} subtask: {subtask.name}")
            for subtask in task.subtasks
        ]
    return choices


@app.get("/subtaskdelete/")
def getsubtaskdeletion():
    form = SubtaskDeletionForm()
    form.subtaskids.choices = subtaskdeletionchoices()
    return render_template("genericform.html", form=form)


@app.post("/subtaskdelete/")
def postsubtaskdeletion():
    if (form := SubtaskDeletionForm()).validate():
        for subtaskid in form.subtaskids.data:
            deletesubtask(subtaskid)
        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("getsubtaskdeletion"))


# =================================================================================
# Task List Deletion Form
@app.get("/tasklistdelete/")
def gettasklistdeletion():
    form = TaskListDeletionForm()
    form.tasklistids.choices = alltlchoices()
    return render_template("genericform.html", form=form)


@app.post("/tasklistdelete/")
def posttasklistdeletion():
    if (form := TaskListDeletionForm()).validate():

        for tasklistid in form.tasklistids.data:
            deletetasklist(tasklistid)

        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettasklistdeletion"))


# =================================================================================
# Deletion Helper Functions
def deletetask(taskid):
    # checking for current_user should be unnecessary here (we'll be getting ids from a form
    # and that form will be populated with the users tasks, not anyone elses... so yeah)
    # delete all subtasks of the task
    for subtask in Subtask.query.filter_by(taskid=taskid).all():
        deletesubtask(subtask.id)

    # delete the task itself
    db.session.delete(Task.query.filter_by(id=taskid).first())
    db.session.commit()


def deletesubtask(stid):
    db.session.delete(Subtask.query.filter_by(id=stid).first())
    db.session.commit()


def deletetasklist(tlid):
    tl = TaskList.query.filter_by(user=current_user, id=tlid).first()
    # if a task belongs to the current user, is in the specified task list, and
    # the task list being deleted is the only task list that it belongs to ->
    # delete the task
    tasks = Task.query.filter_by(user=current_user).all()
    for task in tasks:
        if tl in task.tasklists and len(task.tasklists) < 2:
            deletetask(task.id)

    db.session.delete(tl)
    db.session.commit()


# @cross_origin(supports_credentials=True)
@app.get("/getUserTasks/")
def getTasks():
    username = session.get("username")
    tasks = (
        Task.query.join(User)
        .filter(User.username == username)
        .order_by(Task.duedate)
        .all()
    )

    print("get tasks:")
    for task in tasks:
        print(task.to_json())

    return jsonify(
        {
            "retrieved": datetime.now().isoformat(),
            "count": len(tasks),
            "tasks": [task.to_json() for task in tasks],
        }
    )


@app.post("/postUserTask/")
def postTask():
    newTask = Task.from_json(request.json)
    db.session.add(newTask)
    db.session.commit()
    print("added task: " + newTask.name)
    return jsonify(newTask.to_json()), 201


@app.post("/markComplete/<int:taskId>/<int:complete>/")
# "copmlete" should be a 0 or 1
def markComplete(taskId, complete):
    task = Task.query.get_or_404(taskId)
    task.complete = complete
    db.session.commit()
    if complete:
        return jsonify(
            {
                "message": "Task marked completed",
                "task_id": task.id,
                "complete": task.complete,
            }
        )
    else:
        return jsonify(
            {
                "message": "Task marked imcomplete",
                "task_id": task.id,
                "complete": task.complete,
            }
        )


@app.post("/markStarred/<int:taskId>/<int:starred>/")
# "starred" should be a 0 or 1
def markStarred(taskId, starred):
    task = Task.query.get_or_404(taskId)
    task.starred = starred
    db.session.commit()
    if starred:
        return jsonify(
            {
                "message": "Task starred",
                "task_id": task.id,
                "starred": task.starred,
            }
        )
    else:
        return jsonify(
            {
                "message": "Task unstarred",
                "task_id": task.id,
                "starred": task.starred,
            }
        )


# To be implemented:
@app.get("/getUserColor/")
def getColor():
    username = session.get("username")
    userColor = User.query.filter_by(username=username).first().themecolor
    return jsonify(
        {
            "retrieved": datetime.now().isoformat(),
            "userColor": userColor,
        }
    )


@app.post("/postUserColor/")
def postColor():
    newColor = request.json
    current_user.themecolor = newColor
    db.session.commit()
    return jsonify(newColor), 201
