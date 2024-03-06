
// Call this function when initializing the page or when opening the add event modal
fetchAndPopulateGroups();

function fetchDashboardData() {
    $.ajax({
        url: '/fetch-dashboard-data',
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
            console.log('Error fetching dashboard data.');
        }
    });
}

// Initial dashboard fetch and set interval for continuous updates
fetchDashboardData();
setInterval(fetchDashboardData, 5000);

function fetchFriendsNotInGroup(groupId) {
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
            alert('Error fetching friends.');
        }
    });
}

// Function to show the modal for group details
function showGroupDetailsModal(groupId) {
    fetchGroupDetails(groupId);
    document.getElementById('groupDetailsModal').classList.remove('hidden');
}

// Function to close the group details modal
function closeGroupDetailsModal() {
    document.getElementById('groupDetailsModal').classList.add('hidden');
}

function fetchGroupDetails(groupId) {
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
        },
        error: function() {
            alert('Error fetching group details.');
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
    .catch(error => console.error('Error fetching groups:', error));
}