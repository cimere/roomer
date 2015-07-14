<!-- Fixed navbar -->
<div class="navbar navbar-default navbar-fixed-top">
  <div class="container">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="/">Roomer</a>
    </div>
    <div class="collapse navbar-collapse">
      <ul class="nav navbar-nav">
        <li id="Home"><a href="/">Home</a></li>
        %for room in rooms:
          %if room != "AGILITY":
            <li id="{{room}}"><a href="/room/{{room}}">{{room}}</a></li>
          %end
        %end
      </ul>
    </div><!--/.nav-collapse -->
  </div>
</div>