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

    % include header stanze=[room['name'] for room in rooms_names]

    <!-- Begin page content -->
    <div class="container">
      <h2>Ciao <span class="user">{{user}}</span>, prenota <span class="room_name">{{room_data['name']}}</span></h2>{{room_data['desc']}} Interno:{{room_data['tel']}}<br />
      <div id='calendar'></div>
      <div id="dialog-insert" title="Inserisci evento" style="display: none" >
    	  <label for="event-title">Titolo </label>
    	  <input type="text" name="event-title" id="title" autofocus /><br /><br />
        <label for="event-recursive">Ripeti ogni ...</label><br />
        <div id="radioDiv">
          <form>
          <label><input type="radio" id="repeat-day" name="repeat" value="day"/>   Giorno</label><br />
          <label><input type="radio" id="repeat-week" name="repeat" value="week" />   Settimana</label><br />
          <label><input type="radio" id="repeat-never" name="repeat" value="never" checked />   Mai</label><br />
          </form>
        </div>
        <label for="event-title">fino al </label>
        <input type="text" name="repeat-until" id="until" disabled /><br /><br />
      </div>
      <div id="dialog-update" title="Modifica evento" style="display: none">
    	  <label for="new-event-title">Titolo</label>
    	  <input type="text" id="new-title" /><br />
          <div id="whichEventDiv" style="display: none">
            <form>
              <label><input type="radio" id="onlyThis" name="repeat" value="onlyThis" checked/>   Solo questo</label><br />
              <!-- <label><input type="radio" id="fromHere" name="repeat" value="fromHere" />   Da qui</label><br />  -->
              <label><input type="radio" id="fromStart" name="repeat" value="fromStart" checked /> Tutto</label><br />
            </form>
	  </div>
      </div>
    </div> <!-- /container -->
  </div>
  
  % include footer

  <!-- FullCalendar javascripts -->
  <script src="../fullcalendar.js"></script>
  <script src="../scriptsCalendar.js"></script>

</body>
</html>



