// # Copyright (C) 2010-2016  RhodeCode GmbH
// #
// # This program is free software: you can redistribute it and/or modify
// # it under the terms of the GNU Affero General Public License, version 3
// # (only), as published by the Free Software Foundation.
// #
// # This program is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU Affero General Public License
// # along with this program.  If not, see <http://www.gnu.org/licenses/>.
// #
// # This program is dual-licensed. If you wish to learn more about the
// # RhodeCode Enterprise Edition, including its added features, Support services,
// # and proprietary license terms, please see https://rhodecode.com/licenses/

/**
 * Code Mirror
 */
// global code-mirror logger;, to enable run
// Logger.get('CodeMirror').setLevel(Logger.DEBUG)

cmLog = Logger.get('CodeMirror');
cmLog.setLevel(Logger.OFF);


//global cache for inline forms
var userHintsCache = {};


var initCodeMirror = function(textAreadId, resetUrl, focus, options) {
  var ta = $('#' + textAreadId).get(0);
  if (focus === undefined) {
      focus = true;
  }

  // default options
  var codeMirrorOptions = {
    mode: "null",
    lineNumbers: true,
    indentUnit: 4,
    autofocus: focus
  };

  if (options !== undefined) {
    // extend with custom options
    codeMirrorOptions = $.extend(true, codeMirrorOptions, options);
  }

  var myCodeMirror = CodeMirror.fromTextArea(ta, codeMirrorOptions);

  $('#reset').on('click', function(e) {
    window.location = resetUrl;
  });

  return myCodeMirror;
};

var initCommentBoxCodeMirror = function(textAreaId, triggerActions){
  var initialHeight = 100;

  // global timer, used to cancel async loading
  var loadUserHintTimer;

  if (typeof userHintsCache === "undefined") {
    userHintsCache = {};
    cmLog.debug('Init empty cache for mentions');
  }
  if (!$(textAreaId).get(0)) {
    cmLog.debug('Element for textarea not found', textAreaId);
    return;
  }
  var escapeRegExChars = function(value) {
    return value.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
  };
  /**
   * Load hints from external source returns an array of objects in a format
   * that hinting lib requires
   * @returns {Array}
   */
  var loadUserHints = function(query, triggerHints) {
    cmLog.debug('Loading mentions users via AJAX');
    var _users = [];
    $.ajax({
        type: 'GET',
        data: {query: query},
        url: pyroutes.url('user_autocomplete_data'),
        headers: {'X-PARTIAL-XHR': true},
        async: true
    })
    .done(function(data) {
      var tmpl = '<img class="gravatar" src="{0}"/>{1}';
      $.each(data.suggestions, function(i) {
        var userObj = data.suggestions[i];

        if (userObj.username !== "default") {
          _users.push({
            text: userObj.username + " ",
            org_text: userObj.username,
            displayText: userObj.value_display, // search that field
            // internal caches
            _icon_link: userObj.icon_link,
            _text: userObj.value_display,

            render: function(elt, data, completion) {
              var el = document.createElement('div');
              el.className = "CodeMirror-hint-entry";
              el.innerHTML = tmpl.format(
                  completion._icon_link, completion._text);
              elt.appendChild(el);
            }
          });
        }
      });
      cmLog.debug('Mention users loaded');
      // set to global cache
      userHintsCache[query] = _users;
      triggerHints(userHintsCache[query]);
    })
    .fail(function(data, textStatus, xhr) {
      alert("error processing request: " + textStatus);
    });
  };

    /**
     * filters the results based on the current context
     * @param users
     * @param context
     * @returns {Array}
     */
    var filterUsers = function(users, context) {
      var MAX_LIMIT = 10;
      var filtered_users = [];
      var curWord = context.string;

      cmLog.debug('Filtering users based on query:', curWord);
      $.each(users, function(i) {
        var match = users[i];
        var searchText = match.displayText;

        if (!curWord ||
          searchText.toLowerCase().lastIndexOf(curWord) !== -1) {
          // reset state
          match._text = match.displayText;
          if (curWord) {
            // do highlighting
            var pattern = '(' + escapeRegExChars(curWord) + ')';
            match._text = searchText.replace(
              new RegExp(pattern, 'gi'), '<strong>$1<\/strong>');
          }

            filtered_users.push(match);
        }
        // to not return to many results, use limit of filtered results
        if (filtered_users.length > MAX_LIMIT) {
          return false;
        }
      });

      return filtered_users;
    };

    /**
     * Filter action based on typed in text
     * @param actions
     * @param context
     * @returns {Array}
     */

    var filterActions = function(actions, context){
      var MAX_LIMIT = 10;
      var filtered_actions= [];
      var curWord = context.string;

      cmLog.debug('Filtering actions based on query:', curWord);
      $.each(actions, function(i) {
        var match = actions[i];
        var searchText = match.displayText;

        if (!curWord ||
          searchText.toLowerCase().lastIndexOf(curWord) !== -1) {
          // reset state
          match._text = match.displayText;
          if (curWord) {
            // do highlighting
            var pattern = '(' + escapeRegExChars(curWord) + ')';
            match._text = searchText.replace(
              new RegExp(pattern, 'gi'), '<strong>$1<\/strong>');
          }

          filtered_actions.push(match);
        }
        // to not return to many results, use limit of filtered results
        if (filtered_actions.length > MAX_LIMIT) {
            return false;
        }
      });
      return filtered_actions;
    };

    var completeAfter = function(cm, pred) {
      var options = {
        completeSingle: false,
        async: true,
        closeOnUnfocus: true
      };
        var cur = cm.getCursor();
      setTimeout(function() {
        if (!cm.state.completionActive) {
          cmLog.debug('Trigger mentions hinting');
          CodeMirror.showHint(cm, CodeMirror.hint.mentions, options);
        }
      }, 100);

      // tell CodeMirror we didn't handle the key
      // trick to trigger on a char but still complete it
      return CodeMirror.Pass;
    };

    var submitForm = function(cm, pred) {
      $(cm.display.input.textarea.form).submit();
      return CodeMirror.Pass;
    };

    var completeActions = function(cm, pred) {
      var cur = cm.getCursor();
      var options = {
        closeOnUnfocus: true
      };
      setTimeout(function() {
        if (!cm.state.completionActive) {
          cmLog.debug('Trigger actions hinting');
          CodeMirror.showHint(cm, CodeMirror.hint.actions, options);
        }
      }, 100);
    };

    var extraKeys = {
      "'@'": completeAfter,
      Tab: function(cm) {
        // space indent instead of TABS
        var spaces = new Array(cm.getOption("indentUnit") + 1).join(" ");
        cm.replaceSelection(spaces);
      }
    };
    // submit form on Meta-Enter
    if (OSType === "mac") {
      extraKeys["Cmd-Enter"] = submitForm;
    }
    else {
      extraKeys["Ctrl-Enter"] = submitForm;
    }

    if (triggerActions) {
      extraKeys["Ctrl-Space"] = completeActions;
    }

    var cm = CodeMirror.fromTextArea($(textAreaId).get(0), {
      lineNumbers: false,
      indentUnit: 4,
      viewportMargin: 30,
      // this is a trick to trigger some logic behind codemirror placeholder
      // it influences styling and behaviour.
      placeholder: " ",
      extraKeys: extraKeys,
      lineWrapping: true
    });

    cm.setSize(null, initialHeight);
    cm.setOption("mode", DEFAULT_RENDERER);
    CodeMirror.autoLoadMode(cm, DEFAULT_RENDERER); // load rst or markdown mode
    cmLog.debug('Loading codemirror mode', DEFAULT_RENDERER);
    // start listening on changes to make auto-expanded editor
    cm.on("change", function(self) {
      var height = initialHeight;
      var lines = self.lineCount();
      if ( lines > 6 && lines < 20) {
        height = "auto";
      }
      else if (lines >= 20){
        zheight = 20*15;
      }
      self.setSize(null, height);
    });

    var mentionHint = function(editor, callback, options) {
      var cur = editor.getCursor();
      var curLine = editor.getLine(cur.line).slice(0, cur.ch);

      // match on @ +1char
      var tokenMatch = new RegExp(
          '(^@| @)([a-zA-Z0-9]{1}[a-zA-Z0-9\-\_\.]*)$').exec(curLine);

      var tokenStr = '';
      if (tokenMatch !== null && tokenMatch.length > 0){
        tokenStr = tokenMatch[0].strip();
      } else {
        // skip if we didn't match our token
        return;
      }

      var context = {
        start: (cur.ch - tokenStr.length) + 1,
        end: cur.ch,
        string: tokenStr.slice(1),
        type: null
      };

      // case when we put the @sign in fron of a string,
      // eg <@ we put it here>sometext then we need to prepend to text
      if (context.end > cur.ch) {
        context.start = context.start + 1; // we add to the @ sign
        context.end = cur.ch; // don't eat front part just append
        context.string = context.string.slice(1, cur.ch - context.start);
      }

      cmLog.debug('Mention context', context);

      var triggerHints = function(userHints){
        return callback({
          list: filterUsers(userHints, context),
          from: CodeMirror.Pos(cur.line, context.start),
          to: CodeMirror.Pos(cur.line, context.end)
        });
      };

      var queryBasedHintsCache = undefined;
      // if we have something in the cache, try to fetch the query based cache
      if (userHintsCache !== {}){
        queryBasedHintsCache = userHintsCache[context.string];
      }

      if (queryBasedHintsCache !== undefined) {
        cmLog.debug('Users loaded from cache');
        triggerHints(queryBasedHintsCache);
      } else {
        // this takes care for async loading, and then displaying results
        // and also propagates the userHintsCache
        window.clearTimeout(loadUserHintTimer);
        loadUserHintTimer = setTimeout(function() {
            loadUserHints(context.string, triggerHints);
        }, 300);
      }
    };

    var actionHint = function(editor, options) {
      var cur = editor.getCursor();
      var curLine = editor.getLine(cur.line).slice(0, cur.ch);

      var tokenMatch = new RegExp('[a-zA-Z]{1}[a-zA-Z]*$').exec(curLine);

      var tokenStr = '';
      if (tokenMatch !== null && tokenMatch.length > 0){
        tokenStr = tokenMatch[0].strip();
      }

      var context = {
        start: cur.ch - tokenStr.length,
        end: cur.ch,
        string: tokenStr,
        type: null
      };

      var actions = [
        {
          text: "approve",
          displayText: _TM['Set status to Approved'],
          hint: function(CodeMirror, data, completion) {
            CodeMirror.replaceRange("", completion.from || data.from,
                        completion.to || data.to, "complete");
            $('#change_status').select2("val", 'approved').trigger('change');
          },
          render: function(elt, data, completion) {
            var el = document.createElement('div');
            el.className = "flag_status flag_status_comment_box approved pull-left";
            elt.appendChild(el);

            el = document.createElement('span');
            el.innerHTML = completion.displayText;
            elt.appendChild(el);
          }
        },
        {
          text: "reject",
          displayText: _TM['Set status to Rejected'],
          hint: function(CodeMirror, data, completion) {
              CodeMirror.replaceRange("", completion.from || data.from,
                          completion.to || data.to, "complete");
              $('#change_status').select2("val", 'rejected').trigger('change');
          },
          render: function(elt, data, completion) {
              var el = document.createElement('div');
              el.className = "flag_status flag_status_comment_box rejected pull-left";
              elt.appendChild(el);

              el = document.createElement('span');
              el.innerHTML = completion.displayText;
              elt.appendChild(el);
          }
        }
      ];

      return {
        list: filterActions(actions, context),
        from: CodeMirror.Pos(cur.line, context.start),
        to: CodeMirror.Pos(cur.line, context.end)
      };
    };
    CodeMirror.registerHelper("hint", "mentions", mentionHint);
    CodeMirror.registerHelper("hint", "actions", actionHint);
    return cm;
};

var setCodeMirrorMode = function(codeMirrorInstance, mode) {
  CodeMirror.autoLoadMode(codeMirrorInstance, mode);
  codeMirrorInstance.setOption("mode", mode);
};

var setCodeMirrorLineWrap = function(codeMirrorInstance, line_wrap) {
  codeMirrorInstance.setOption("lineWrapping", line_wrap);
};

var setCodeMirrorModeFromSelect = function(
  targetSelect, targetFileInput, codeMirrorInstance, callback){

  $(targetSelect).on('change', function(e) {
    cmLog.debug('codemirror select2 mode change event !');
    var selected = e.currentTarget;
    var node = selected.options[selected.selectedIndex];
    var mimetype = node.value;
    cmLog.debug('picked mimetype', mimetype);
    var new_mode = $(node).attr('mode');
    setCodeMirrorMode(codeMirrorInstance, new_mode);
    cmLog.debug('set new mode', new_mode);

    //propose filename from picked mode
    cmLog.debug('setting mimetype', mimetype);
    var proposed_ext = getExtFromMimeType(mimetype);
    cmLog.debug('file input', $(targetFileInput).val());
    var file_data = getFilenameAndExt($(targetFileInput).val());
    var filename = file_data.filename || 'filename1';
    $(targetFileInput).val(filename + proposed_ext);
    cmLog.debug('proposed file', filename + proposed_ext);


    if (typeof(callback) === 'function') {
      try {
        cmLog.debug('running callback', callback);
        callback(filename, mimetype, new_mode);
      } catch (err) {
        console.log('failed to run callback', callback, err);
      }
    }
    cmLog.debug('finish iteration...');
  });
};

var setCodeMirrorModeFromInput = function(
  targetSelect, targetFileInput, codeMirrorInstance, callback) {

  // on type the new filename set mode
  $(targetFileInput).on('keyup', function(e) {
    var file_data = getFilenameAndExt(this.value);
    if (file_data.ext === null) {
      return;
    }

    var mimetypes = getMimeTypeFromExt(file_data.ext, true);
    cmLog.debug('mimetype from file', file_data, mimetypes);
    var detected_mode;
    var detected_option;
    for (var i in mimetypes) {
      var mt = mimetypes[i];
      if (!detected_mode) {
        detected_mode = detectCodeMirrorMode(this.value, mt);
      }

      if (!detected_option) {
        cmLog.debug('#mimetype option[value="{0}"]'.format(mt));
        if ($(targetSelect).find('option[value="{0}"]'.format(mt)).length) {
          detected_option = mt;
        }
      }
    }

    cmLog.debug('detected mode', detected_mode);
    cmLog.debug('detected option', detected_option);
    if (detected_mode && detected_option){

      $(targetSelect).select2("val", detected_option);
      setCodeMirrorMode(codeMirrorInstance, detected_mode);

      if(typeof(callback) === 'function'){
        try{
          cmLog.debug('running callback', callback);
          var filename = file_data.filename + "." + file_data.ext;
          callback(filename, detected_option, detected_mode);
        }catch (err){
          console.log('failed to run callback', callback, err);
        }
      }
    }

  });
};

var fillCodeMirrorOptions = function(targetSelect) {
  //inject new modes, based on codeMirrors modeInfo object
  var modes_select = $(targetSelect);
  for (var i = 0; i < CodeMirror.modeInfo.length; i++) {
    var m = CodeMirror.modeInfo[i];
    var opt = new Option(m.name, m.mime);
    $(opt).attr('mode', m.mode);
    modes_select.append(opt);
  }
};

var CodeMirrorPreviewEnable = function(edit_mode) {
  // in case it a preview enabled mode enable the button
  if (['markdown', 'rst', 'gfm'].indexOf(edit_mode) !== -1) {
    $('#render_preview').removeClass('hidden');
  }
  else {
    if (!$('#render_preview').hasClass('hidden')) {
      $('#render_preview').addClass('hidden');
    }
  }
};
