const userEvents = [];
let rootUrl;
let userLoggedIn;
const baseEventHtml =
  '<div class="event">' +
  '<a style="color: inherit; text-decoration: none;" class="outer-button">' +
  '<div class="event card container pure-g">' +
  '<img class="event-image l-box pure-u-1-4">' +
  '<div class="event-text l-box pure-u-1-2"></div></div></a>' +
  '<button class="pure-button event-add l-box inner-button"></button></div>';

window.onload = function () {
  rootUrl = window.location.origin;
  // loadUserEvents();
  upcomingButton = document.getElementById("upcoming");
  weekButton = document.getElementById("week");
  monthButton = document.getElementById("month");
  allEventsButton = document.getElementById("all-events");
  searchButton = document.getElementById("event-search");

  upcomingButton.addEventListener("click", () =>
    getEvents("upcoming", upcomingButton)
  );
  weekButton.addEventListener("click", () => getEvents("week", weekButton));
  monthButton.addEventListener("click", () => getEvents("month", monthButton));
  allEventsButton.addEventListener("click", () =>
    getEvents("future", allEventsButton)
  );
  searchButton.addEventListener("click", searchEvents);
  document.getElementById("upcoming").click();
  loadUserEvents();
};

// function setLoginState() {
//   console.log(loggedIn);
//   if (loggedIn) {
//     userLoggedIn = true;
//   } else {
//     userLoggedIn = false;
//   }
// }

async function loadUserEvents() {
  const response = await fetch(rootUrl + "/api/getMyEvents");
  const json = await response.json();
  console.log(json);
  for (let i = 0; i < json.length; i++) {
    // userEvents.push(json.events[i].event_id);
    userEvents.push(json[i].event_id);
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
  const eventType = document.getElementById("event-type").value;
  const eventStart = document.getElementById("event-start").value;
  const eventEnd = document.getElementById("event-end").value;

  let query = "?";
  if (eventName != "") {
    query +=
      query == "?" ? "eventName=" + eventName : "&eventName=" + eventName;
  }
  if (eventType != "") {
    query +=
      query == "?" ? "eventType=" + eventType : "&eventType=" + eventType;
  }
  if (eventStart != "") {
    query +=
      query == "?" ? "eventStart=" + eventStart : "&eventStart=" + eventStart;
  }
  if (eventEnd != "") {
    query += query == "?" ? "eventEnd=" + eventEnd : "&eventEnd=" + eventEnd;
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
  if (newEvents.length == 0) {
    events.innerHTML = "<h1> No Events Found </h1>";
  }
}

function createEvent(eventData) {
  const parser = new DOMParser();
  const newEvent = parser.parseFromString(baseEventHtml, "text/html");
  const eventDescription =
    eventData.event_description.length > 150
      ? eventData.event_description.substring(0, 150) + "..."
      : eventData.event_description;
  const eventText =
    "<h2 style='font-family:&quot;Chakra Petch&quot;, sans-serif; margin-bottom: 5px; font-size:36px'>" +
    eventData.event_name +
    "</h2>" +
    "<p style='background-color: #18d950; border-radius: 10px; display: inline-block; padding: 5px 10px; margin-top: 5px;'>" +
    eventData.event_type +
    "</p>" +
    "<p style='margin-top: 5px; font-weight: bold'>" +
    "<span>🕑&nbsp;&nbsp;</span>" +
    eventData.event_date +
    " - " +
    eventData.event_end +
    "</p><p style='font-weight: bold'>" +
    "<span>📍&nbsp;&nbsp;</span>" +
    eventData.event_location +
    "</p><p style='font-family:&quot;Chakra Petch&quot;, sans-serif;'>" +
    eventDescription +
    "</p>";
  if (eventData.event_image_url) {
    newEvent
      .getElementsByClassName("event-image")[0]
      .setAttribute("src", eventData.event_image_url);
  } else {
    // TODO: add default image once we have decided on one
    newEvent
      .getElementsByClassName("event-image")[0]
      .setAttribute("src", "static/event-default-img-med.png");
  }
  newEvent.getElementsByClassName("event-text")[0].innerHTML = eventText;
  if (userEvents.includes(eventData.event_id)) {
    newEvent.getElementsByClassName("event-add")[0].innerHTML =
      "<p>Event added to schedule</p>";
  } else {
    newEvent.getElementsByClassName("event-add")[0].innerHTML =
      "<p>Add event to schedule</p>";
    newEvent
      .querySelector("button")
      .setAttribute("onClick", "addToSchedule(" + eventData.event_id + ")");
  }
  newEvent.querySelector("button").setAttribute("id", eventData.event_id);
  newEvent
    .querySelector("a")
    .setAttribute("href", rootUrl + "/event/" + eventData.event_id);
  return newEvent.documentElement.innerHTML;
}

function addToSchedule(eventId) {
  if (loggedIn) {
    fetch(rootUrl + "/addEvent?event_id=" + eventId);
    document.getElementById(eventId).innerHTML =
      "<p>Event added to schedule</p>";
    userEvents.push(eventId);
    // Once event has been added to schedule the button should do nothing
    document.getElementById(eventId).setAttribute("onClick", "");
  } else {
    alert("Please sign in to add event to your schedule.");
  }
}

async function addGoogleCalendar(eventId) {
  // console.log(eventId)
  const response = await fetch(rootUrl + "/api/google_calendar/" + eventId);
  const json = await response.json();
  condition = json.add_or_not;
  // console.log(json.add_or_not)
  if (condition) {
    alert("Add successfully!!");
  } else {
    alert("Please sign in to add event to Google Calendar");
  }
}
