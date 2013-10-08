<!doctype html>
<html>
<head>
  % include head title='Home'
</head>
<body>

<!-- Wrap all page content here -->
  <div id="wrap">

    % include header stanze=rooms

    <!-- Begin page content -->
    <div class="container">
      <h1>Ciao {{username}}.</h1>
      <div>
        <h4>Scegli una stanza da prenotare.</br>
        <em>Hint: puoi sceglierla anche dalla barra di navigazione in alto.</em></h4>
      </div>
      <ul>
      %for room in rooms:
      <li><a href="/room/{{room}}">{{room}}</a></li>
      %end
      </ul>
    </div> <!-- /container -->
  </div>
  
  % include footer

</body>
</html>
