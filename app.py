import secrets
import datetime
import json
from flask import Flask, render_template, jsonify, request
from flask_simple_crypt import SimpleCrypt
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from flask_htpasswd import HtPasswdAuth
from openai import OpenAI
import genform as gf
import delform as df
import chatform as cf

# Load values from user_config.json
# These values include API keys, model names, and other configurations
API_KEY = ""
GPT_MODEL = ""
DALLE_MODEL = ""
LINK = ""
DEL_WINDOW = 7
###

# Constants
TOKEN_LEN = 32  # Length of generated tokens for security
SQL_PATH = "sqlite:///gpt.db"  # Path to the SQLite database

# Initialize the Flask app
app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = 'config/.htpasswd'  # Path for password configuration
app.config['SECRET_KEY'] = 'Please change this key'  # Secret key for session handling
app.config['SQLALCHEMY_DATABASE_URI'] = SQL_PATH  # Setting up the database URI

# Integrate additional libraries with the Flask app
bootstrap = Bootstrap4(app)  # Bootstrap for frontend styling
htpasswd = HtPasswdAuth(app)  # Basic HTTP authentication
cipher = SimpleCrypt()  # Encryption for sensitive data
cipher.init_app(app)
db = SQLAlchemy(app)  # Database integration with SQLAlchemy


# Define the database model for the "Link" table
class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String, nullable=False)  # Encrypted API key
    token_master = db.Column(db.String, nullable=False, index=True)  # Token for user to delete links
    token = db.Column(db.String, nullable=False, index=True)  # Unique token for link access
    context = db.Column(db.String)  # Context for the AI model
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Timestamp for link creation

    # Initialize the Link instance with necessary attributes
    def __init__(self, api_key=None, token=None, token_master=None, context=context, time=None):
        self.api_key = api_key
        self.token = token
        self.token_master = token_master
        self.context = context
        self.time = time


# Set up app context to initialize the database and load configuration
with app.app_context():
    db.drop_all()
    db.create_all()

    with open("/Users/student-sbs/PycharmProjects/sbs-schoolDEV/config/user_config.json") as file:
        config = json.load(file)
        API_KEY = config['API_KEY']
        GPT_MODEL = config['GPT_MODEL']
        LINK = config['LINK']
        DEL_WINDOW = config['DEL_WINDOW']
        DALLE_MODEL = config['DALLE_MODEL']

# Define the main route for index page
@app.route("/", methods=('GET', 'POST'))
def index():
    return render_template('index.html')


# Define a route to delete links based on tokens
@app.route("/delete", methods=('GET', 'POST'))
@app.route("/delete.html", methods=('GET', 'POST'))
@htpasswd.required  # Protect the route with HTTP authentication
def delete(user):
    form = df.DelForm()  # Form to handle deletion input
    data = " "

    # Check if form is submitted and validated
    if form.validate_on_submit():
        try:
            # Attempt to delete links associated with a given token
            token = form.token.data.strip()
            status = db.session.query(Link).filter(Link.token_master.like(token))
            cnt = status.count()
            status.delete()
            db.session.commit()
            data = "Number of deleted links: " + str(cnt)

            # Also delete links older than the configured deletion window
            too_old = datetime.datetime.today() - datetime.timedelta(days=DEL_WINDOW)
            status = db.session.query(Link).filter(Link.time < too_old)
            cnt_old = status.count()
            status.delete()
            db.session.commit()
            print("Old data deleted: " + str(cnt_old))
        except:
            data = "Error deleting data. Please try again."
        else:
            data = "Number of deleted links: " + str(cnt)
    return render_template('delete.html', form=form, data=data)


# Define a route to generate a link for image generation
@app.route('/generatorpic', methods=('GET', 'POST'))
@app.route('/generatorpic.html', methods=('GET', 'POST'))
@htpasswd.required
def generatorpic(user):
    form = gf.GenPicForm()  # Form for generating image links
    data = "Please enter the condition and the number of links above. Each link can generate one image only."

    if form.validate_on_submit():
        link = " "
        api_key = API_KEY
        context = form.context.data.strip()
        try:
            # Verify the API key with a test request to OpenAI
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": "Reply with 'Hello' if you read this."}],
            )
        except:
            data = "API key could not be verified. Please check and try again."
        else:
            token_master = secrets.token_urlsafe(TOKEN_LEN)

            try:
                links = []
                for i in range(form.vals.data):  # Create multiple links based on input
                    token = secrets.token_urlsafe(TOKEN_LEN)
                    link = LINK + token + "§PIC§.html"

                    # Save the API key, token, and other data to the database
                    db.session.add(Link(cipher.encrypt(api_key.encode()), token, token_master, context))
                    db.session.commit()
                    links.append(link)
            except:
                data = "Error saving data. Please try again."
            else:
                data = "API key successfully verified. Save the token to later delete the link for students."

            return render_template('generatorpic.html', form=form, data=data, links=links)

    return render_template('generatorpic.html', form=form, data=data)


