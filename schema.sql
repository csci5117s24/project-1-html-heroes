create table event (
    event_id serial primary key,
    event_type text not null,
    event_name text not null,
    event_location text not null,
    event_date timestamp not null,
    event_description text not null,
    event_image_url text null,
    event_create_at timestamp default current_timestamp
);

create table users (
    user_id text primary key,
    user_name text not null,
    user_email text not null
)

create table my_events (
    primary key (event_id, user_id),
    event_id integer references event(event_id) not null,
    user_id text references users(user_id) not null
)

-- command for new event
insert into event (event_type, event_name, event_location, event_date, event_description, event_image_url) 
values ('concert', 'Drake', 'US Bank', '2024-02-12 10:00:00', 'Concert with Drake', '')

-- command for new user
insert into users (user_id, user_name, user_email)
values ('123', 'John', 'test@gmail.com')

-- command for new event for user
insert into my_events (event_id, user_id)
values (1, '123')

-- commmand to get all events
select * from event

-- command to get all users
select * from users

-- command to get all event ids for specific user
select * from my_events where user_id = '123'

-- command to get all events from list of event ids
select * from event where event_id in (1, 2, 3)

