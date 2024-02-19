import json
from os import environ as env
from flask import Flask, render_template, url_for, session, redirect, request
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import database
from database import get_db_cursor

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

with app.app_context():
    database.setup()

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
    return render_template('index.html', pretty=json.dumps(session.get('user'), indent=4))

# @app.route('/specific_page')
# def render_specific_page():
#     return render_template('specific_page.html')

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
    if session.get('user') is None:
        return """
        <html>
            <head><title>Sign In Required</title></head>
            <body>
            <script>
                alert('Please sign in to create a event.');
                window.location = '/';
            </script>
            </body>
        </html>
        """
    else:
        return render_template('create_event.html')

@app.route('/event/<int:event_id>')
def event(event_id):
    event = database.get_event(event_id).get_json()['event']
    print(event)
    if event:
        return render_template('specific_page.html', event=event[0])
    else:
        return render_template('index.html')

@app.route('/profile')
def profile():
    user = session.get("user")
    my_events = []
    if not user == None:
        my_events = database.get_user_events(user['sub']).get_json()['events']
    return render_template('profile.html', events=my_events)

@app.route('/find_events')
def find_events():
    events = database.get_events(0, 10).get_json()['events']
    return render_template('find_events.html', events=events)

### API Endpoints
@app.route('/api/events')
def api_events():
    if (request.args):
        name = request.args.get("eventName", "")
        date = request.args.get("eventDate", "")
        groupType = request.args.get("groupType", "")
        groupName = request.args.get("groupName", "")
        return database.get_filtered_events(name, date, groupType, groupName)
    return database.get_events()

@app.route('/api/events/<int:event_id>')
def api_event(event_id):
    return database.get_event(event_id)

@app.route('/api/users/<user_id>/events')
def api_user_events(user_id):
    return database.get_user_events(user_id)

@app.route('/api/events/future')
def api_future_events():
    return database.get_all_future_events()

@app.route('/api/events/upcoming')
def api_upcoming_events():
    return database.get_upcoming_events()

@app.route('/api/events/week')
def api_week_events():
    return database.get_week_events()

@app.route('/api/events/month')
def api_month_events():
    return database.get_month_events()

@app.route('/search')
def search():
    query = request.args.get('query', '')
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM event WHERE event_name ILIKE %s ORDER BY event_date DESC", (f'%{query}%',))
        events = cur.fetchall() or []
    return render_template('search_results.html', events=events)

# Auth0 routes
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token['userinfo']
    
    user = database.get_user(token['userinfo']['sub']).get_json()
    if user['user'] == []:
        # add user to the database
        auth_info = token['userinfo']
        database.add_user(auth_info['sub'], auth_info['name'], auth_info['email'], auth_info['picture'])
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