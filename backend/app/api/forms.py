from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

class ICalForm(FlaskForm):
    ical_file = FileField('iCal File', validators=[
        FileRequired(),
        FileAllowed(['ics'], 'iCal Files only!')
    ])
    submit = SubmitField('Import iCal')