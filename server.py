from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/create_event')
def render_create_event():
    return render_template('create_event.html')

@app.route('/event/<int:event_id>')
def render_event(event_id):
    return render_template('event.html', event_id=event_id)

@app.route('/profile')
def render_profile():
    return render_template('profile.html')