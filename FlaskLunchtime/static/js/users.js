
function addFriend(username) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr('content'));
            }
        }
    });
    $.ajax({
        url: '/add-friend',
        type: 'POST',
        data: {username: username},
        success: function(response) {
            alert(response.message);
            $('#friendUsername').val('');
        },
        error: function(response) {
            alert('Error sending friend request.');
        }
    });
}


function acceptRequest(requestId) {
    var csrftoken = $('meta[name="csrf-token"]').attr('content');
    $.ajax({
        url: '/accept-request/' + requestId,
        type: 'POST',
        data: {},
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(response) {
            alert(response.message);
            location.reload();
        },
        error: function(xhr, status, error) {
            alert('Error accepting request: ' + xhr.responseText);
        }
    });
}

function denyRequest(requestId) {
    var csrftoken = $('meta[name="csrf-token"]').attr('content');
    $.ajax({
        url: '/deny-request/' + requestId,
        type: 'POST',
        data: {},
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(response) {
            alert(response.message);
            location.reload();
        },
        error: function(xhr, status, error) {
            alert('Error accepting request: ' + xhr.responseText);
        }
    });
}

function updateFriendRequestButton(username, disabled = true) {
    const button = $(`button[data-username="${username}"]`);
    if (disabled) {
        button.attr('disabled', true);
        button.text('Request Sent');
    } else {
        button.removeAttr('disabled');
        button.text('Add Friend');
    }
}