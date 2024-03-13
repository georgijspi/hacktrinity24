
// Call this function when initializing the page or when opening the add event modal
fetchAndPopulateGroups();

function getDashboardData() {
    $.ajax({
        url: '/get-dashboard-data',
        type: 'GET',
        success: function(response) {
            // Update Groups
            var groupsList = $('#groupsList');
            groupsList.empty();
            response.groups.forEach(function(group) {
                var listItem = $('<li class="mb-2 flex justify-between items-center w-full cursor-pointer"></li>');
                listItem.append('<span class="flex-grow" onclick="showGroupDetailsModal(' + group.id + ')">' + group.name + '</span>');
                listItem.append('<button onclick="inviteToGroup(\'' + group.id + '\')" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded float-right">Invite</button>');
                groupsList.append(listItem);
            });

            // Update Friends List
            var friendsList = $('#friendsList');
            friendsList.empty();
            response.friends.forEach(function(friend) {
                friendsList.append('<li>' + friend.username + '</li>');
            });

            // Update Pending Requests
            var pendingList = $('#pendingRequestsList');
            pendingList.empty();
            response.pending_requests.forEach(function(request) {
                var listItem = $('<li class="mb-2 flex justify-between items-center"></li>');
                listItem.append(request.username);
                var buttons = $('<div></div>');
                buttons.append('<button onclick="acceptRequest(\'' + request.id + '\')" class="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded">Accept</button>');
                buttons.append('<button onclick="denyRequest(\'' + request.id + '\')" class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">Deny</button>');
                listItem.append(buttons);
                pendingList.append(listItem);
            });
        },
        error: function() {
            console.log('Error getting dashboard data.');
        }
    });
}

// Initial dashboard get and set interval for continuous updates
getDashboardData();
setInterval(getDashboardData, 5000);

function getFriendsNotInGroup(groupId) {
    $.ajax({
        url: '/get-friends-not-in-group/' + groupId,
        type: 'GET',
        beforeSend: function(xhr) {
            var csrftoken = $('meta[name="csrf-token"]').attr('content');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(response) {
            var friendListModal = $('#friendListModal');
            friendListModal.empty();
            response.friends.forEach(function(friend) {
                friendListModal.append('<li>' + friend.username +
                '<button onclick="addUserToGroup(\'' + friend.id + '\', \'' + groupId + '\')" class="ml-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded">Invite</button></li>');
            });
        },
        error: function() {
            alert('Error getting friends.');
        }
    });
}

// Function to show the modal for group details
function showGroupDetailsModal(groupId) {
    getGroupDetails(groupId);
    document.getElementById('groupDetailsModal').classList.remove('hidden');
}

// Function to close the group details modal
function closeGroupDetailsModal() {
    document.getElementById('groupDetailsModal').classList.add('hidden');
}

function getGroupDetails(groupId) {
    $.ajax({
        url: '/get-group-details/' + groupId,
        type: 'GET',
        success: function(response) {
            let foodEmojis = ['🍏', '🍔', '🍕', '🍣', '🍤', '🍩', '🍪', '🍉', '🍓', '🍒'];
            let content = `<p><strong>Name:</strong> ${response.name}</p>`;
            content += `<p><strong>Description:</strong> ${response.description}</p>`;
            content += `<p><strong>Chatroom Link:</strong> <a href="${response.chatroom_link}" target="_blank">Join Chat</a></p>`;

            // Display group members with random food emoji
            content += '<h4>Members:</h4><ul>';
            response.members.forEach(function(member) {
                let randomEmoji = foodEmojis[Math.floor(Math.random() * foodEmojis.length)];
                content += `<li>${randomEmoji} ${member.username}</li>`;
            });
            content += '</ul>';

            // Display events
            content += '<h4>Events:</h4><ul>';
            response.events.forEach(function(event) {
                content += `<li>${event.title} - ${event.description}</li>`;
            });
            content += '</ul>';
            
            $('#groupDetailsContent').html(content);
            // Set the group ID for the button
            $('#checkGroupAvailabilityBtn').attr('data-group-id', groupId);

            // Alternatively, directly attach the click event listener to the button here
            $('#checkGroupAvailabilityBtn').off('click').on('click', function() {
                fetchGroupAvailability(groupId); // Correctly use the groupId from this scope
            });
        },
        error: function() {
            alert('Error getting group details.');
        }
    });
}

function fetchAndPopulateGroups() {
fetch('/groups')
    .then(response => response.json())
    .then(data => {
    const select = document.getElementById('eventGroup');
    data.groups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.name;
        select.appendChild(option);
        });
    });
}

function fetchGroups() {
    var select = document.getElementById('eventGroup');
    if (!select) {
        console.error('Group select not found');
        return; // Exit if the select element is not found
    }
    fetch('/get-groups')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('eventGroup');
        select.innerHTML = '';
        data.groups.forEach(group => {
            const option = document.createElement('option');
            option.value = group.id;
            option.textContent = group.name;
            select.appendChild(option);
        });
    })
    .catch(error => console.error('Error getting groups:', error));
}

function fetchGroupAvailability(group_id, friend_id = null) {
    $.ajax({
        url: '/get-availability',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ group_id: group_id, friend_id: friend_id }),
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr('content'));
        },
        success: function(response) {
            renderNewTimetable(response.availability); // Use the new function here
        },
        error: function(xhr) {
            alert('Error fetching availability: ' + xhr.responseText);
        }
    });
}

function renderHeatmap(availability) {
    // Clear existing heatmap before rendering a new one
    calendar.getEvents().forEach(function(event) {
        if (event.extendedProps.isHeatmap) { // Assuming you mark heatmap events with an extendedProp
            event.remove();
        }
    });

    availability.forEach(slot => {
        var color = getHeatmapColor(slot.availability);
        // Assuming you can add background events to act as a heatmap
        calendar.addEvent({
            start: slot.date + 'T' + slot.time,
            end: new Date(slot.date + 'T' + slot.time).addHours(1).toISOString(), // This needs a utility function to add hours
            rendering: 'background',
            backgroundColor: color,
            isHeatmap: true // Custom property to identify heatmap events
        });
    });
}

Date.prototype.addHours = function(h) {
    this.setTime(this.getTime() + (h*60*60*1000));
    return this;
}


function getHeatmapColor(availability) {
    if (availability > 90) return 'rgba(0, 255, 0, 0.5)'; // Opaque green
    if (availability > 75) return 'rgba(255, 255, 0, 0.5)'; // Opaque yellow
    if (availability > 50) return 'rgba(255, 0, 0, 0.5)'; // Opaque red
    return 'rgba(255, 255, 255, 0.5)'; // Default color
}

// Assuming 'calendar' is initialized in the global scope for accessibility
var calendar;

function renderNewTimetable(availability) {
    // Check if the calendar instance exists. If it does, destroy it.
    if (calendar) {
        calendar.destroy();
    }

    // Re-select the calendar element
    var calendarEl = document.getElementById('calendar');

    // Re-initialize the calendar with possibly new configurations
    calendar = new FullCalendar.Calendar(calendarEl, {
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
        // Convert availability data into background events for heatmap
        events: availability.map(slot => ({
            start: slot.date + 'T' + slot.time,
            end: new Date(slot.date + 'T' + slot.time).addHours(1).toISOString(),
            rendering: 'background',
            backgroundColor: getHeatmapColor(slot.availability),
            allDay: false
        }))
    });

    calendar.render();
}
