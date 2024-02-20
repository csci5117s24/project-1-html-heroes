window.onload = function() {
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

const baseEventHtml = "<a style=\"color: inherit; text-decoration: none;\">" +
    "<div class=\"pure-g event card container\">" +
    "<div class=\"pure-u-1-4 event-image\"></div>" +
    "<div class=\"pure-u-1-2 event-text l-box\"></div>" +
    "<div class=\"pure-u-1-4 event-add l-box\"></div></div></a>";

const rootUrl = "http://localhost:5000";

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
    const eventText = "<h2>" + eventData.event_type + "</h2><p>" + eventData.event_date + "</p><p>" + eventData.event_location + "</p><p>" + eventData.event_name + "</p><p>" + eventData.event_description + "</p>";
    newEvent.getElementsByClassName("event-image")[0].innerHTML = "<img src=" + eventData.event_image_url + ">";
    newEvent.getElementsByClassName("event-text")[0].innerHTML = eventText;
    newEvent.getElementsByClassName("event-add")[0].innerHTML = "<p>Add event button</p>";
    newEvent.querySelector("a").setAttribute("href", rootUrl + "/event/" + eventData.event_id);
    return newEvent.documentElement.innerHTML;
}
