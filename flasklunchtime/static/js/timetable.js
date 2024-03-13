document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        slotMinTime: '08:00:00',
        slotMaxTime: '19:00:00',
        allDaySlot: false,
        nowIndicator: true,
        expandRows: true,
        dateClick: function(info) {
            openAddEventModal(info);
        },
        eventSources: [
            {
                url: '/events',
                method: 'GET',
                extraParams: {
                    // Any extra parameters you might want to pass to the server
                    // To be filled in later, ie; styling, etc.
                },
                failure: function() {
                    alert("There was an error while fetching events!");
                },
            }
        ]
    });
    calendar.render();

    // Initialize date and time pickers
    flatpickr(".datetimepicker", {
        enableTime: true,
        dateFormat: "Y-m-d\\TH:i:S",
        time_24hr: true,
    });

    // Fetch and populate groups
    fetchGroups();

});

function openAddEventModal(info) {
    const startInput = document.getElementById('eventStart');
    if (!startInput) {
        console.error('eventStart input not found');
        return; // Exit the function if element is not found
    }
    startInput.value = info.dateStr;

    const endDate = new Date(info.dateStr);
    endDate.setHours(endDate.getHours() + 1);
    document.getElementById('eventEnd').value = endDate.toISOString().split('.')[0];

    fetchGroups();
    document.getElementById('eventModal').classList.remove('hidden');
}

function closeAddEventModal() {
    document.getElementById('eventModal').classList.add('hidden');
}

document.getElementById('addEventForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission

    // Serialize form data
    var eventData = {
        title: document.getElementById('eventTitle').value,
        start: document.getElementById('eventStart').value,
        end: document.getElementById('eventEnd').value,
        group_id: document.getElementById('eventGroup').value,
    };

    // AJAX request to add event
    addEvent(eventData);
});

function addEvent(eventData) {
    // Adjust AJAX call as needed
    // Example:
    $.ajax({
        url: '/add-event',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(eventData),
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr('content')); // CSRF token
        },
        success: function(response) {
            alert('Event added successfully!');
            closeAddEventModal();
            // Optionally, refresh the calendar or specific part of the page
        },
        error: function(xhr) {
            alert('Error adding event: ' + xhr.responseText);
        }
    });
}

function changeTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(function(div) {
        div.classList.add('hidden');
    });
    // Show the selected tab content
    document.getElementById(tabName).classList.remove('hidden');

    // Update tab headers style
    document.getElementById('createEventTab').classList.toggle('text-blue-500 border-blue-500', tabName === 'createEvent');
    document.getElementById('checkAvailabilityTab').classList.toggle('text-blue-500 border-blue-500', tabName === 'checkAvailability');
}
