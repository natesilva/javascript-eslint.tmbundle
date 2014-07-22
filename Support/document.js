/* global Zepto, document, EJS, context, ejsTemplate, TextMate, window */

'use strict';

Zepto(document).ready(function($) {
  var VERSION = '1.1.1';

  // Remove the marker flag indicating that the validation window
  // for this document is showing.
  $(document).on('visibilitychange', function() {
    window.setTimeout(function() {
      if (document.hidden && ('markerFile' in context) && context.markerFile) {
        TextMate.system('/bin/rm "' + context.markerFile + '"');
      }
    }, 1);
  });

  // close the report window when the user presses ESCape
  $(document).keydown(function(e) {
    if (e.keyCode === 27) {
      e.preventDefault();
      var cmd = '"tell application \\"System Events\\" ' +
        'to keystroke \\"w\\" using command down"';
      TextMate.system('osascript -e ' + cmd, function(){});
    }
  });

  // render the template and inject it into the page
  var html = new EJS({text: ejsTemplate}).render(context);
  $('#content').html(html);

  // By default, links will open in the TextMate results window. If
  // the <a> tag has class "open-external" we’ll catch it and open
  // the link in the user’s browser instead.
  $('.open-external').on('click', function(e) {
    e.preventDefault();
    var href = $(this).attr('href');
    if (!href.match(/^http(?:s?)\:\/\/[^\/]/)) {
      // doesn’t look like a normal URL
      return;
    }
    TextMate.system('open "' + encodeURI(href) + '"', null);
  });

  $('.version-number').text('v' + VERSION);
});
