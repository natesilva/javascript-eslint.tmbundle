/* global Zepto, document, EJS, context, ejsTemplate, TextMate, window */

'use strict';

Zepto(document).ready(function($) {
  var VERSION = '2.0.0';

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
      TextMate.system('osascript -e ' + cmd, function() {});
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

	// parse a version number into semver parts
  var parseVersion = function(ver) {
    return ver.split('.').map(function(part) { return parseInt(part, 10); });
  };

  // return true if target is newer than current
  var newer = function(current, target) {
    var currentParts = parseVersion(current);
    var targetParts = parseVersion(target);
    if (currentParts.length !== 3 || targetParts.length !== 3) { return false; }

    if (targetParts[0] > currentParts[0]) { return true; }
    if (targetParts[0] < currentParts[0]) { return false; }

    if (targetParts[1] > currentParts[1]) { return true; }
    if (targetParts[1] < currentParts[1]) { return false; }

    if (targetParts[2] > currentParts[2]) { return true; }
    if (targetParts[2] < currentParts[2]) { return false; }

    return false;
  };

  $('.update-checker').on('click', function(e) {
    e.preventDefault();
    $.ajax({
      url: 'https://raw.githubusercontent.com/natesilva/javascript-eslint.tmbundle/master/latest.json',
      dataType: 'json',
      success: function(data) {
        $('.update-checker').addClass('hidden');
        if (newer(VERSION, data.latest)) {
          $('.update-available').removeClass('hidden');
        } else {
          $('.no-update').removeClass('hidden');
        }
      },
      error: function() {
        $('.update-checker').addClass('hidden');
        $('.update-error').removeClass('hidden');
      }
    });
  });
});
