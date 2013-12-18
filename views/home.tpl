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
      <h2>Ciao {{user['firstname']}}</h2>
      <div>
        <h4>Scegli una stanza da prenotare.</br></h4>
      </div>
      <div class="alert alert-warning" style="display: none;">
	Suggeriamo di utilizzare l'indirizzo <a href="http://roomer" >http://roomer</a>.
	Una volta cliccato il link salvate il nuovo indirizzo tra i preferiti con CTRL+D.
      </div>
      <br />
      <div class="well">
	%if reservations == []:
	<p>Nessuna prenotazione nei prossimi sette giorni.</p>
	%else:
	%for reservation in  reservations:
	<div class="btn">
	  <a class="btn btn-primary" href="\room\{{ reservation['name']}}">
	    {{ reservation['reservations']['day'] }}<br />
	    {{ reservation['reservations']['start'] }} - {{ reservation['reservations']['end'] }}<br />
	    {{ reservation['name'] }}<br />
	    {{ reservation['reservations']['title'] }}
	  </a>
	</div>
	%end
	%end
      </div> <!-- /well -->
      <div class="well">
	<ul class="list-unstyled">
	  %for room in rooms:
	  <li>
	    <div class="row">
	      <br />
	      <div class="col-md-2"><a href="\room\{{room['name']}}"><img src="/images/{{room['name']}}.png" /></a></div>
	      <div class="col-md-8">{{room['desc']}}</div>
	    </div> <!-- /row -->  
	  </li>
	  %end
	</ul>
      </div> <!-- /well -->
      <div class="well">
	<ul class="list-unstyled">
	  <li>
	    <div class="row">
	      <div class="col-md-2"><img src="/images/AGILITY.png" /></div>
	      <div class="col-md-8">Corner AGILITY, postazione per 3 persone con tavolino e punti rete (non prenotabile).</div>
	    </div>
	  </li>
	</ul>
      </div> <!-- /well -->
    </div> <!-- /container -->
  </div>
  
  % include footer

</body>
</html>
