$(document).ready(function(){
    $('#table').after('<div style="text-align: center;"><div id="nav" class="pagination"></div></div>');
    var rowsShown = 10;
    var rowsTotal = $('#table tbody tr').length;
    var numPages = rowsTotal/rowsShown;
    if (numPages > 1) {
        if (numPages > 9) {
            
            for(i = 0;i < numPages - 1;i++) {
                if (i < 9){
                    var pageNum = i + 1;
                    $('#nav').append('<a href="#" rel="'+i+'">'+pageNum+'</a> ');                    
                }
            }
            $('#nav').append('<a href="#" style="pointer-events: none; cursor: default;">...</a> ');
            $('#nav').append('<a href="#" rel="'+(numPages - 1)+'">'+numPages+'</a> ');

        } else {

            for(i = 0;i < numPages;i++) {
                var pageNum = i + 1;
                $('#nav').append('<a href="#" rel="'+i+'">'+pageNum+'</a> ');            
            }

        }
      $('#table tbody tr').hide();
      $('#table tbody tr').slice(0, rowsShown).show();
      $('#nav a:first').addClass('active');
      $('#nav a').bind('click', function(){

          $('#nav a').removeClass('active');
          $(this).addClass('active');
          var currPage = $(this).attr('rel');
          var startItem = currPage * rowsShown;
          var endItem = startItem + rowsShown;
          console.log($('#nav a').length)
          $('#table tbody tr').css('opacity','0.0').hide().slice(startItem, endItem).
          css('display','table-row').animate({opacity:1}, 300);
      });     
    } else {
      for(i = 0;i < numPages;i++) {
          var pageNum = i + 1;
      }
      $('#table tbody tr').hide();
      $('#table tbody tr').slice(0, rowsShown).show();
      $('#nav a').bind('click', function(){

          $('#nav a').removeClass('active');
          $(this).addClass('active');
          var currPage = $(this).attr('rel');
          var startItem = currPage * rowsShown;
          var endItem = startItem + rowsShown;
          $('#table tbody tr').css('opacity','0.0').hide().slice(startItem, endItem).
          css('display','table-row').animate({opacity:1}, 300);
      });
    }

});