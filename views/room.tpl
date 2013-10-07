<!doctype html>
<html>
<head>
  % include head title='Prenota'
  <!-- FullCalendar stylesheet -->
  <link rel='stylesheet' href='../fullcalendar.css' />
</head>
<body>

<!-- Wrap all page content here -->
  <div id="wrap">

    % include header stanze=rooms

    <!-- Begin page content -->
    <div class="container">
      <h1>Ciao <span class="user">{{user}}</span>, prenota <span class="room_name">{{room['name']}}</span></h1>
      <div id='calendar'></div>
      <div id="dialog-insert" title="Inserisci evento" style="display: none" >
    	  <label for="event-title">Titolo</label>
    	  <input type="text" name="event-title" id="title" />
      </div>
      <div id="dialog-update" title="Modifica evento" style="display: none">
    	  <label for="new-event-title">Titolo</label>
    	  <input type="text" name="new-event-title" id="new-title" />
      </div>
    </div> <!-- /container -->
  </div>
  
  % include footer

  <!-- FullCalendar javascripts -->
  <script src="../fullcalendar.js"></script>
  <script src="../scriptsCalendar.js"></script>

</body>
</html>



