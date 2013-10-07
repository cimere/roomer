<!-- TODO: merge this informations in homepage
adding reservations info -->

<!doctype html>
<html>
<head>
  % include head title='Login'
</head>
<body>
  <h1>Dettagli {{user['_id']}}</h1>
  <p><strong>Nome: </strong>{{user['firstname']}}</p>
  <p><strong>Cognome: </strong>{{user['lastname']}}</p>
  <p><strong>email: </strong>{{user['email']}}</p>
</body>
</html>
