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

@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event(event_id):
    event = database.get_event(event_id).get_json()['event']

    #fetch user_name based on user_id
    reviews = database.get_review(event_id).get_json()['reviews']
    for review in reviews:
        user_name = database.get_user(review['user_id']).get_json()['user'][0]['user_name']
        review['user_name'] = user_name

    if request.method == 'POST':
        print(request.form['review'], session["user"]['sub'])
        # I set rating as 3 star temporarily since the rating system is not done.
        database.add_review(event_id, session["user"]['sub'], 3, request.form['review'])
        return redirect(url_for('event', event_id=event_id))

    # # test
    # print(reviews)
    # print(event)
    if event:
        user = session.get('user') is not None
        return render_template('specific_page.html', event=event[0], user=user, reviews=reviews)
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
    return database.get_events()

@app.route('/api/events/<int:event_id>')
def api_event(event_id):
    return database.get_event(event_id)

@app.route('/api/users/<user_id>/events')
def api_user_events(user_id):
    return database.get_user_events(user_id)

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