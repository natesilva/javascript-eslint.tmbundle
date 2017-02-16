/* global document, TextMate, window */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
  var VERSION = '3.0.2';

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

  // close the report window when the user presses ESCape
  var handleEscape = function() {
    document.addEventListener('keydown', function(e) {
      if (e.keyCode === 27) {
        e.preventDefault();
        var cmd = '"tell application \\"System Events\\" ' +
          'to keystroke \\"w\\" using command down"';
        TextMate.system('osascript -e ' + cmd, function() {});
      }
    });
  };

  // By default, links will open in the TextMate results window. If
  // the <a> tag has class "open-external" we’ll catch it and open
  // the link in the user’s browser instead.
  var handleExternalLinks = function() {
    var handler = function(e) {
      e.preventDefault();
      var href = e.currentTarget.href;
      if (!href.match(/^http(?:s?)\:\/\/[^\/]/)) {
        // doesn’t look like a normal URL
        return;
      }
      TextMate.system('open "' + encodeURI(href) + '"', null);
    };

    var els = document.getElementsByClassName('open-external');
    Array.prototype.slice.call(els).forEach(function(el) {
      el.addEventListener('click', handler);
    });
  };

  var handleUpdateChecker = function() {
    var handler = function(e) {
      e.preventDefault();

      var request = new XMLHttpRequest();
      var url = 'https://raw.githubusercontent.com/natesilva/javascript-eslint.tmbundle/master/latest.json';
      request.open('GET', url, true);

      request.onload = function() {
        if (request.status < 200 || request.status > 299) {
          document.querySelector('.update-checker').classList.add('hidden');
          document.querySelector('.update-error').classList.remove('hidden');
        }

        var data = JSON.parse(request.responseText);
        document.querySelector('.update-checker').classList.add('hidden');
        if (newer(VERSION, data.latest)) {
          document.querySelector('.update-available').classList.remove('hidden');
        } else {
          document.querySelector('.no-update').classList.remove('hidden');
        }
      };

      request.onerror = function() {
        document.querySelector('.update-checker').classList.add('hidden');
        document.querySelector('.update-error').classList.remove('hidden');
      };

      request.send();
    };

    var els = document.getElementsByClassName('update-checker');
    Array.prototype.slice.call(els).forEach(function(el) {
      el.addEventListener('click', handler);
    });
  };

  var showVersion = function() {
    var el = document.querySelector('.version-number');
    if (el) { el.textContent = VERSION; }
  };

  // self init
  handleEscape();
  handleExternalLinks();
  handleUpdateChecker();
  showVersion();
});
