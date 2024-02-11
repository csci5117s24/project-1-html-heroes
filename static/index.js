window.onload = function() {
    upcomingButton = document.getElementById("upcoming");
    weekButton = document.getElementById("week");
    monthButton = document.getElementById("month");
    allEventsButton = document.getElementById("all-events");
    
    upcomingButton.addEventListener("click", getUpcomingEvents);
    weekButton.addEventListener("click", getWeekEvents);
    monthButton.addEventListener("click", getMonthEvents);
    allEventsButton.addEventListener("click", getAllEvents);
}

// Might be possible to put all of these functions into one, might be harder to read though
function getUpcomingEvents() {
    changeActiveButton(this);
    const upcomingEvents = "<p>Upcoming events</p>";
    changeEvents(upcomingEvents);
}

function getWeekEvents() {
    changeActiveButton(this);
    const weekEvents = "<p>Week events</p>";
    changeEvents(weekEvents);
}

function getMonthEvents() {
    changeActiveButton(this);
    const monthEvents = "<p>Month events</p>";
    changeEvents(monthEvents);
}

function getAllEvents() {
    changeActiveButton(this);
    const allEvents = "<p>All events</p>";
    changeEvents(allEvents);
}

function changeActiveButton(newActive) {
    activeButton = document.getElementsByClassName("pure-button-active");
    activeButton[0].classList.remove("pure-button-active");
    newActive.classList.add("pure-button-active");
}

function changeEvents(newEvents) {
    events = document.getElementById("events");
    events.innerHTML = newEvents;
}