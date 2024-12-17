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
        label="Task List Name", validators=[InputRequired(), Length(max=80)]
    )

    # our choices are not predefined here for tasks, so we'll have a method to populate
    # choices in the routes
    taskids = SelectMultipleField(
        label="Tasks", choices=[], validators=[Optional()], validate_choice=False
    )

    # currently these forms have submit fields. we may be able to remove the submit fields
    createtasklist = SubmitField(label="Create Task List")


# =================================================================================


class TaskCreationForm(FlaskForm):

    title = "Task Creation Form"

    # no option for id (id is autoincrementing)

    name = StringField(label="Task Name", validators=[InputRequired(), Length(max=80)])

    # don't have to check complete or starred
    complete = BooleanField(label="Complete", validators=[Optional()])

    starred = BooleanField(label="Starred", validators=[Optional()])

    progressnotes = TextAreaField(
        "Progress Notes", validators=[Optional(), Length(max=400)]
    )

    duedate = DateField("Due Date", validators=[Optional()])

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


# =================================================================================


class SubtaskCreationForm(FlaskForm):

    title = "Subtask Creation Form"

    # have to have some way to designate the taskid -> I think we can get it through the routes

    name = StringField(
        label="Subtask Name", validators=[InputRequired(), Length(max=80)]
    )
    complete = BooleanField(label="Complete", validators=[Optional()])
    priority = IntegerField(
        "Priority", validators=[Optional(), NumberRange(min=1, max=10)]
    )

    createsubtask = SubmitField(label="Create Subtask")


# =================================================================================
# Deletion Forms
# =================================================================================
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
