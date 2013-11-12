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
