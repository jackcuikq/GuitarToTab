from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class TabForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    audio = FileField('Upload Audio', validators=[FileAllowed(['wav'])]) 
    submit = SubmitField('Create')
    content = TextAreaField('Tab')