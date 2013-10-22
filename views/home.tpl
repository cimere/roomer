<!doctype html>
<html>
<head>
  % include head title='Home'
</head>
<body>

<!-- Wrap all page content here -->
  <div id="wrap">

    % include header stanze= [room['name'] for room in rooms]

    <!-- Begin page content -->
    <div class="container">
      <h1>Ciao {{username}}.</h1>
      <div>
        <h4>Scegli una stanza da prenotare.</br></h4>
        <em>Hint: puoi sceglierla anche dalla barra di navigazione in alto.</em>
      </div>
      <ul>
      %for room in rooms:
      <li><a href="/room/{{room['name']}}">{{room['name']}}</a></li>
      %end
      <li>Corner AGILITY, postazione per 3 persone con tavolino e punti rete (non prenotabile).</li>
      </ul>
    </div> <!-- /container -->
  </div>
  
  % include footer

</body>
</html>
