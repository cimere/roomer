<!doctype html>
<html>
<head>
  % include head title='Home'
</head>
<body>

<!-- Wrap all page content here -->
  <div id="wrap">

    % include header rooms=[room['name'] for room in rooms],username=user['firstname']


    <!-- Begin page content -->
    <div class="container">
      <div class="alert alert-warning" style="display: none;">
	Suggeriamo di utilizzare l'indirizzo <a href="http://roomer" >http://roomer</a>.
	Una volta cliccato il link salvate il nuovo indirizzo tra i preferiti con CTRL+D.
      </div>
      <br />
      <div class="panel panel-default">
	<div class="panel-heading">Ciao {{user['firstname']}}, ecco le tue prenotazioni:</div>
	<div class="panel-body">
	  %if reservations == []:
	  <p>Nessuna prenotazione nei prossimi sette giorni.</p>
	  %else:
	  %for reservation in  reservations:
	  <div class="btn">
	    <a class="btn btn-primary" href="/room/{{ reservation['name']}}">
	      {{ reservation['reservations']['day'] }}<br />
	      {{ reservation['reservations']['start'] }} - {{ reservation['reservations']['end'] }}<br />
	      {{ reservation['name'] }}<br />
	      {{ reservation['reservations']['title'] }}
	    </a>
	  </div>
	  %end
	  %end
	</div>
      </div>
      <div class="panel panel-default">
	<div class="panel-heading">Scegli una stanza da prenotare.</div>
	<div class="panel-body">
	  <ul class="list-unstyled">
	    %if rooms == []:
	    <p>Whooops! {{user['firstname']}}, non puoi prenotare stanze. :(</p>
	    <p>Contatta l'amministratore di roomer per risolvere il problema.</p>
	    %else:
	    %for room in rooms:
	    %if room['bookable'] == True:
	    <a class="btn btn-{{room['name']}}" title="{{room['desc']}}" href="/room/{{room['name']}}">{{room['name']}}</a>
	    %else:
	    <div class="btn btn-{{room['name']}} noClick" title="{{room['desc']}}">{{room['name']}}</div>
	    %end
	    %end
	  </ul>
	</div>
      </div>
    </div> <!-- /container -->
  </div>
  
  % include footer
  <script src="../scripts.js"></script>

</body>
</html>
