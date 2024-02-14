from os import environ as env
from flask import Flask, render_template, url_for, session, redirect, request
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import database

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

with app.app_context():
    database.setup()

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


@app.route('/')
def index():
    return render_template('index.html')

# Specific_page is not complete yet
@app.route('/specific_page')
def render_specific_page():
    return render_template('specific_page.html')

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_type = request.form['event_type']
        event_name = request.form['event_name']
        event_location = request.form['event_location']
        event_date = request.form['event_date']
        event_description = request.form['event_description']
        event_image_url = request.form['event_image_url']

        form_data = {
            "event_type": event_type,
            "event_name": event_name,
            "event_location": event_location,
            "event_date": event_date,
            "event_description": event_description,
            "event_image_url": event_image_url
        }

        print(form_data)
        database.add_event(event_type, event_name, event_location, event_date, event_description, event_image_url)
        return render_template('profile.html')
    return render_template('create_event.html')

@app.route('/event/<int:event_id>')
def event(event_id):
    event = database.get_event(event_id).get_json()['event']
    if event:
        return render_template('event.html', event=event[0])
    else:
        return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/find_events')
def find_events():
    events = database.get_events(0, 10).get_json()['events']
    return render_template('find_events.html', events=events)

### API Endpoints
@app.route('/api/events')
def api_events():
    return database.get_events()

@app.route('/api/events/<int:event_id>')
def api_event(event_id):
    return database.get_event(event_id)

@app.route('/api/users/<user_id>/events')
def api_user_events(user_id):
    return database.get_user_events(user_id)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )