from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    msg = StringField('Nachricht: ', validators=[DataRequired()])
    submit = SubmitField('Senden', render_kw={'id': 'sendButton'})



