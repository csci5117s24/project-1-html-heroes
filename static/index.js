let userEvents;
let rootUrl;
const baseEventHtml = "<div class=\"event\">" +
    "<a style=\"color: inherit; text-decoration: none;\" class=\"outer-button\">" +
    "<div class=\"event card container pure-g\">" +
    "<img class=\"event-image l-box pure-u-1-4\">" +
    "<div class=\"event-text l-box pure-u-1-2\"></div></div></a>" +
    "<button class=\"pure-button event-add l-box inner-button\"></button></div>";


window.onload = function() {
    rootUrl = window.location.origin;
    loadUserEvents();
    upcomingButton = document.getElementById("upcoming");
    weekButton = document.getElementById("week");
    monthButton = document.getElementById("month");
    allEventsButton = document.getElementById("all-events");
    searchButton = document.getElementById("event-search");
    
    upcomingButton.addEventListener("click", () => getEvents("upcoming", upcomingButton));
    weekButton.addEventListener("click", () => getEvents("week", weekButton));
    monthButton.addEventListener("click", () => getEvents("month", monthButton));
    allEventsButton.addEventListener("click", () => getEvents("future", allEventsButton));
    searchButton.addEventListener("click", searchEvents);
    document.getElementById("upcoming").click();
}

async function loadUserEvents() {
    const response = await fetch(rootUrl + "/api/getMyEvents");
    const json = await response.json();
    if (json.length === 0) {
        userEvents = [];
    } else {
        userEvents = json.events;
    }
}

async function getEvents(type, activeButton) {
    const response = await fetch(rootUrl + "/api/events/" + type);
    const events = (await response.json()).events;
    changeActiveButton(activeButton);
    const upcomingEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        upcomingEvents.push(newEvent);
    }
    changeEvents(upcomingEvents);

    if (type === "future") {
        document.getElementById("event-filter").hidden = false;
    } else {
        document.getElementById("event-filter").hidden = true;
    }
}

function searchEvents() {
    const eventName = document.getElementById("event-name").value;
    const eventDate = document.getElementById("event-date").value;
    const eventType = document.getElementById("event-type").value;

    let query = "?";
    if (eventName != "") {
        query += (query == "?") ? "eventName=" + eventName : "&eventName=" + eventName;
    }
    if (eventDate != "") {
        query += (query == "?") ? "eventDate=" + eventDate : "&eventDate=" + eventDate;
    }
    if (eventType != "") {
        query += (query == "?") ? "eventType=" + eventType : "&eventType=" + eventType;
    }
    filterEvents(query);
}

async function filterEvents(query) {
    const response = await fetch(rootUrl + "/api/events" + query);
    const events = (await response.json()).events;
    const upcomingEvents = [];
    for (let i = 0; i < events.length; i++) {
        const newEvent = createEvent(events[i]);
        upcomingEvents.push(newEvent);
    }
    changeEvents(upcomingEvents);
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
    const eventText = "<h2>" + eventData.event_name + "</h2><p>" + eventData.event_date + "</p><p>" + eventData.event_location + "</p><p>" + eventData.event_type + "</p><p>" + eventData.event_description + "</p>";
    if (eventData.event_image_url) {
        newEvent.getElementsByClassName("event-image")[0].setAttribute("src", eventData.event_image_url);
    }
    newEvent.getElementsByClassName("event-text")[0].innerHTML = eventText;
    newEvent.getElementsByClassName("event-add")[0].innerHTML = "Add event to schedule"
    newEvent.querySelector("button").setAttribute("onClick", "addToSchedule()");
    newEvent.querySelector("a").setAttribute("href", rootUrl + "/event/" + eventData.event_id);
    return newEvent.documentElement.innerHTML;
}


function addToSchedule() {
    console.log("adding event to schedule")
}