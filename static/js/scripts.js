$(document).ready(function() {

    $.get('/get_user_ids', function(data) {
        $( "#username" ).autocomplete({ source: data["username"] });
    });
});