# Define a route to generate links without image generation
@app.route('/generator', methods=('GET', 'POST'))
@app.route('/generator.html', methods=('GET', 'POST'))
@htpasswd.required
def generator(user):
    form = gf.GenForm()  # Form for generating non-image links
    data = "Please enter context above. API key will be verified afterward."

    if form.validate_on_submit():
        link = " "
        api_key = API_KEY
        context = form.context.data.strip()

        try:
            # Verify the API key with a test request to OpenAI
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": "Reply with 'Hello' if you read this."}],
            )
        except:
            data = "API key could not be verified. Please check and try again."
        else:
            token_master = secrets.token_urlsafe(TOKEN_LEN)

            try:
                token = secrets.token_urlsafe(TOKEN_LEN)
                link = LINK + token + ".html"
                # Save the API key, token, and context to the database
                db.session.add(Link(cipher.encrypt(api_key.encode()), token, token_master, context))
                db.session.commit()
            except:
                data = "Error saving data. Please try again."
            else:
                data = "API key successfully verified. Save the token to later delete the link for students."

            return render_template('generator.html', form=form, data=data, link=link)

    return render_template('generator.html', form=form, data=data)


# Define a route to handle message sending and response generation
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']

    chat_items = None
    api_key = None
    context = None
    for item in message:
        if 'chat' in item:
            chat_items = item['chat']
        elif 'ak' in item:
            api_key = item['ak']
            api_key = cipher.decrypt(api_key.encode()).decode()
        elif 'context' in item:
            context = item['context']

    # Build message history for chat interaction with OpenAI
    msg = [{"role": "system", "content": context}]
    if chat_items is not None:
        for chat_item in chat_items:
            if 'user' in chat_item:
                msg.append({"role": "user", "content": chat_item['user']})
            if 'bot' in chat_item:
                msg.append({"role": "assistant", "content": chat_item['bot']})

    # Generate a response using OpenAI API
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(model=GPT_MODEL, messages=msg)
    ret = completion.choices[0].message.content

    return jsonify({"status": message, "last": ret})


# Define route to handle image generation requests
@app.route('/send_messagePic', methods=['POST'])
def send_messagePic():
    data = request.json
    message = data['message']
    msg = ""

    chat_items = None
    api_key = None
    context = None
    link = None
    for item in message:
        if 'chat' in item:
            msg_usr = item['chat']
        elif 'ak' in item:
            api_key = item['ak']
            api_key = cipher.decrypt(api_key.encode()).decode()
        elif 'context' in item:
            context = item['context']
        elif 'token' in item:
            link = item['token']

    # Build message history for generating images
    msg = [{"role": "system", "content": context}]
    msg.append({"role": "user", "content": msg_usr})
    client = OpenAI(api_key=api_key)
    response = client.images.generate(model=DALLE_MODEL, prompt=msg_usr)
    ret = response.data[0].url
    status = db.session.query(Link).filter(Link.token.like(link))
    cnt = status.count()
    status.delete()
    db.session.commit()
    return jsonify({"status": message, "last": ret})


# Define route to handle student access
@app.route('/<name>', methods=('GET', 'POST'))
def student(name=None):
    if name.endswith('§PIC§.html') or name.endswith('§PIC§'):
        token = name.replace('§PIC§.html', '')

        # Retrieve link from database
        status = db.session.query(Link).filter(Link.token.like(token))
        cnt = status.count()

        # Verify link exists for access and pass form and token to template
        if cnt == 1:
            form = cf.ChatPicForm()
            l = status.one()
            api_key = l.api_key.decode()
            context = l.context
            return render_template('chatpic.html', form=form, token=token, context=context, ak=api_key)
        else:
            return render_template('error.html')
    else:
        token = name.replace('.html', '')

        status = db.session.query(Link).filter(Link.token.like(token))
        cnt = status.count()

        # Verify access to chat and pass data to template
        if cnt == 1:
            form = cf.ChatForm()
            l = status.one()
            api_key = l.api_key.decode()
            context = l.context
            data = [{"role": "system", "content": context},
                    {"role": "last", "content": "---"},
                    {"role": "ak", "content": api_key}]
            return render_template('chat.html', form=form, data=data, context=context, ak=api_key)
        else:
            return render_template('error.html')


# Run the Flask app
if __name__ == '__main__':
    app.run()