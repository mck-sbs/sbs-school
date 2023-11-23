from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired, NumberRange


class DelForm(FlaskForm):
    token = StringField('Token:', validators=[DataRequired()])
    submit = SubmitField('Lösche Link')



