/*
 * Ticket status dashboard
 * John Jarvis jarv@edx.org
 *
 * Don't try to run this on IE
 */
URL = "http://localhost:5000/tender";

$(document).ready(function() {

    var updateBoard = function(data) {
      new_stats = ""; 
      most_recent = "";
      $.each(data.categories, function(i,v) {
        new_stats += '<div class="row">' +
                     '<div class="span8 stat label">' + v.label + '</div>' +
                     '<div class="span4 stat value">' + v.total + '</div>' +
                     '</div>';


        if (v.label == 'Pending Issues') {
          most_recent += '<table>';
          $.each(v.most_recent, function(i,v) {
            most_recent += '<tr><td>' + v.author_name + '</td>' +
                           '<td>' + v.title + '</td>' +
                           '<td>' + v.updated + '</td></tr>';
          });
          most_recent += '</table>';
          $('#most_recent').html(most_recent);
        }
      });
      $('#stats').html(new_stats);

      summary_stats = "";
      summary_stats += '<table class="summary_stats">' +
                       '<tr><th>Date</th><th>Created</th>' +
                       '<th>Resolved</th></tr>';
      $.each(data.stats, function(i,v) {
        summary_stats += '<tr><td>' + v.title + '</td>' + 
                         '<td>' + v.created + '</td>' +
                         '<td>' + v.resolved + '</td></tr>';
      });
      summary_stats += '</table>';
      $('#summary_stats').html(summary_stats);
    };


    ajax_poll = function() {
      $.ajax({
          url: URL,
          cache: 'false',
          dataType: 'json',
          type: 'get',
          async: 'false',
          success: updateBoard,
          error: function () {
            $('#stats').html('<span style="text-align: center; font-size: 40px;">' +
                             'server error</span>');
          }
      });
    };

    ajax_poll();
    var id = setInterval(ajax_poll,800);
});
