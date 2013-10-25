<!doctype html>
<html>
<head>
  % include head title='Login'
</head>
<body>

<!-- Wrap all page content here -->
  <div id="wrap">
    <div class="container">
      <form class="form-signin" method="post">
         <h2 class="form-signin-heading">Test Login</h2>
        <label class="sr-only" for="username">Utente</label>
        <input type="text" name="username" id="username" class="form-control" autofocus value="{{username}}">
        <label class="checkbox">
          <input type="checkbox" value="remember-me"> Ricordami
        </label>
        <input type="submit" class="btn btn-lg btn-warning btn-block" value="Entra">
      </form>
    </div> <!-- /container -->
  </div>

  % include footer

  <!-- Page-customized javascritps -->
  <script src="../scripts.js"></script>

</body>
</html>
