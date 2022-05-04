$(document).ready(function() {
    if(localStorage.getItem('hidden_status') == 'visible') {
        $('#history-container').slideDown(0);
    } else if (localStorage.getItem('hidden_status') == null) {
        localStorage.setItem('hidden_status', 'hidden');
    }
});

$('#toggle-container').on('click', function() {
    hidden_status = localStorage.getItem('hidden_status');
    if(hidden_status == 'hidden') {
        $('#history-container').slideDown(400);
        localStorage.setItem('hidden_status', 'visible');
    } else if (hidden_status == 'visible') {
        $('#history-container').slideUp(400);
        localStorage.setItem('hidden_status', 'hidden');
    }
});

function add_history_item(table_row_id) {

    let values = []
    let row = document.getElementById(table_row_id);
    $(row).children("td").each(function() {
        values.push($(this).text());
    });

    $.post('/add_destination', {
        'coordinate-type':values[0],
        'nickname':values[1],
        'latitude':values[2].toString(),
        'longitude':values[3].toString(),
        'from_history':'yes'
    }).then(function() {
        location.reload();
    });
}

function remove_history_item(table_row_id) {

    $.post('/remove_history_destination', {
        'id':table_row_id
    }).then(function() {
        $('#' + table_row_id).hide(400, function(){ $('#' + table_row_id).remove(); }).then(function() {
            location.reload()
        });
    });
}