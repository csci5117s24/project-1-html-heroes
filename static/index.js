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

const baseEventHtml = "<div class=\"pure-g event\"><div class=\"pure-u-1-4 event-image\"></div><div class=\"pure-u-1-2 event-text l-box\"></div><div class=\"pure-u-1-4 event-add l-box\"></div></div>"
// Might be possible to put all of these functions into one, might be harder to read though
function getUpcomingEvents() {
    changeActiveButton(this);
    const upcomingEvents = [];
    upcomingEvents.push(createEvent("Test club", "Starting soon", "Location", "Test event", "Event description for an upcoming event"));
    changeEvents(upcomingEvents);
}

function getWeekEvents() {
    changeActiveButton(this);
    const weekEvents = [];
    weekEvents.push(createEvent("Test club", "Next week", "Location", "Test event", "Event description for an event next week"));
    changeEvents(weekEvents);
}

function getMonthEvents() {
    changeActiveButton(this);
    const monthEvents = [];
    monthEvents.push(createEvent("Test club", "In a few weeks", "Location", "Test event", "Event description for an event in the next month"));
    changeEvents(monthEvents);
}

function getAllEvents() {
    changeActiveButton(this);
    const allEvents = [];
    allEvents.push(createEvent("Test club", "Starting soon", "Location", "Test event", "Event description for an upcoming event"));
    allEvents.push(createEvent("Test club", "Next week", "Location", "Test event", "Event description for an event next week"));
    allEvents.push(createEvent("Test club", "In a few weeks", "Location", "Test event", "Event description for an event in the next month"));
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

function createEvent(clubName, date, location, eventName, eventDesc) {
    const parser = new DOMParser();
    const newEvent = parser.parseFromString(baseEventHtml, 'text/html');
    const eventText = parser.parseFromString(clubName + " - " + date + "<br>" + location + "<br>" + eventName + "<br>" + eventDesc, 'text/html');
    newEvent.getElementsByClassName("event-image")[0].innerHTML = "<p>Image</p>";
    newEvent.getElementsByClassName("event-text")[0].innerHTML = eventText.documentElement.innerHTML;
    newEvent.getElementsByClassName("event-add")[0].innerHTML = "<p>Add event button</p>";
    return newEvent.documentElement.innerHTML;
}






