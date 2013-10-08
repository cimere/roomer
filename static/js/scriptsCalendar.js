$(document).ready(function() {

	var room_name = $('span.room_name').text()
	var user = $('span.user').text();

	// var date = new Date();
	// var d = date.getDate();
	// var m = date.getMonth();
	// var y = date.getFullYear();
	// console.log(Date(y, m, d, 10, 30))
	// console.log(Date.parse(Date(y, m, d, 10, 30)))

    var calendar = $('#calendar').fullCalendar({
        // options and callbacks
        weekends: false, // will hide Saturdays and Sundays
    	header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		selectable: true,
		selectHelper: true,
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
	                		    	console.log(user+" is inserting a new event called "+event_title);
	                		    	var event = {
												title: event_title,
												user: user,
												start: start,
												end: end,
												allDay: allDay
									}
									event["id"] = createID(event);
	                		    	if (event_title) {
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
												start: start,
												end: end,
												allDay: allDay
											}, 
											function() {
												console.log("event saved")
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
                		    	console.log(new_event_title)
                		    	if (new_event_title) {
                		    		calEvent.title = new_event_title;
              						calendar.fullCalendar('updateEvent',calEvent);
	                        	    $.post('/update_event',
                        	    		{
											id: calEvent.id,
											room: room_name,
											title: calEvent.title,
											user: calEvent.user,
											start: calEvent.start,
											end: calEvent.end,
											allDay: calEvent.allDay
										}, 
										function() {
											console.log(id+" event modified")
										}
									);
                		    	}
                    	        $("#dialog-update").dialog( "close" );
                            },
                            "Rimuovi": function() {
                            	id = calEvent._id;
                        	    calendar.fullCalendar('removeEvents', id)
                        	    $("#dialog-update").dialog( "close" );
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
				$.post('/update_event',
		    		{
						id: calEvent.id,
						room: room_name,
						title: calEvent.title,
						user: calEvent.user,
						start: calEvent.start,
						end: calEvent.end,
						allDay: calEvent.allDay
					}, 
					function() {
						console.log(calEvent.id+" event modified")
					}
				);
			}
       	},
       	eventDrop: function(calEvent, dayDelta, minuteDelta, allDay, revertFunc) {
	   		if (isOverlapping(calEvent)) {
				revertFunc();
			} else {
	       		$.post('/update_event',
		    		{
						id: calEvent.id,
						room: room_name,
						title: calEvent.title,
						user: calEvent.user,
						start: calEvent.start,
						end: calEvent.end,
						allDay: calEvent.allDay
					}, 
					function() {
						console.log(calEvent.id+" event modified")
					}
				);
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
	    var array = calendar.fullCalendar('clientEvents');
	    for(i in array){
	    	if (event.id == array[i].id) {
	    		// console.log('no op');
	    	} else {
		        if (event.end > array[i].start && event.start < array[i].end){
		        	// console.log('Overlap = TRUE \nstart: '+array[i].start+'\nend: '+array[i].end)
		           	return true;
	        	}
	        }
	    }
	    return false;
	}

	// Create unique ID
	function createID(event) {
		var date = new Date()
		return event.user + String(Date.parse(event.start)) + 
			   String(Date.parse(event.end)) + date.getTime();
	}
});