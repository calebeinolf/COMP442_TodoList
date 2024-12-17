# pip install assemblyai
from __future__ import annotations
import os
import json
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash, jsonify, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

from datetime import date, time
from datetime import datetime

# general use cases:
# date(year,month,day)
# time(hour,minute)

# local imports
from hashing_examples import UpdatedHasher
from loginforms import RegisterForm, LoginForm

# no need to import since we moved the forms to app.py
# from taskandtasklistforms import (
# TaskCreationForm,
# TaskListCreationForm,
# SubtaskCreationForm,
# TaskDeletionForm,
# TaskListDeletionForm,
# SubtaskDeletionForm,
# )

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
    notes = db.Column(db.Unicode, nullable=True)
    userid = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    # now we have a list of subtasks which can refer to their task through the task var
    subtasks = db.relationship("Subtask", backref="task")
    tasklists = db.relationship(
        "TaskList", secondary=TasksToTaskLists, back_populates="tasks"
    )

    def __eq__(self, othertask):
        return isinstance(othertask, Task) and self.id == othertask.id

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "duedate": self.duedate,
            "complete": self.complete,
            "starred": self.starred,
            "notes": self.notes,
            "tasklistnames": [tasklist.name for tasklist in self.tasklists],
        }

    def from_json(json):
        return Task(
            name=json["name"],
            duedate=json["duedate"],
            complete=json["complete"],
            starred=json["starred"],
            userid=current_user.id,
            # tasklists=json["tasklists"]
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

    def to_json(self):
        return {"id": self.id, "name": self.name}

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
    nateothertl.appendtask(nktask1)

    db.session.commit()

# thought it would eliminate a lot of headache to just put these forms
# in app.py so that we can more easily validate things with the database
# =================================================================================
# SERVER SIDE VALIDATION FORMS FOR TASK, TASK LIST, AND SUBTASK CREATION AND DELETION
# =================================================================================
from flask_wtf import FlaskForm
from wtforms.fields import (
    SubmitField,
    StringField,
    SelectMultipleField,
    BooleanField,
    TextAreaField,
    DateField,
    TimeField,
    IntegerField,
)
from wtforms.validators import (
    InputRequired,
    Length,
    Optional,
    NumberRange,
    ValidationError,
)


# =================================================================================
# Creation Forms
# =================================================================================
class TaskListCreationForm(FlaskForm):
    # add title for use in genericform.html -> may want to remove down the road
    title = "New Task List"

    # user will not be an option in forms (user will be current_user from flask_login)
    name = StringField(
        label="Task List Name", validators=[InputRequired(), Length(min=1, max=80)]
    )

    # our choices are not predefined here for tasks, so we'll have a method to populate
    # choices in the routes
    taskids = SelectMultipleField(
        label="Tasks", choices=[], validators=[Optional()], validate_choice=False
    )

    # currently these forms have submit fields. we may be able to remove the submit fields
    createtasklist = SubmitField(label="Create Task List")

    # tasks, subtasks, and task lists should be uniquely named
    def validate_name(form, field):
        tasklists = TaskList.query.filter_by(user=current_user).all()
        for tl in tasklists:
            if tl.name == form.name.data:
                raise ValidationError(
                    f"Cannot have multiple task lists with the same name. There is already a task list named {tl.name}."
                )


# =================================================================================


class TaskCreationForm(FlaskForm):

    title = "Task Creation Form"

    # no option for id (id is autoincrementing)

    name = StringField(
        label="Task Name", validators=[InputRequired(), Length(min=1, max=80)]
    )

    # don't have to check complete or starred
    complete = BooleanField(label="Complete", validators=[Optional()])

    starred = BooleanField(label="Starred", validators=[Optional()])

    progressnotes = TextAreaField(
        "Progress Notes", validators=[Optional(), Length(max=400)]
    )

    duedate = IntegerField("Due Date", validators=[Optional()])
    # duedate = DateField("Due Date",validators=[Optional()])

    duetime = TimeField("Due Time", validators=[Optional()])

    priority = IntegerField(
        "Priority", validators=[Optional(), NumberRange(min=1, max=10)]
    )

    generalnotes = TextAreaField(
        "General Notes", validators=[Optional(), Length(max=400)]
    )

    # userid will not be in the form -> userid will be the id of flask_login current_user

    # subtasks have a separate form

    # once again these choices will be populated in the routes
    tasklistids = SelectMultipleField(
        "Task Lists", choices=[], validators=[Optional()], validate_choice=False
    )

    createtask = SubmitField(label="Create Task")

    # ensure that duetime is not set if duedate is not set
    def validate_duetime(form, field):
        if not form.duedate.data:
            raise ValidationError(
                "A due time cannot be set for a task with no due date."
            )

    # don't need this
    # def validate_name(form,field):
    # tasks = Task.query.filter_by(user=current_user).all()
    # for t in tasks:
    # if t.name == form.name.data:
    # raise ValidationError(f"Cannot have multiple tasks with the same name. There is already a task named {t.name}.")


# =================================================================================


class AnonymousTaskCreationForm(FlaskForm):

    title = "Task Creation Form"

    name = StringField(
        label="Task Name", validators=[InputRequired(), Length(min=1, max=80)]
    )

    duedate = DateField("Due Date", validators=[Optional()])

    # don't have to check complete or starred
    # complete = BooleanField(label="Complete",validators=[Optional()])

    submit = SubmitField(label="Add Task")

    # session["anonymoustasks"] = {id:[name,duedate,complete]}


# =================================================================================


class SubtaskCreationForm(FlaskForm):

    title = "Subtask Creation Form"

    # have to have some way to designate the taskid -> I think we can get it through the routes

    name = StringField(
        label="Subtask Name", validators=[InputRequired(), Length(min=1, max=80)]
    )
    complete = BooleanField(label="Complete", validators=[Optional()])
    priority = IntegerField(
        "Priority", validators=[Optional(), NumberRange(min=1, max=10)]
    )

    createsubtask = SubmitField(label="Create Subtask")

    def validate_name(form, field):
        # TODO: NEED TO SET currenttaskid IN THE session WHEN WE GO TO ADD SUBTASKS TO A CERTAIN TASK
        subtasks = Subtask.query.filter_by(taskid=session.get("currenttaskid")).all()
        for st in subtasks:
            if st.name == form.name.data:
                raise ValidationError(
                    f"Error, cannot have multiple subtasks with the same name for a given task. There's already a {st.name} subtask for this task."
                )


# =================================================================================
# Deletion Forms
# =================================================================================
class SingleTaskDeletionForm(FlaskForm):
    taskid = IntegerField("Task ID", validators=[InputRequired()])
    submit = SubmitField("Delete Task")


class TaskDeletionForm(FlaskForm):

    title = "Delete Task"

    taskids = SelectMultipleField(
        "Tasks", choices=[], validate_choice=False, validators=[InputRequired()]
    )

    submit = SubmitField("Delete Task(s)")


# =================================================================================


class SubtaskDeletionForm(FlaskForm):

    title = "Delete Subtask"

    subtaskids = SelectMultipleField(
        "Subtasks", choices=[], validate_choice=False, validators=[InputRequired()]
    )

    submit = SubmitField("Delete Subtask(s)")


# =================================================================================


class TaskListDeletionForm(FlaskForm):

    title = "Delete Task List"

    tasklistids = SelectMultipleField(
        "Task Lists", choices=[], validate_choice=False, validators=[InputRequired()]
    )

    submit = SubmitField("Delete Task List(s)")


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
            print(f"current_user:{current_user}")
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
    return redirect(url_for("getanonymoususerpage"))


# =================================================================================
# Home Page and View
@app.get("/index/")
@login_required
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
@login_required
def viewalltasks():
    return render_template(
        "view.html",
        alltasklists=TaskList.query.filter_by(userid=current_user.id).all(),
        alltasks=Task.query.filter_by(userid=current_user.id).all(),
    )


# =================================================================================
# AnonymousUserTask = namedtuple("anonymoustask",["name","duedate","complete"])


@app.get("/")
@app.get("/anonymoususer/")
def getanonymoususerpage():
    # IF UNCOMMENTED THE FOLLOWING LINE WILL CLEAR THE SESSION UPON LOADING THE ANONYMOUS USER PAGE
    # session.clear()
    session["anonymoustasks"] = session.get("anonymoustasks", {})
    session["nextanonymoustaskid"] = session.get("nextanonymoustaskid", 0)
    print(session)
    # could do this conditionally only if session["anonymoustasks"] is empty
    flash(
        "Login to access additional features such as task lists, AI task creation, and more!"
    )
    return render_template(
        "anonymoususer.html", tasks=session.get("anonymoustasks", {})
    )


@app.get("/addtaskanonymous/")
def getaddtaskanonymous():
    return render_template("anonymoustaskform.html", form=AnonymousTaskCreationForm())


@app.post("/addtaskanonymous/")
def postaddtaskanonymous():
    print("in postaddtaskanonymous")
    if (form := AnonymousTaskCreationForm()).validate():
        session["anonymoustasks"] = session.get("anonymoustasks", {})
        # complete is False
        addtaskforanonymoususer(form.name.data, form.duedate.data, False)
        print("returned from addtaskforanonymoususer to postaddtaskanonymous fine")
        return redirect(url_for("getanonymoususerpage"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("getaddtaskanonymous"))


def addtaskforanonymoususer(name: str, duedate: date, complete: bool):
    # session keys MUST be strings
    session["anonymoustasks"][str(session["nextanonymoustaskid"])] = [
        name,
        duedate.strftime("%m/%d/%Y") if duedate else "",
        complete,
    ]
    # making sure it (session["nextanonymoustaskid"]) has a value to be safe, but it definitely always should have a value
    session["nextanonymoustaskid"] = session.get("nextanonymoustaskid", 0) + 1


# =================================================================================
# Create Task Via Form
def alltlchoices():
    # get all of the current user's task lists
    tasklists = TaskList.query.filter_by(userid=current_user.id).all()
    # tl is both identified by and labeled by name attribute
    return [(tl.id, tl.name) for tl in tasklists]


@app.get("/api/v0/getcsrftok/<string:mode>/<string:formtype>")
@login_required
def getcsrftok(mode: str, formtype: str):
    # taskform will last outside of if scope
    if mode == "create" and formtype == "task":
        form = TaskCreationForm()
        form.tasklistids.choices = alltlchoices()
    elif mode == "delete" and formtype == "task":
        form = TaskDeletionForm()
        form.taskids.choices = alltaskchoices()

    elif mode == "create" and formtype == "tasklist":
        form = TaskListCreationForm()
        form.taskids.choices = alltaskchoices()
    elif mode == "delete" and formtype == "tasklist":
        form = TaskListDeletionForm()
        form.tasklistids.choices = alltlchoices

    elif mode == "create" and formtype == "subtask":
        form = SubtaskCreationForm()
    elif mode == "delete" and formtype == "subtask":
        form = SubtaskDeletionForm()
        form.subtaskids.choices = subtaskdeletionchoices()
    # return csrf token html element
    return form.csrf_token()


@app.get("/api/v0/getflashedmessages/")
@login_required
def getflashedmessages():
    return jsonify(get_flashed_messages()), 200


@app.get("/api/v0/getauts/")
def getanonusertasks():
    return jsonify(session.get("anonymoustasks", {})), 200


# for anonymous user tasks
@app.get("/togglecomplete/<int:id>/")
def togglecomplete(id: int):
    # print(f"session['anonymoustasks'][str(id)][2] which is {session["anonymoustasks"][str(id)][2]} set to {not session["anonymoustasks"][str(id)][2]}")
    session["anonymoustasks"][str(id)][2] = not session["anonymoustasks"][str(id)][2]
    session.modified = True
    print(session)
    return jsonify(f"toggled to {session["anonymoustasks"][str(id)][2]}"), 200


@app.get("/deleteaut/<int:id>/")
def deleteaut(id: int):
    del session["anonymoustasks"][str(id)]
    session.modified = True
    print(session)
    return jsonify("anonymous user task deleted"), 200


@app.get("/taskform/")
@login_required
def gettaskform():
    form = TaskCreationForm()
    form.tasklistids = alltlchoices()
    return render_template("genericform.html", form=form)


@app.post("/taskform/")
@login_required
def posttaskform():
    if (form := TaskCreationForm()).validate():

        # we populate subtasks after form submission
        newtask = Task(
            name=form.name.data,
            complete=form.complete.data,
            starred=form.starred.data,
            progressnotes=form.progressnotes.data,
            duedate=form.duedate.data,
            duetime=form.duetime.data,
            priority=form.priority.data,
            notes=form.generalnotes.data,
            user=current_user,
        )

        # add a db tasklist to the task for each of the names in tasklistids
        # each task added must belong to the current user
        for tasklistid in form.tasklistids.data:
            # print(f"attempting to add {TaskList.query.filter_by(user=current_user,id=tasklistid).first()} (filter by current user and task list name)")
            newtask.tasklists.append(
                TaskList.query.filter_by(userid=current_user.id, id=tasklistid).first()
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
# Create Subtask Via Form


@app.get("/subtaskform/")
@login_required
def getsubtaskform():
    form = SubtaskCreationForm()
    return render_template("genericform.html", form=form)


@app.post("/subtaskform/")
@login_required
def postsubtaskform():
    if (form := SubtaskCreationForm()).validate():
        if not session.get("currenttaskid"):
            raise ValueError(
                "currenttaskid must be set in the session in order to add a subtask correctly"
            )

        # check to make sure there are no subtasks for this task that have the same name
        # subtasks = Subtask.query.filter_by(taskid=session.get("currenttaskid")).all()
        # for st in subtasks:
        # if st.name == form.name.data:
        # flash(
        # f"Error, cannot have multiple subtasks with the same name for a given task. There's already a {st.name} subtask for this task."
        # )
        # return redirect(url_for("getsubtaskform"))

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
# Creating Task Lists Via Form
def alltaskchoices():
    # current_user is of type User -> sweet
    # get the tasks for the current user
    tasks = Task.query.filter_by(userid=current_user.id).all()
    return [(task.id, task.name) for task in tasks]


# when the user clicks the button to add task list, a post request will be sent to
# the server
@app.get("/tasklistform/")
@login_required
def gettasklistform():
    tlform = TaskListCreationForm()
    tlform.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=tlform)


@app.post("/tasklistform/")
@login_required
def posttasklistform():
    if (form := TaskListCreationForm()).validate():
        # input(f"taskids.data: {form.taskids.data}. Hit Ctrl-C")

        newtl = TaskList(name=form.name.data, userid=current_user.id)

        # add a db task to the task list for each of the ids in taskids
        # each task added must belong to the current user
        for taskid in form.taskids.data:
            # print(f"attempting to add {Task.query.filter_by(user=current_user,id=taskid).first()} (filter by current user and task list id)")
            newtl.appendtask(
                Task.query.filter_by(userid=current_user.id, id=taskid).first()
            )
        db.session.add(newtl)
        db.session.commit()
        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettasklistform"))


# =================================================================================
# AI
# =================================================================================

import chat_gpt
import assemblyai as aai
from config import assemblyAIKey


@app.post("/speech_for_gpt/")
@login_required
def talkToGPT():
    file = request.files["file"]
    file.save("client_side_audio.webm")

    aai.settings.api_key = assemblyAIKey
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe("client_side_audio.webm")
    # transcript = transcriber.transcribe("./my-local-audio-file.wav")

    question = transcript.text

    print(question)

    allTaskLists: list[TaskList] = TaskList.query.filter_by(
        userid=current_user.id
    ).all()
    allTaskListNames: list[str] = [taskList.name for taskList in allTaskLists]
    allTasks: list[Task] = Task.query.filter_by(userid=current_user.id).all()
    allTaskNames: list[str] = [task.name for task in allTasks]

    chatGpt = chat_gpt.Chat_GPT()
    response: chat_gpt.Chat_GPT_Response = chatGpt.newAsk(
        question, allTaskListNames, allTaskNames
    )
    if response.error_message == "None":
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
    else:
        flash(f"ChatGPT Error: {response.error_message}")
        return jsonify({"status": "error", "GPTResponse": response.toDict()})

@app.get("/askChatGPT/")
@login_required
def askGPT():
    question: str = request.args.get("question")

    allTaskLists: list[TaskList] = TaskList.query.filter_by(
        userid=current_user.id
    ).all()
    allTaskListNames: list[str] = [taskList.name for taskList in allTaskLists]
    allTasks: list[Task] = Task.query.filter_by(userid=current_user.id).all()
    allTaskNames: list[str] = [task.name for task in allTasks]

    chatGpt = chat_gpt.Chat_GPT()
    response: chat_gpt.Chat_GPT_Response = chatGpt.newAsk(
        question, allTaskListNames, allTaskNames
    )

    if response.error_message == "None":

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
            # task.duedate = dbTask.duedate

        return jsonify({"status": "success", "GPTResponse": response.toDict()})
    else:
        flash(f"ChatGPT Error: {response.error_message}")
        return jsonify({"status": "error", "GPTResponse": response.toDict()})


def addGPTResponse(response: chat_gpt.Chat_GPT_Response):

    for tasklist in response.tasklists:
        t: TaskList = TaskList(name=tasklist.name, userid=current_user.id)
        db.session.add(t)
    db.session.commit()

    for task in response.tasks:
        taskLists: list[TaskList] = TaskList.query.filter(
            TaskList.name.in_(task.tasklistnames), TaskList.userid == current_user.id
        ).all()
        db.session.add(
            Task(
                name=task.name,
                starred=task.starred,
                duedate=task.duedate,
                priority=task.priority,
                userid=current_user.id,
                tasklists=taskLists,
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
# Task Deletion Via Form


@app.get("/taskdeleteform/")
@login_required
def gettaskdeletion():
    form = TaskDeletionForm()
    form.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=form)


@app.post("/singletaskdelete/")
@login_required
def deleteSingleTask():
    try:
        taskid = request.args.get("taskid")
        deletetask(taskid)
        return {"taskid": taskid}
    except:
        return 400


@app.post("/taskdeleteform/")
@login_required
def posttaskdeletion():
    if (form := TaskDeletionForm()).validate():

        for taskid in form.taskids.data:
            deletetask(taskid)

        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("gettaskdeletion"))


# =================================================================================
# Subtask Deletion Via Form
@app.get("/tasksforsubtaskdeleteform/")
@login_required
def gettasksforsubtaskdeletion():
    # can reuse the TaskDeletion form with a different title here
    form = TaskDeletionForm()
    form.title = "Tasks for Subtask Deletion"
    form.submit.label.text = "Delete Subtasks For These"
    form.taskids.choices = alltaskchoices()
    return render_template("genericform.html", form=form)


@app.post("/tasksforsubtaskdeleteform/")
@login_required
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


@app.get("/subtaskdeleteform/")
@login_required
def getsubtaskdeletion():
    form = SubtaskDeletionForm()
    form.subtaskids.choices = subtaskdeletionchoices()
    return render_template("genericform.html", form=form)


@app.post("/subtaskdeleteform/")
@login_required
def postsubtaskdeletion():
    if (form := SubtaskDeletionForm()).validate():
        for subtaskid in form.subtaskids.data:
            deletesubtask(subtaskid)
        return redirect(url_for("index"))
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
    return redirect(url_for("getsubtaskdeletion"))


# =================================================================================
# Task List Deletion Via Form
@app.get("/tasklistdeleteform/")
@login_required
def gettasklistdeletion():
    form = TaskListDeletionForm()
    form.tasklistids.choices = alltlchoices()
    return render_template("genericform.html", form=form)


@app.post("/tasklistdeleteform/")
@login_required
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
    tl = TaskList.query.filter_by(userid=current_user.id, id=tlid).first()
    # if a task belongs to the current user, is in the specified task list, and
    # the task list being deleted is the only task list that it belongs to ->
    # delete the task
    tasks = Task.query.filter_by(userid=current_user.id).all()
    for task in tasks:
        if tl in task.tasklists and len(task.tasklists) < 2:
            deletetask(task.id)

    db.session.delete(tl)
    db.session.commit()


@app.get("/getListTasks/<int:listId>/")
@login_required
def getTasksFromList(listId):
    tasks: list[Task] = (
        Task.query.join(TasksToTaskLists)
        .filter(TasksToTaskLists.c.tlid == listId)
        .filter(Task.userid == current_user.id)
        .all()
    )

    return jsonify({"tasks": [task.to_json() for task in tasks]})


@app.get("/getUserTaskLists/")
@login_required
def getUserTaskLists():
    tasklists: list[TaskList] = TaskList.query.filter_by(userid=current_user.id).all()

    print(f"Task Lists: {tasklists}")

    return jsonify({"tasklists": [taskList.to_json() for taskList in tasklists]})


# @cross_origin(supports_credentials=True)
@app.get("/getUserTasks/")
@login_required
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
@login_required
def postTask():
    if (form := TaskCreationForm()).validate():
        # instead of getting the object from json, we can do what we
        # normally would do with wtforms because we're using URLSearchParams
        # newTask = Task.from_json(request.json)

        newtask = Task(
            name=form.name.data,
            complete=form.complete.data,
            starred=form.starred.data,
            progressnotes=form.progressnotes.data,
            duedate=form.duedate.data,
            duetime=form.duetime.data,
            priority=form.priority.data,
            notes=form.generalnotes.data,
            user=current_user,
        )

        # add a db tasklist to the task for each of the names in tasklistids
        # each task added must belong to the current user
        #print(f"{form.tasklistids.data = }")
        for tasklistid in form.tasklistids.data:
            # print(f"attempting to add {TaskList.query.filter_by(user=current_user,id=tasklistid).first()} (filter by current user and task list name)")
            if tasklistid:
                newtask.tasklists.append(
                    TaskList.query.filter_by(user=current_user, id=tasklistid).first()
                )
        # add and commit to the database, then we ask if the user would like to add subtasks
        db.session.add(newtask)  # like before
        db.session.commit()  # like before

        print("added task: " + newtask.name)
        # is it incorrect to return json here because application/x-www-form-urlencoded is
        # what was sent to us? -> answer: nah, I think it's fine
        return jsonify(newtask.to_json()), 201
    # if failed add, tell them why
    for field, em in form.errors.items():
        flash(f"Error in {field}: {em}")
        print(f"flashed 'Error in {field}: {em}'")

    return (
        jsonify(
            {"message": "Requested creation of an invalid task: task creation failed"}
        ),
        400,
    )


@app.post("/updateUserTask/")
@login_required
def updateTask():
    response = request.json
    print(response)
    taskId = response["id"]
    task = Task.query.get_or_404(taskId)

    task.name = response["name"]
    task.duedate = response["duedate"]
    task.notes = response["notes"]

    db.session.commit()

    return task.to_json()


@app.post("/markComplete/<int:taskId>/<int:complete>/")
@login_required
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
@login_required
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


@app.get("/getUserColor/")
@login_required
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
@login_required
def postColor():
    newColor = request.json
    current_user.themecolor = newColor
    db.session.commit()
    return jsonify(newColor), 201
