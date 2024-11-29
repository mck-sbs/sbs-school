from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired


# ChatForm class represents a simple chat form with a message input and submit button
class ChatForm(FlaskForm):
    # Message input field with a label "Nachricht: " and a DataRequired validator to ensure it’s not empty
    msg = StringField('Nachricht: ', validators=[DataRequired()])
    # Submit button with custom HTML attribute to set the button's ID as 'sendButtonChat'
    submit = SubmitField('Senden', render_kw={'id': 'sendButtonChat'})


# ChatPicForm class represents a chat form similar to ChatForm, potentially for a chat that involves sending images
class ChatPicForm(FlaskForm):
    # Message input field with a label "Nachricht: " and a DataRequired validator to ensure it’s not empty
    msg = StringField('Nachricht: ', validators=[DataRequired()])
    # Submit button with custom HTML attribute to set the button's ID as 'sendButton'
    submit = SubmitField('Senden', render_kw={'id': 'sendButton'})