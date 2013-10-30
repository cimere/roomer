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
        <em>Hint: puoi sceglierla anche dalla barra di navigazione in alto.</em>
      </div>
      <br />
      <div class="well">
	<ul class="list-unstyled">
	  %for room in rooms:
	  <li><a href="/room/{{room['name']}}">{{room['name']}}</a> - {{room['desc']}} Interno: {{room['tel']}}</li>
	  %end
	  <li>Corner AGILITY, postazione per 3 persone con tavolino e punti rete (non prenotabile).</li>
	</ul>
      </div> <!-- /well -->
    </div> <!-- /container -->
  </div>
  
  % include footer

</body>
</html>
