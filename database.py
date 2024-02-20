""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor
from flask import jsonify
import datetime

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def add_event(event_type, event_name, event_location, event_date, event_description, event_image_url):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO event (event_type, event_name, event_location, event_date, event_description, event_image_url) values (%s, %s, %s, %s, %s, %s)", (event_type, event_name, event_location, event_date, event_description, event_image_url))
        print(f"Added event: {event_type}, {event_name}, {event_location}, {event_date}, {event_description}, {event_image_url}")

def add_user(user_id, user_name, user_email, user_avatar):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO users (user_id, user_name, user_email, user_avatar) values (%s, %s, %s, %s)", (user_id, user_name, user_email, user_avatar))
        print(f"Added user: {user_id}, {user_name}, {user_email}, {user_avatar}")

def add_user_event(user_id, event_id):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO my_events (user_id, event_id) values (%s, %s)", (user_id, event_id))
        print(f"Added user event: {user_id}, {event_id}")

def get_events(page = 0, events_per_page = 10):
    ''' note -- result can be used as list of dictionaries'''
    limit = events_per_page
    offset = page*events_per_page
    with get_db_cursor() as cur:
        cur.execute("select * from event order by event_id limit %s offset %s", (limit, offset))
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})

def get_event(event_id):
    with get_db_cursor() as cur:
        cur.execute("select * from event where event_id = %s", (event_id,))
        return jsonify({'event': [dict(x) for x in cur.fetchall()]})
    
def get_user_events(user_id):
    with get_db_cursor() as cur:
        cur.execute("select * from my_events where user_id = %s", (user_id,))
        user_events = [dict(x) for x in cur.fetchall()]
        event_ids = [event['event_id'] for event in user_events]
        if not event_ids == []:
            cur.execute("select * from event where event_id in %s", (tuple(event_ids),))            
            return jsonify({'events': [dict(x) for x in cur.fetchall()]})
        return jsonify({'events': []})

def get_user(user_id):
    with get_db_cursor() as cur:
        cur.execute("select * from users where user_id = %s", (user_id,))
        return jsonify({'user': [dict(x) for x in cur.fetchall()]})
    

# TODO: once duration is added, change from event_date to ending time
def get_all_future_events():
    with get_db_cursor() as cur:
        cur.execute("select * from event where event_date > current_timestamp")
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})
    
def get_upcoming_events():
    with get_db_cursor() as cur:
        cur.execute("select * from event where event_date < (current_timestamp + (2 * interval '1 day')) and event_date > current_timestamp")
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})
    
def get_week_events():
    with get_db_cursor() as cur:
        cur.execute("select * from event where event_date < (current_timestamp + (7 * interval '1 day')) and event_date > current_timestamp")
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})
    
def get_month_events():
    with get_db_cursor() as cur:
        cur.execute("select * from event where event_date < (current_timestamp + (1 * interval '1 month')) and event_date > current_timestamp")
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})
    
def get_filtered_events(name, date, type):
    with get_db_cursor() as cur:
        selectString = ""
        selectValues = []
        if (name != ""):
            if (selectString == ""):
                selectString += "event_name like %s"
            else:
                selectString += "and event_name like %s"
            selectValues.append(name + "%")
        if (date != ""):
            print(date)
            if (selectString == ""):
                selectString += "DATE(event_date) = DATE(%s)"
            else:
                selectString += "and DATE(event_date) = DATE(%s)"
            selectValues.append(date)
        if (type != ""):
            if (selectString == ""):
                selectString += "event_type like %s"
            else:
                selectString += "and event_type like %s"
            selectValues.append(type + "%")
        # if (groupName != ""):
        #     if (selectString != ""):
        #         selectString += "event_name like %s"
        #     else:
        #         selectString += "and event_name like %s"
        #     selectValues.append(name)
        cur.execute("select * from event WHERE " + selectString, tuple(selectValues))
            
        return jsonify({'events': [dict(x) for x in cur.fetchall()]})
