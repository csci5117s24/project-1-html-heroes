import json
from os import environ as env
from flask import Flask, render_template, url_for, session, redirect, request
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import database
from database import get_db_cursor
import re
from datetime import datetime
import pytz 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
    user = session.get('user') is not None
    return render_template('index.html', user=user)
    # return render_template('index.html', pretty=json.dumps(session.get('user'), indent=4))

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
        event_end = request.form['event_end']
        image = request.files['event_image']
        if image:
            event_image_url = database.add_picture(image, session["user"]['sub'])
        else:
            event_image_url = None

        form_data = {
            "event_type": event_type,
            "event_name": event_name,
            "event_location": event_location,
            "event_date": event_date,
            "event_description": event_description,
            "event_image_url": event_image_url
        }

        print(form_data)
        database.add_event(event_type, event_name, event_location, event_date, event_description, event_image_url, event_end, session["user"]['sub'])
        return redirect(url_for('profile'))
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

@app.route('/update_event/<int:event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    if request.method == 'POST':
        event_type = request.form['event_type']
        event_name = request.form['event_name']
        event_location = request.form['event_location']
        event_date = request.form['event_date']
        event_description = request.form['event_description']
        event_end = request.form['event_end']
        event_image_url = request.form['event_image_url']

        form_data = {
            "event_type": event_type,
            "event_name": event_name,
            "event_location": event_location,
            "event_date": event_date,
            "event_description": event_description,
            "event_image_url": event_image_url
        }
        print(f'here is the form_data:{form_data}')
        database.update_event(event_id, event_type, event_name, event_location, event_date, event_description, event_image_url, event_end)
        return redirect(url_for('profile'))
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
        id_list = database.get_events_ids_created_by_user(session["user"]['sub'])
        print(id_list)
        add_or_not = event_id in id_list
        if add_or_not:
            event = database.get_event(event_id).get_json()['event']
            print(event)
            return render_template('update_event.html', event=event[0])
        else:
            return """
            <html>
                <head><title>Reject!</title></head>
                <body>
                <script>
                    alert('This event is not created by you. You can not update it!');
                    window.location = '/profile';
                </script>
                </body>
            </html>
            """


@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event(event_id):
    event = database.get_event(event_id).get_json()['event']
    user = session.get("user")
    if not user == None:
        #check if this event is in your system or not
        add_or_not = event_id in database.get_user_event_id(session["user"]['sub'])
    else:
        add_or_not = False

    if not user == None:
        #check if this event is created by you
        by_you = event_id in database.get_events_ids_created_by_user(session["user"]['sub'])
    else:
        by_you = False

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
        return render_template('specific_page.html', event=event[0], user=user, reviews=reviews, add_or_not=add_or_not, by_you=by_you)
    else:
        return render_template('index.html')

@app.route('/profile')
def profile():
    user = session.get("user")
    my_events = []
    pattern = r'\w{3}, (\d{2}) (\w{3}) (\d{4}) (\d{2}:\d{2}:\d{2}) GMT'  

    if not user == None:
        # Parse date, month, year and time from the string
        my_events = database.get_user_events(user['sub']).get_json()['events']
        for each in my_events:
            match = re.search(pattern, each['event_date'])
            date = match.group(1)  
            month = match.group(2) 
            year = match.group(3)  
            time = match.group(4)
            each["parse_time"]= {}
            each["parse_time"]["date"]=date
            each["parse_time"]["month"]=month  
            each["parse_time"]["year"]=year  
            each["parse_time"]["time"]=time
            # print(each["parse_time"])
            print(each)
    
        created_events = database.get_events_created_by_user(user['sub']).get_json()['event']
        for each in created_events:
            match = re.search(pattern, each['event_date'])
            date = match.group(1)  
            month = match.group(2) 
            year = match.group(3)  
            time = match.group(4)
            each["parse_time"]= {}
            each["parse_time"]["date"]=date
            each["parse_time"]["month"]=month  
            each["parse_time"]["year"]=year  
            each["parse_time"]["time"]=time
            # print(each["parse_time"])
        # print(my_events)
        # print(created_events)
        return render_template('profile.html', events=my_events, events2=created_events)
    else:
        return """
        <html>
            <head><title>Sign In Required</title></head>
            <body>
            <script>
                alert('Please sign in to view your schedule.');
                window.location = '/';
            </script>
            </body>
        </html>
        """


@app.route('/addEvent', methods=['GET', 'POST'])
def addEvent():
    if request.method == 'POST':
        event_id = request.form['event_id']
        database.add_user_event(session["user"]['sub'], event_id)
    elif request.args.get('event_id'):
        event_id = request.args.get('event_id')
        database.add_user_event(session["user"]['sub'], event_id)
        return ('', 204)    # return without reloading page
    return redirect(url_for('event', event_id=event_id))

@app.route('/find_events')
def find_events():
    user = session.get('user') is not None
    # return render_template('index.html', pretty=json.dumps(session.get('user'), indent=4))
    
    return render_template('index.html', user=user)
    
    # events = database.get_events(0, 10).get_json()['events']
    # return render_template('find_events.html', events=events)

@app.route('/api/google_calendar/<int:event_id>')
def api_google_calendar(event_id):

    # Parse start and end time
    event1 = database.get_event(event_id).get_json()['event'][0]
    start = event1['event_date']
    end = event1['event_end']
    location = event1['event_location']
    description = event1['event_description']
    event_name = event1['event_name']

    date_format = "%a, %d %b %Y %H:%M:%S %Z"
    parsed_date = datetime.strptime(start, date_format)
    formatted_start = parsed_date.strftime('%Y-%m-%dT%H:%M:%S')
    parsed_date = datetime.strptime(end, date_format)
    formatted_end = parsed_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    # print(start)
    # print(formatted_start)
    # print(end)
    # print(formatted_end)

    """Shows basic usage of the Google Calendar API.
    """
    user = session.get('user') is not None
    if user:
        token = database.get_user_token(session["user"]['sub']).get_json()['token'][0]
        
        # print("------")
        # print(token)
        # print("------")

        if token == None:
            token = {"token": "", 
                     "refresh_token": "", 
                     "token_uri": "", 
                     "client_id": "", 
                     "client_secret": "", 
                     "scopes": ["https://www.googleapis.com/auth/calendar"], 
                     "expiry": ""}
        else:
            token = token['token']
        
        credential = database.get_credential(1).get_json()['credential'][0]
        credential = credential['config']
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        creds = None
        creds = Credentials.from_authorized_user_info(token, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    credential, SCOPES
                )
                creds = flow.run_local_server(port=0)
            database.update_token(creds.to_json(), session["user"]['sub'])
        
        # add event
        try:
            service = build("calendar", "v3", credentials=creds)
            event = {
                'summary': event_name,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': formatted_start,
                    'timeZone': 'America/Chicago',
                },
                'end': {
                    'dateTime': formatted_end,
                    'timeZone': 'America/Chicago',
                },
                # 'recurrence': [
                #     'RRULE:FREQ=DAILY;COUNT=2'
                # ],
                # 'attendees': [
                #     {'email': 'lpage@example.com'},
                #     {'email': 'sbrin@example.com'},
                # ],
                # 'reminders': {
                #     'useDefault': False,
                #     'overrides': [
                #     {'method': 'email', 'minutes': 24 * 60},
                #     {'method': 'popup', 'minutes': 10},
                #     ],
                # },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print(f"An error occurred: {error}")
        return f"""
        <html>
            <head><title>Add successfully</title></head>
            <body>
            <script>
                alert('Add to Google Calendar successfully!');
                window.location = '/event/{event_id}';
            </script>
            </body>
        </html>
        """
    else:
        return f"""
        <html>
            <head><title>Sign In Required</title></head>
            <body>
            <script>
                alert('Please sign in to add event to Google Calender.');
                window.location = '/event/{event_id}';
            </script>
            </body>
        </html>
        """

@app.route('/new_user')
def new_user():
    return render_template('new_user.html')

### API Endpoints
@app.route('/api/events')
def api_events():
    if (request.args):
        name = request.args.get("eventName", "")
        date = request.args.get("eventDate", "")
        type = request.args.get("eventType", "")
        return database.get_filtered_events(name, date, type)
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

@app.route('/api/getMyEvents')
def getMyEvents():
    user = session.get("user")
    my_events = []
    if not user == None:
        my_events = database.get_user_events(user['sub']).get_json()['events']
    return my_events

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
        return redirect(url_for('new_user'))
    else:
        # check if user is different from the one in the database
        user = user['user'][0]
        if user['user_name'] != token['userinfo']['name'] or user['user_email'] != token['userinfo']['email'] or user['user_avatar'] != token['userinfo']['picture']:
            print('updating user')
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