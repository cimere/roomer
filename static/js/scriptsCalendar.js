// TODO:
// 1. use UNIX time: DONE
// 2. check overlapping on all day: DONE
// 3. default su week: DONE
// 4. recursive events
// 5. only creator or admin can remove his events

$(document).ready(function() {

    $( "#until" ).datepicker({ dateFormat: "dd-mm-yy", minDate: 0, maxDate: "+6M" });


    $("#radioDiv").click(function() {

        var recursive = false;
        var selected = $("#radioDiv input[type='radio']:checked");
        if (selected.length > 0)
            repeat = selected.val();
        if (repeat == "never") {
            $('#until').prop('disabled', true);
            recursive = false;
        } else {
            $('#until').prop('disabled', false);
            recursive = true;
        }
    });

    var room_name = $('span.room_name').text()
    var user = $('span.user').text();

    // var date = new Date();
    // var d = date.getDate();
    // var m = date.getMonth();
    // var y = date.getFullYear();
    // console.log(Date(y, m, d, 10, 30))
    // console.log(Date.parse(Date(y, m, d, 10, 30)))

    var calendar = $('#calendar').fullCalendar({

        // options

        defaultView: 'agendaWeek',
        weekends: false, // will hide Saturdays and Sundays
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        selectable: true,
        selectHelper: true,

        // callbacks

        select: function(start, end, allDay) {
            
            // TODO: repeating events
            // Create a dummy even Object to check overlapping events
            var dummyEvent = new Object();
            dummyEvent.start = start;
            dummyEvent.end = end;
            if (!isOverlapping(dummyEvent)) {
                $( "#dialog-insert" ).dialog({
                    resizable: false,
                    modal: true,
                    buttons: {
                                "Inserisci": function() {
                                    var event_title = $('#title').val();
                                    var until = $('#until').val();
                                    // create event array
                                    var event = {
                                                title: event_title,
                                                user: user,
                                                start: start,
                                                end: end,
                                                allDay: allDay
                                    }
                                    event["id"] = createID(event);
                                    console.log(user+" is inserting a new event called "+event_title+" recursive "+repeat+" until "+until);
                                    if (event_title && until) {
                                        // repeat render and post for each event in array
                                        calendar.fullCalendar('renderEvent',
                                            event,
                                            true // make the event "stick"
                                        );
                                        // Insert in mongoDB
                                        $.post('/insert_event', 
                                            {
                                                id: event.id,
                                                room: room_name,
                                                title: event_title,
                                                user: user,
                                                start: Date.parse(start)/1000, // to UNIX format
                                                end: Date.parse(end)/1000,
                                                allDay: allDay
                                            }, 
                                            function() {
                                                console.log(user + " created event id " + event["id"]);
                                            }
                                        );
                                    }
                                    $("#dialog-insert").dialog( "close" );
                                }
                             }
                })
            } else {
                calendar.fullCalendar('unselect');
            }
        },
        eventClick: function(calEvent, jsEvent, view) {

            $( "#dialog-update" ).dialog({
                resizable: false,
                modal: true,
                buttons: {
                            "Modifica": function() {
                                var new_event_title = $( "#new-title" ).val()
                                if (new_event_title) {
                                    calEvent.title = new_event_title;
                                    calendar.fullCalendar('updateEvent',calEvent);
                                    postUpdateToServer(room_name, calEvent);
                                }
                                $("#dialog-update").dialog( "close" );
                            },
                            "Rimuovi": function() {
                                id = calEvent._id;
                                calendar.fullCalendar('removeEvents', id)
                                $("#dialog-update").dialog( "close" );
                                // check userl
                                $.post('/remove_event', {id: id, room: room_name},
                                    function() {
                                        console.log(id+" event deleted")
                                    }
                                );
                            }
                         }
            })
        },
        eventResize: function(calEvent, dayDelta, minuteDelta, revertFunc) {
            // console.log('user is resizing event '+calEvent.id);
            // console.log('start: '+calEvent.start+'\nend: '+calEvent.end);
            if (isOverlapping(calEvent)) {
                revertFunc();
            } else {
                postUpdateToServer(room_name, calEvent);
            }
        },
        eventDrop: function(calEvent, dayDelta, minuteDelta, allDay, revertFunc) {
            if (isOverlapping(calEvent)) {
                revertFunc();
            } else {
                postUpdateToServer(room_name, calEvent, allDay);
            }
        },
        eventRender: function(event, element) {
            element.find('.fc-event-title').append("<br/>" + event.user); 
        },
        editable: true,
        eventSources: [
            {
                url: '/get_events/'+room_name,
                error: function() {
                    alert('there was an error while fetching events!');
                }
            }
        ]

    })

    // Helper functions

    // Avoid overlapping
    // http://code.google.com/p/fullcalendar/issues/detail?id=396
    // http://stackoverflow.com/questions/2369683/is-there-a-way-to-prevent-overlapping-events-in-jquery-fullcalendar
    function isOverlapping(event){
        // TODO: check overlap on all day event
        // "calendar" on line below should ref the element on which fc has been called 
        if (Date.parse(event.start) == Date.parse(event.end)) { // all day event
            msecToTheEnd = 60*60*24*1000 - 1;
            event.end.setTime(Date.parse(event.end) + msecToTheEnd);
        }
        var array = calendar.fullCalendar('clientEvents');
        for(i in array){
            if (event.id == array[i].id) {
                // console.log('no op');
            } else {
                if (event.end > array[i].start && event.start < array[i].end) {
                    // console.log('Overlap = TRUE \nstart: '+array[i].start+'\nend: '+array[i].end)
                    return true;
                }
            }
        }
        return false;
    }

    // Create unique ID
    function createID(event) {
        var date = new Date();
        var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        var salt = "";
        for (var i=0; i<=5; i++) {
            salt = salt + alphabet[Math.floor(Math.random() * alphabet.length)];
        };
        return event.user + date.getTime() + salt;
    }

    // POST update to server
    function postUpdateToServer(room_name, calEvent, allDay) {
        if (calEvent.allDay || allDay) {
            var tempEnd = calEvent.end;
        } else {
            var tempEnd = Date.parse(calEvent.end)/1000;
        };
        $.post('/update_event',
            {
                id: calEvent.id,
                room: room_name,
                title: calEvent.title,
                user: calEvent.user,
                start: Date.parse(calEvent.start)/1000,
                end: tempEnd,
                allDay: calEvent.allDay
            }, 
            function() {
                console.log(calEvent.id+" event modified")
            }
        );
    }

    // Create event array
    function createEventArray(event_title, user, start, end, allDay, repeat) {
        
        var events = [];


        switch (repeat) {
          case 'day':
            //
          case 'week':
            //
          case 'month':
            //
          default:
            //
        }

    }
});
