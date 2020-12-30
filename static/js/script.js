
// functionality of the mobile collapse navbar
  $(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.modal').modal();
    // $('.datepicker').datepicker();
    
    // Back to Top function
  var offset = 100;
  var speed = 250; var duration = 500;
  $(window).scroll(function(){ 
      if ($(this).scrollTop() < offset) { $('.topbutton') .fadeOut(duration); } else { $('.topbutton') .fadeIn(duration); } }); $('.topbutton').on('click', function(){ $('html, body').animate({scrollTop:0}, speed); 
      return false; });
  });
