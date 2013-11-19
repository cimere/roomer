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
    
    var room_name = $('span.room_name').text();
    $(document.getElementById(room_name)).addClass("active");
    var user = $('span.user').text();

    var calendar = $('#calendar').fullCalendar({
	
        // options
	// Text/Time Customization
	monthNames: ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
		     'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
	monthNamesShort: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu',
			  'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
	dayNames: ['Domenica', 'Lunedi', 'Martedi', 'Mercoledi',
		   'Giovedi', 'Venerdi', 'Sabato', 'Domenica'],
	dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mer',
			'Gio', 'Ven', 'Sab', 'Dom'],
	timeFormat: 'H:mm{ - H:mm}',
	columnFormat: {
	    month: 'ddd',    // Lun
	    week: 'ddd d', // Lun 31
	    day: 'dddd d'  // Lunedi 31
	},
	buttonText: {
            prev:     '&lsaquo;', // <
	    next:     '&rsaquo;', // >
	    prevYear: '&laquo;',  // <<
	    nextYear: '&raquo;',  // >>
	    today:    'Oggi',
	    month:    'Mese',
	    week:     'Settimana',
	    day:      'Giorno'
	},
	// General Display
	firstDay: 1,
	aspectRatio: 1.6,
        weekends: false, // will hide Saturdays and Sundays
	header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
	// Views
        defaultView: 'agendaWeek',
	// Agenda Options
	allDaySlot: false,
	firstHour: 8,
	minTime: "7:00am",
	maxTime: "9:00pm",
	axisFormat: 'HH(:mm)',
	// Selection
        selectable: true,
        selectHelper: true,
	// Event Data
	ignoreTimezone: false,
        // callbacks
        select: function(start, end, allDay) {
            
	    if (allDay) {
		calendar.fullCalendar( 'changeView', 'agendaWeek' );
		return;
	    }
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
	    if (calEvent.user == user) {
		var buttons = {}
		$( "#new-title" ).val(calEvent.title);
		if (calEvent.repeat == "never") {
		    var dialog_title = "Modifica evento";
		    addModifyButton(buttons, calEvent);
		    addRemoveButton(buttons, calEvent);
                    $("#whichEventDiv").hide();
		} else {
		    var dialog_title = "Rimuovi Evento";
		    addRemoveButton(buttons, calEvent);
		    $("#whichEventDiv").show();
		}
		$( "#dialog-update" ).dialog({
		    resizable: false,
                    modal: true,
                    buttons: buttons,
		    title: dialog_title
		})
	    } else {
		// 
	    }
        },
        eventResize: function(calEvent, dayDelta, minuteDelta, revertFunc) {
            if ((isOverlapping(calEvent)) || (calEvent.repeat != "never") || (calEvent.user != user)) {
                revertFunc();
            } else {
                postUpdateToServer(room_name, calEvent);
            }
        },
        eventDrop: function(calEvent, dayDelta, minuteDelta, allDay, revertFunc) {
            if ((isOverlapping(calEvent)) || (calEvent.repeat != "never") || (calEvent.user != user)) {
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

    enableSmartLinks(calendar);

    // moving on start date
    var start_unix = getParameterByName('start');
    if (start_unix == '') {
	var start_date = new Date();
    } else {
	var start_date = $.fullCalendar.parseDate( start_unix );
    }
    console.log( start_date );
    calendar.fullCalendar('gotoDate', start_date);
    

    // Helper functions

    // smart links (open new calendar view on current calendar date)
    function enableSmartLinks( calendar ) {
	$("li > a").each(function( index ) {
	    var parent_id = $( this ).parent().get( 0 ).id;
	    if (parent_id != "Home") {
	    	$( this ).click( function() {
		    var currentDate = calendar.fullCalendar( 'getDate' );
		    var currentDateInt = Date.parse(currentDate)/1000
		    $(this).attr('href', parent_id+"?start="+currentDateInt);
		})
	    }
	})
    }

    // grab query string paramater
    // http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values
    function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
	return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }
    // Buttons

    function addRemoveButton(buttons, calEvent) {
	
	buttons["Rimuovi"] = function() {
            id = calEvent._id;
            $("#dialog-update").dialog( "close" );
            var scope = $("#whichEventDiv input[type='radio']:checked").val();
            $.post('/remove_event', {id: id, 
				     room: room_name, 
				     repeat: calEvent.repeat,
				     scope: scope,
				     num: calEvent.num},
		   function() {
		       calendar.fullCalendar( 'refetchEvents' );
		   }
		  );
	}
    }

    function addModifyButton(buttons, calEvent) {

	buttons["Modifica"] =  function() {
            var new_event_title = $( "#new-title" ).val()
            if (new_event_title) {
		var scope = $("#whichEventDiv input[type='radio']:checked").val();
		calEvent.title = new_event_title;
		postUpdateToServer(room_name, calEvent);
            }
            $("#dialog-update").dialog( "close" );
	}
    }


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
            } else {
                if (event.end > array[i].start && event.start < array[i].end) {
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
    function postUpdateToServer(room_name, calEvent, which) {
        // if (calEvent.allDay || allDay) {
        //     var tempEnd = calEvent.end;
        // } else {
        //     var tempEnd = Date.parse(calEvent.end)/1000;
        // };
	var scope = $("#whichEventDiv input[type='radio']:checked").val();
        $.post('/update_event',
               {
                   id: calEvent.id,
                   room: room_name,
                   title: calEvent.title,
                   user: calEvent.user,
		   start: Date.parse(calEvent.start)/1000, // to UNIX format
		   end: Date.parse(calEvent.end)/1000,
		   allDay: calEvent.allDay,
		   repeat: calEvent.repeat,
		   until: calEvent.until,
		   num: calEvent.num,
		   scope: scope
               }, 
               function() {
                   calendar.fullCalendar( 'refetchEvents' );
               }
	      );
    }

    // Post insert to server
    function insertEvent(room, title, user, start, end, allDay) {

	var event_id = createID(user)
	var until = $('#until').val();
	repeatLogic();        
	if (repeat == 'never') {
	    var backgroundColor = "#6AA4C1";
	    var borderColor = "#3A87AD";

	} else {
	    var backgroundColor = "#E41359";
	    var borderColor = "#930A38";
	}
	$.post('/insert_event', 
               {
                   id: event_id,
                   room: room,
                   title: title,
                   user: user,
		   start: Date.parse(start)/1000, // to UNIX format
		   end: Date.parse(end)/1000,
                   allDay: allDay,
		   repeat: repeat,
		   until: until + "T23:59:59",
		   num: 0,
		   backgroundColor: backgroundColor,
		   borderColor: borderColor
               }, 
               function() {
                   calendar.fullCalendar( 'refetchEvents' );
               }
              );
    }
});
