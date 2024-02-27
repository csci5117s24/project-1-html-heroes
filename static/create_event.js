window.onload = function() {
    let input = document.getElementById("stacked-event-location");
    let autocomplete = new google.maps.places.Autocomplete(input);
}

function validateTimes() {
    var start = document.getElementById("stacked-event-time").value;
    var end = document.getElementById("stacked-event-end").value;

    if (start >= end) {
        alert("End time must be greater than start time.");
        return false;
    }

    return true;
}
