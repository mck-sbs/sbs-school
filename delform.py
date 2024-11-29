from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired, NumberRange


# DelForm class defines a form for deleting a link, requiring a token for authorization
class DelForm(FlaskForm):
    # Token input field with a label "Token:" and a DataRequired validator to ensure it’s not empty
    token = StringField('Token:', validators=[DataRequired()])
    # Submit button with a label "Lösche Link" (translated as "Delete Link")
    submit = SubmitField('Lösche Link')