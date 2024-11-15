from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectMultipleField
from wtforms.validators import InputRequired, Length, Optional

class TaskListForm(FlaskForm):
    name = StringField(label="Task List Name", validators=[InputRequired(),Length(max=80)])
    # our choices are not predefined here for tasks, so we'll have a method to populate
    # choices in the routes
    tasks = SelectMultipleField(label="Tasks",choices=[],validators=[Optional()],validate_choice=True)
    createtasklist = SubmitField(label="Create Task List")

class TaskForm(FlaskForm):
    pass

