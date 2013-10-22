
// TODO:
// 1. use UNIX time: DONE
// 2. check overlapping on all day: DONE
// 3. default su week: DONE
// 4. recursive events
// 5. only creator or admin can remove his events. Not needed

$(document).ready(function() {

    $( "#until" ).datepicker({ 
	dateFormat: "yy-mm-dd",
	firstDay: 1,
	dayNamesMin: [ "Do", "Lu", "Ma", "Me", "Gi", "Ve", "Sa" ],
	minDate: 0, 
	maxDate: "+6M" 
    });

    $( "#radioDiv" ).click( repeatLogic );

    var room_name = $('span.room_name').text()
    var user = $('span.user').text();

    var calendar = $('#calendar').fullCalendar({
	
        // options
	aspectRatio: 1.6,
        defaultView: 'agendaWeek',
	allDaySlot: false,
        weekends: false, // will hide Saturdays and Sundays
	firstHour: 8,
	firstDay: 1,
	columnFormat: {
	    month: 'ddd',    // Mon
	    week: 'ddd d', // Mon 31
	    day: 'dddd d'  // Monday 31
	},
	header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        selectable: true,
        selectHelper: true,

        // callbacks
        select: function(start, end, allDay) {
            
	    if (allDay) {
		calendar.fullCalendar( 'changeView', 'agendaWeek' );
		return;
	    }
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
                            if (event_title) {
                                // Insert in mongoDB
				insertEvent(room_name, event_title, user, start, end, allDay );
				$( "#dialog-insert" ).dialog( "close" );
                            };
                        }
                    }
                });
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
	    if (event.until == 0) {
		element.find('.fc-event-title').append(" - " + event.user); 
	    } else {
		element.find('.fc-event-title').append("- " + event.user + "<br />fino al " + event.until.slice(0,10));
	    }
        },
        editable: true,
        eventSources: [
            {
                url: '/get_events/'+room_name,
                error: function() {
                    alert('There was an error while fetching events!');
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

    // parse a date in dd-mm-yyyy format
    // http://stackoverflow.com/questions/2587345/javascript-date-parse
    function parseDate(input) {

	var parts = input.split('-');
	// new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
	return new Date(parts[2], parts[1] - 1, parts[0], 23, 59, 59, 999); // Months are 0-based
    }
    
    // Repeat-event UI logic
    function repeatLogic() {

        var recursive = false;
        var selected = $("#radioDiv input[type='radio']:checked");
        if (selected.length > 0)
            repeat = selected.val();
        if (repeat == "never") {
            $('#until').prop('disabled', true);
	    $('#until').val("");
            recursive = false;
        } else {
            $('#until').prop('disabled', false);
            recursive = true;
        }
    }
    
    // Create unique ID
    function createID(user) {
        var date = new Date();

        var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        var salt = "";
        for (var i=0; i<=5; i++) {
            salt = salt + alphabet[Math.floor(Math.random() * alphabet.length)];
        };
        return user + date.getTime() + salt;
    }

    // POST update to server
    function postUpdateToServer(room_name, calEvent, allDay) {
        // if (calEvent.allDay || allDay) {
        //     var tempEnd = calEvent.end;
        // } else {
        //     var tempEnd = Date.parse(calEvent.end)/1000;
        // };
        $.post('/update_event',
               {
                   id: calEvent.id,
                   room: room_name,
                   title: calEvent.title,
                   user: calEvent.user,
                   start: calEvent.start,
                   end: calEvent.end,
                   allDay: calEvent.allDay,
		   repeat: calEvent.repeat,
		   until: calEvent.until
               }, 
               function() {
		   console.log(user + " modified event id " + calEvent.id);
                   calendar.fullCalendar( 'refetchEvents' );
               }
	      );
    }

    // Post insert to server
    function insertEvent(room, title, user, start, end, allDay) {

	var event_id = createID(user)
	var until = $('#until').val();
	repeatLogic();        
	console.log(user+" is inserting a new event called "+title+" recursive "+repeat+" until "+until);	
	$.post('/insert_event', 
               {
                   id: event_id,
                   room: room,
                   title: title,
                   user: user,
                   start: start,
                   end: end,
                   allDay: allDay,
		   repeat: repeat,
		   until: until + "T23:59:59"
               }, 
               function() {
		   console.log(user + " created event id " + event_id);
                   calendar.fullCalendar( 'refetchEvents' );
               }
              );
    }
});
