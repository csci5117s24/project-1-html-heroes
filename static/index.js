window.onload = function() {
    upcomingButton = document.getElementById("upcoming");
    weekButton = document.getElementById("week");
    monthButton = document.getElementById("month");
    allEventsButton = document.getElementById("all-events");
    
    upcomingButton.addEventListener("click", getUpcomingEvents);
    weekButton.addEventListener("click", getWeekEvents);
    monthButton.addEventListener("click", getMonthEvents);
    allEventsButton.addEventListener("click", getAllEvents);
    document.getElementById("upcoming").click();
}

const baseEventHtml = "<a style=\"color: inherit; text-decoration: none;\">" +
    "<div class=\"pure-g event card container\">" +
    "<div class=\"pure-u-1-4 event-image\"></div>" +
    "<div class=\"pure-u-1-2 event-text l-box\"></div>" +
    "<div class=\"pure-u-1-4 event-add l-box\"></div></div></a>";

const rootUrl = "http://localhost:5000";

async function getUpcomingEvents() {
    const response = await fetch(rootUrl + "/api/events/upcoming");
    const events = (await response.json()).events;
    console.log(events)
    changeActiveButton(this);
    const upcomingEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        upcomingEvents.push(newEvent);
    }
    changeEvents(upcomingEvents);
}

async function getWeekEvents() {
    const response = await fetch(rootUrl + "/api/events/week");
    const events = (await response.json()).events;
    changeActiveButton(this);
    const weekEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        weekEvents.push(newEvent);
    }
    changeEvents(weekEvents);
}

async function getMonthEvents() {
    const response = await fetch(rootUrl + "/api/events/month");
    const events = (await response.json()).events;
    changeActiveButton(this);
    const monthEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        monthEvents.push(newEvent);
    }
    changeEvents(monthEvents);
}

async function getAllEvents() {
    const response = await fetch(rootUrl + "/api/events/future");
    const events = (await response.json()).events;
    changeActiveButton(this);
    const allEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        allEvents.push(newEvent);
    }
    changeEvents(allEvents);
}

function changeActiveButton(newActive) {
    activeButton = document.getElementsByClassName("pure-button-active");
    activeButton[0].classList.remove("pure-button-active");
    newActive.classList.add("pure-button-active");
}

function changeEvents(newEvents) {
    events = document.getElementById("events");
    events.innerHTML = "";
    for (let i = 0; i < newEvents.length; i++) {
        events.innerHTML += newEvents[i];
    }
}

function createEvent(eventData) {
    const parser = new DOMParser();
    const newEvent = parser.parseFromString(baseEventHtml, 'text/html');
    const eventText = parser.parseFromString(eventData.event_type + " - " + eventData.event_date + "<br>" + eventData.event_location + "<br>" + eventData.event_name + "<br>" + eventData.event_description, 'text/html');
    newEvent.getElementsByClassName("event-image")[0].innerHTML = "<img src=" + eventData.event_image_url + ">";
    newEvent.getElementsByClassName("event-text")[0].innerHTML = eventText.documentElement.innerHTML;
    newEvent.getElementsByClassName("event-add")[0].innerHTML = "<p>Add event button</p>";
    newEvent.querySelector("a").setAttribute("href", rootUrl + "/event/" + eventData.event_id);
    return newEvent.documentElement.innerHTML;
}






