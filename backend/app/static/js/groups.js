
function createGroup() {
    var groupName = document.getElementById('groupName').value;
    var description = document.getElementById('groupDescription').value;
    var chatroomLink = document.getElementById('chatroomLink').value;
    var csrftoken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
        url: '/create-group',
        type: 'POST',
        data: {
            'group_name': groupName,
            'description': description,
            'chatroom_link': chatroomLink
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(response) {
            alert(response.message);
            $('#groupName').val('');
            $('#groupDescription').val('');
            $('#chatroomLink').val('');
        },
        error: function(xhr, status, error) {
            // Improved error handling
            alert('Error creating group: ' + xhr.responseText);
        }
    });
}

function inviteToGroup(groupId) {
    showModal();
    fetchFriendsNotInGroup(groupId);
}

function addUserToGroup(userId, groupId) {
    var csrftoken = $('meta[name="csrf-token"]').attr('content');
    $.ajax({
        url: '/invite-to-group',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ user_id: userId, group_id: groupId }),
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(response) {
            alert(response.message);
            closeModal();
            location.reload();
        },
        error: function(xhr) {
            alert('Error adding user to group: ' + xhr.responseText);
        }
    });
}

// Function to show the modal
function showModal() {
    document.getElementById('inviteModal').classList.remove('hidden');
}

// Function to close the modal
function closeModal() {
    document.getElementById('inviteModal').classList.add('hidden');
}