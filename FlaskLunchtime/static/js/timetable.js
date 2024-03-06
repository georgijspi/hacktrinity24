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
    // Pre-fill the start and optionally end date
    document.getElementById('eventStart').value = info.dateStr;
    const endDate = new Date(info.dateStr);
    endDate.setHours(endDate.getHours() + 1);
    document.getElementById('eventEnd').value = endDate.toISOString().split('.')[0];
    // Fetch groups to populate the dropdown
    fetchGroups();

    // Show modal
    document.getElementById('addEventModal').classList.remove('hidden');
}


function closeAddEventModal() {
    document.getElementById('addEventModal').classList.add('hidden');
}

document.getElementById('addEventForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission
    
    const eventData = {
        title: document.getElementById('eventTitle').value,
        start: document.getElementById('eventStart').value,
        end: document.getElementById('eventEnd').value,
        group_id: document.getElementById('eventGroup').value,
    };
    
    addEvent(eventData);
});

function addEvent(eventData) {
    $.ajax({
        url: '/add-event',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(eventData),
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr('content'));
        },
        success: function(response) {
            alert(response.message);
            closeAddEventModal();
            // Optionally refresh the calendar or page
        },
        error: function(xhr) {
            alert('Error adding event: ' + xhr.responseText);
        }
    });
}