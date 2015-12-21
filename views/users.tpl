<!-- TODO: merge this informations in homepage
adding reservations info -->

<!doctype html>
<html>
<head>
   % include head title='Users' 
</head>
<body>

    <div id="wrap">
    
    % include header 

    <!-- Begin page content -->
    <div class="container">
        <br />
	    <table class="table table-bordered display" id="table_users">
            <thead>
            <tr>
            <th>Name</th>
            </tr>
            </thead>
        </table>
    </div> <!-- /container -->
</body>
  % include footer

  <script src=" https://cdn.datatables.net/1.10.10/js/jquery.dataTables.min.js"></script>
  <script>
    $(document).ready( function () {
        console.log('ecco');
        $('#table_users').DataTable( {
            ajax: '/users',
            columns: [{ data: 0 }]
            } );
        } );

  </script>
</html>
