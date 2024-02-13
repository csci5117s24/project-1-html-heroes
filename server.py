from flask import Flask, render_template, url_for
import database

app = Flask(__name__)
with app.app_context():
    database.setup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_event')
def create_event():
    return render_template('create_event.html')

@app.route('/event/<int:event_id>')
def event(event_id):
    return render_template('event.html', event_id=event_id)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/find_events')
def find_events():
    return render_template('find_events.html')

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