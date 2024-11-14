from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,StringField,SelectMultipleField,BooleanField,TextAreaField,DateField,TimeField,IntegerField
from wtforms.validators import InputRequired,Length,Optional,NumberRange,ValidationError

class TaskListForm(FlaskForm):
    # user will not be an option in forms (user will be current_user from flask_login)
    name = StringField(label="Task List Name", validators=[InputRequired(),Length(max=80)])
    
    # our choices are not predefined here for tasks, so we'll have a method to populate
    # choices in the routes
    tasks = SelectMultipleField(label="Tasks",choices=[],validators=[Optional()],validate_choice=True)
    
    createtasklist = SubmitField(label="Create Task List")

class TaskForm(FlaskForm):
    # no option for id (id is autoincrementing)

    name = StringField(label="Task Name", validators=[InputRequired(),Length(max=80)])
    
    # don't have to check complete or starred
    complete = BooleanField(label="Complete",validators=[Optional()])

    starred = BooleanField(label="Starred",validators=[Optional()])

    progressnotes = TextAreaField("Progress Notes",validators=[Optional(),Length(max=400)])

    duedate = DateField("Due Date",validators=[Optional()])

    duetime = TimeField("Due Time",validators=[Optional()])

    priority = IntegerField("Priority",validators=[NumberRange(min=1,max=10)])

    generalnotes = TextAreaField("General Notes",validators=[Optional(),Length(max=400)])

    # userid will not be in the form -> userid will be the id of flask_login current_user

    # subtasks have a separate form

    # once again these choices will be populated in the routes
    tasklists = SelectMultipleField("Task Lists",choices=[],validators=[Optional()],validate_choice=True)

    # ensure that duetime is not set if duedate is not set
    def validate_duetime(form,field):
        if not form.duedate: raise ValidationError("A due time cannot be set for a Task with no due date.")

class SubtaskForm(FlaskForm):
    # have to have some way to designate the taskid -> I think we can do that elsewhere
    name = StringField(label="Subtask Name", validators=[InputRequired(),Length(max=80)])
    complete = BooleanField(label="Complete",validators=[Optional()])