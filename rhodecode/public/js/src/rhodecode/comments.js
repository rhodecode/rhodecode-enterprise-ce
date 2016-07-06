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

var firefoxAnchorFix = function() {
  // hack to make anchor links behave properly on firefox, in our inline
  // comments generation when comments are injected firefox is misbehaving
  // when jumping to anchor links
  if (location.href.indexOf('#') > -1) {
    location.href += '';
  }
};

// returns a node from given html;
var fromHTML = function(html){
  var _html = document.createElement('element');
  _html.innerHTML = html;
  return _html;
};

var tableTr = function(cls, body){
  var _el = document.createElement('div');
  var _body = $(body).attr('id');
  var comment_id = fromHTML(body).children[0].id.split('comment-')[1];
  var id = 'comment-tr-{0}'.format(comment_id);
  var _html = ('<table><tbody><tr id="{0}" class="{1}">'+
               '<td class="add-comment-line"><span class="add-comment-content"></span></td>'+
               '<td></td>'+
               '<td></td>'+
               '<td>{2}</td>'+
               '</tr></tbody></table>').format(id, cls, body);
  $(_el).html(_html);
  return _el.children[0].children[0].children[0];
};

var removeInlineForm = function(form) {
  form.parentNode.removeChild(form);
};

var createInlineForm = function(parent_tr, f_path, line) {
  var tmpl = $('#comment-inline-form-template').html();
  tmpl = tmpl.format(f_path, line);
  var form = tableTr('comment-form-inline', tmpl);
  var form_hide_button = $(form).find('.hide-inline-form');

  $(form_hide_button).click(function(e) {
     $('.inline-comments').removeClass('hide-comment-button');
     var newtr = e.currentTarget.parentNode.parentNode.parentNode.parentNode.parentNode;
     if ($(newtr.nextElementSibling).hasClass('inline-comments-button')) {
         $(newtr.nextElementSibling).show();
     }
     $(newtr).parents('.comment-form-inline').remove();
     $(parent_tr).removeClass('form-open');
     $(parent_tr).removeClass('hl-comment');
  });

  return form;
};

var getLineNo = function(tr) {
  var line;
  // Try to get the id and return "" (empty string) if it doesn't exist
  var o = ($(tr).find('.lineno.old').attr('id')||"").split('_');
  var n = ($(tr).find('.lineno.new').attr('id')||"").split('_');
  if (n.length >= 2) {
    line = n[n.length-1];
  } else if (o.length >= 2) {
   line = o[o.length-1];
  }
  return line;
};

/**
 * make a single inline comment and place it inside
 */
var renderInlineComment = function(json_data, show_add_button) {
  show_add_button = typeof show_add_button !== 'undefined' ? show_add_button : true;
  try {
    var html = json_data.rendered_text;
    var lineno = json_data.line_no;
    var target_id = json_data.target_id;
    placeInline(target_id, lineno, html, show_add_button);
  } catch (e) {
    console.error(e);
  }
};

function bindDeleteCommentButtons() {
    $('.delete-comment').one('click', function() {
        var comment_id = $(this).data("comment-id");

        if (comment_id){
            deleteComment(comment_id);
        }
    });
}

/**
 * Inject inline comment for on given TR this tr should be always an .line
 * tr containing the line. Code will detect comment, and always put the comment
 * block at the very bottom
 */
var injectInlineForm = function(tr){
  if (!$(tr).hasClass('line')) {
      return;
  }

  var _td = $(tr).find('.code').get(0);
  if ($(tr).hasClass('form-open') ||
      $(tr).hasClass('context') ||
      $(_td).hasClass('no-comment')) {
      return;
  }
  $(tr).addClass('form-open');
  $(tr).addClass('hl-comment');
  var node = $(tr.parentNode.parentNode.parentNode).find('.full_f_path').get(0);
  var f_path = $(node).attr('path');
  var lineno = getLineNo(tr);
  var form = createInlineForm(tr, f_path, lineno);

  var parent = tr;
  while (1) {
      var n = parent.nextElementSibling;
      // next element are comments !
      if ($(n).hasClass('inline-comments')) {
          parent = n;
      }
      else {
          break;
      }
  }
  var _parent = $(parent).get(0);
  $(_parent).after(form);
  $('.comment-form-inline').prev('.inline-comments').addClass('hide-comment-button');
  var f = $(form).get(0);

  var _form = $(f).find('.inline-form').get(0);

  var pullRequestId = templateContext.pull_request_data.pull_request_id;
  var commitId = templateContext.commit_data.commit_id;

  var commentForm = new CommentForm(_form, commitId, pullRequestId, lineno, false);
  var cm = commentForm.getCmInstance();

  // set a CUSTOM submit handler for inline comments.
  commentForm.setHandleFormSubmit(function(o) {
    var text = commentForm.cm.getValue();

    if (text === "") {
      return;
    }

    if (lineno === undefined) {
      alert('missing line !');
      return;
    }
    if (f_path === undefined) {
      alert('missing file path !');
      return;
    }

    var excludeCancelBtn = false;
    var submitEvent = true;
    commentForm.setActionButtonsDisabled(true, excludeCancelBtn, submitEvent);
    commentForm.cm.setOption("readOnly", true);
    var postData = {
        'text': text,
        'f_path': f_path,
        'line': lineno,
        'csrf_token': CSRF_TOKEN
    };
    var submitSuccessCallback = function(o) {
      $(tr).removeClass('form-open');
      removeInlineForm(f);
      renderInlineComment(o);
      $('.inline-comments').removeClass('hide-comment-button');

      // re trigger the linkification of next/prev navigation
      linkifyComments($('.inline-comment-injected'));
      timeagoActivate();
      bindDeleteCommentButtons();
      commentForm.setActionButtonsDisabled(false);

    };
    var submitFailCallback = function(){
        commentForm.resetCommentFormState(text)
    };
    commentForm.submitAjaxPOST(
        commentForm.submitUrl, postData, submitSuccessCallback, submitFailCallback);
  });

  setTimeout(function() {
      // callbacks
      if (cm !== undefined) {
          cm.focus();
      }
  }, 10);

    $.Topic('/ui/plugins/code/comment_form_built').prepare({
        form:_form,
        parent:_parent}
    );
};

var deleteComment = function(comment_id) {
  var url = AJAX_COMMENT_DELETE_URL.replace('__COMMENT_ID__', comment_id);
  var postData = {
    '_method': 'delete',
    'csrf_token': CSRF_TOKEN
  };

  var success = function(o) {
    window.location.reload();
  };
  ajaxPOST(url, postData, success);
};

var createInlineAddButton = function(tr){
  var label = _gettext('Add another comment');
  var html_el = document.createElement('div');
  $(html_el).addClass('add-comment');
  html_el.innerHTML = '<span class="btn btn-secondary">{0}</span>'.format(label);
  var add = new $(html_el);
  add.on('click', function(e) {
    injectInlineForm(tr);
  });
  return add;
};

var placeAddButton = function(target_tr){
  if(!target_tr){
    return;
  }
  var last_node = target_tr;
  // scan
  while (1){
    var n = last_node.nextElementSibling;
    // next element are comments !
    if($(n).hasClass('inline-comments')){
      last_node = n;
      // also remove the comment button from previous
      var comment_add_buttons = $(last_node).find('.add-comment');
      for(var i=0; i<comment_add_buttons.length; i++){
        var b = comment_add_buttons[i];
        b.parentNode.removeChild(b);
      }
    }
    else{
      break;
    }
  }
  var add = createInlineAddButton(target_tr);
  // get the comment div
  var comment_block = $(last_node).find('.comment')[0];
  // attach add button
  $(add).insertAfter(comment_block);
};

/**
 * Places the inline comment into the changeset block in proper line position
 */
var placeInline = function(target_container, lineno, html, show_add_button) {
  show_add_button = typeof show_add_button !== 'undefined' ? show_add_button : true;

  var lineid = "{0}_{1}".format(target_container, lineno);
  var target_line = $('#' + lineid).get(0);
  var comment = new $(tableTr('inline-comments', html));
  // check if there are comments already !
  var parent_node = target_line.parentNode;
  var root_parent = parent_node;
  while (1) {
    var n = parent_node.nextElementSibling;
    // next element are comments !
    if ($(n).hasClass('inline-comments')) {
      parent_node = n;
    }
    else {
      break;
    }
  }
  // put in the comment at the bottom
  $(comment).insertAfter(parent_node);
  $(comment).find('.comment-inline').addClass('inline-comment-injected');
  // scan nodes, and attach add button to last one
  if (show_add_button) {
    placeAddButton(root_parent);
  }

  return target_line;
};

var linkifyComments = function(comments) {

  for (var i = 0; i < comments.length; i++) {
    var comment_id = $(comments[i]).data('comment-id');
    var prev_comment_id = $(comments[i - 1]).data('comment-id');
    var next_comment_id = $(comments[i + 1]).data('comment-id');

    // place next/prev links
    if (prev_comment_id) {
      $('#prev_c_' + comment_id).show();
      $('#prev_c_' + comment_id + " a.arrow_comment_link").attr(
          'href', '#comment-' + prev_comment_id).removeClass('disabled');
    }
    if (next_comment_id) {
      $('#next_c_' + comment_id).show();
      $('#next_c_' + comment_id + " a.arrow_comment_link").attr(
          'href', '#comment-' + next_comment_id).removeClass('disabled');
    }
    // place a first link to the total counter
    if (i === 0) {
      $('#inline-comments-counter').attr('href', '#comment-' + comment_id);
    }
  }

};
  
/**
 * Iterates over all the inlines, and places them inside proper blocks of data
 */
var renderInlineComments = function(file_comments, show_add_button) {
  show_add_button = typeof show_add_button !== 'undefined' ? show_add_button : true;

  for (var i = 0; i < file_comments.length; i++) {
    var box = file_comments[i];

    var target_id = $(box).attr('target_id');

    // actually comments with line numbers
    var comments = box.children;

    for (var j = 0; j < comments.length; j++) {
      var data = {
        'rendered_text': comments[j].outerHTML,
        'line_no': $(comments[j]).attr('line'),
        'target_id': target_id
      };
      renderInlineComment(data, show_add_button);
    }
  }

  // since order of injection is random, we're now re-iterating
  // from correct order and filling in links
  linkifyComments($('.inline-comment-injected'));
  bindDeleteCommentButtons();
  firefoxAnchorFix();
};


/* Comment form for main and inline comments */
var CommentForm = (function() {
    "use strict";

    function CommentForm(formElement, commitId, pullRequestId, lineNo, initAutocompleteActions) {

        this.withLineNo = function(selector) {
            var lineNo = this.lineNo;
            if (lineNo === undefined) {
                return selector
            } else {
                return selector + '_' + lineNo;
            }
        };

        this.commitId = commitId;
        this.pullRequestId = pullRequestId;
        this.lineNo = lineNo;
        this.initAutocompleteActions = initAutocompleteActions;

        this.previewButton = this.withLineNo('#preview-btn');
        this.previewContainer = this.withLineNo('#preview-container');

        this.previewBoxSelector = this.withLineNo('#preview-box');

        this.editButton = this.withLineNo('#edit-btn');
        this.editContainer = this.withLineNo('#edit-container');

        this.cancelButton = this.withLineNo('#cancel-btn');

        this.statusChange = '#change_status';
        this.cmBox = this.withLineNo('#text');
        this.cm = initCommentBoxCodeMirror(this.cmBox, this.initAutocompleteActions);

        this.submitForm = formElement;
        this.submitButton = $(this.submitForm).find('input[type="submit"]');
        this.submitButtonText = this.submitButton.val();

        this.previewUrl = pyroutes.url('changeset_comment_preview',
            {'repo_name': templateContext.repo_name});

        // based on commitId, or pullReuqestId decide where do we submit
        // out data
        if (this.commitId){
            this.submitUrl = pyroutes.url('changeset_comment',
                {'repo_name': templateContext.repo_name,
                 'revision': this.commitId});

        } else if (this.pullRequestId) {
            this.submitUrl = pyroutes.url('pullrequest_comment',
                {'repo_name': templateContext.repo_name,
                 'pull_request_id': this.pullRequestId});

        } else {
            throw new Error(
                'CommentForm requires pullRequestId, or commitId to be specified.')
        }

        this.getCmInstance = function(){
            return this.cm
        };

        var self = this;

        this.getCommentStatus = function() {
          return $(this.submitForm).find(this.statusChange).val();
        };

        this.isAllowedToSubmit = function() {
          return !$(this.submitButton).prop('disabled');
        };

        this.initStatusChangeSelector = function(){
            var formatChangeStatus = function(state, escapeMarkup) {
                var originalOption = state.element;
                return '<div class="flag_status ' + $(originalOption).data('status') + ' pull-left"></div>' +
                       '<span>' + escapeMarkup(state.text) + '</span>';
            };
            var formatResult = function(result, container, query, escapeMarkup) {
                return formatChangeStatus(result, escapeMarkup);
            };

            var formatSelection = function(data, container, escapeMarkup) {
                return formatChangeStatus(data, escapeMarkup);
            };

            $(this.submitForm).find(this.statusChange).select2({
                placeholder: _gettext('Status Review'),
                formatResult: formatResult,
                formatSelection: formatSelection,
                containerCssClass: "drop-menu status_box_menu",
                dropdownCssClass: "drop-menu-dropdown",
                dropdownAutoWidth: true,
                minimumResultsForSearch: -1
            });
            $(this.submitForm).find(this.statusChange).on('change', function() {
                var status = self.getCommentStatus();
                if (status && !self.lineNo) {
                    $(self.submitButton).prop('disabled', false);
                }
                //todo, fix this name
                var placeholderText = _gettext('Comment text will be set automatically based on currently selected status ({0}) ...').format(status);
                self.cm.setOption('placeholder', placeholderText);
            })
        };

        // reset the comment form into it's original state
        this.resetCommentFormState = function(content) {
            content = content || '';

            $(this.editContainer).show();
            $(this.editButton).hide();

            $(this.previewContainer).hide();
            $(this.previewButton).show();

            this.setActionButtonsDisabled(true);
            self.cm.setValue(content);
            self.cm.setOption("readOnly", false);
        };

        this.submitAjaxPOST = function(url, postData, successHandler, failHandler) {
            failHandler = failHandler || function() {};
            var postData = toQueryString(postData);
            var request = $.ajax({
                    url: url,
                    type: 'POST',
                    data: postData,
                    headers: {'X-PARTIAL-XHR': true}
                })
                .done(function(data) {
                    successHandler(data);
                })
                .fail(function(data, textStatus, errorThrown){
                    alert(
                        "Error while submitting comment.\n" +
                        "Error code {0} ({1}).".format(data.status, data.statusText));
                    failHandler()
                });
            return request;
        };

        // overwrite a submitHandler, we need to do it for inline comments
        this.setHandleFormSubmit = function(callback) {
            this.handleFormSubmit = callback;
        };

        // default handler for for submit for main comments
        this.handleFormSubmit = function() {
            var text = self.cm.getValue();
            var status = self.getCommentStatus();

            if (text === "" && !status) {
                return;
            }

            var excludeCancelBtn = false;
            var submitEvent = true;
            self.setActionButtonsDisabled(true, excludeCancelBtn, submitEvent);
            self.cm.setOption("readOnly", true);
            var postData = {
                'text': text,
                'changeset_status': status,
                'csrf_token': CSRF_TOKEN
            };

            var submitSuccessCallback = function(o) {
                if (status) {
                    location.reload(true);
                } else {
                    $('#injected_page_comments').append(o.rendered_text);
                    self.resetCommentFormState();
                    bindDeleteCommentButtons();
                    timeagoActivate();
                }
            };
            var submitFailCallback = function(){
                self.resetCommentFormState(text)
            };
            self.submitAjaxPOST(
                self.submitUrl, postData, submitSuccessCallback, submitFailCallback);
        };

        this.previewSuccessCallback = function(o) {
            $(self.previewBoxSelector).html(o);
            $(self.previewBoxSelector).removeClass('unloaded');

            // swap buttons
            $(self.previewButton).hide();
            $(self.editButton).show();

            // unlock buttons
            self.setActionButtonsDisabled(false);
        };

        this.setActionButtonsDisabled = function(state, excludeCancelBtn, submitEvent) {
            excludeCancelBtn = excludeCancelBtn || false;
            submitEvent = submitEvent || false;

            $(this.editButton).prop('disabled', state);
            $(this.previewButton).prop('disabled', state);

            if (!excludeCancelBtn) {
                $(this.cancelButton).prop('disabled', state);
            }

            var submitState = state;
            if (!submitEvent && this.getCommentStatus() && !this.lineNo) {
                // if the value of commit review status is set, we allow
                // submit button, but only on Main form, lineNo means inline
                submitState = false
            }
            $(this.submitButton).prop('disabled', submitState);
            if (submitEvent) {
              $(this.submitButton).val(_gettext('Submitting...'));
            } else {
              $(this.submitButton).val(this.submitButtonText);
            }

        };

        // lock preview/edit/submit buttons on load, but exclude cancel button
        var excludeCancelBtn = true;
        this.setActionButtonsDisabled(true, excludeCancelBtn);

        // anonymous users don't have access to initialized CM instance
        if (this.cm !== undefined){
            this.cm.on('change', function(cMirror) {
                if (cMirror.getValue() === "") {
                    self.setActionButtonsDisabled(true, excludeCancelBtn)
                } else {
                    self.setActionButtonsDisabled(false, excludeCancelBtn)
                }
            });
        }

        $(this.editButton).on('click', function(e) {
            e.preventDefault();

            $(self.previewButton).show();
            $(self.previewContainer).hide();
            $(self.editButton).hide();
            $(self.editContainer).show();

        });

        $(this.previewButton).on('click', function(e) {
            e.preventDefault();
            var text = self.cm.getValue();

            if (text === "") {
                return;
            }

            var postData = {
                'text': text,
                'renderer': DEFAULT_RENDERER,
                'csrf_token': CSRF_TOKEN
            };

            // lock ALL buttons on preview
            self.setActionButtonsDisabled(true);

            $(self.previewBoxSelector).addClass('unloaded');
            $(self.previewBoxSelector).html(_gettext('Loading ...'));
            $(self.editContainer).hide();
            $(self.previewContainer).show();

            // by default we reset state of comment preserving the text
            var previewFailCallback = function(){
                self.resetCommentFormState(text)
            };
            self.submitAjaxPOST(
                self.previewUrl, postData, self.previewSuccessCallback, previewFailCallback);

        });

        $(this.submitForm).submit(function(e) {
            e.preventDefault();
            var allowedToSubmit = self.isAllowedToSubmit();
            if (!allowedToSubmit){
               return false;
            }
            self.handleFormSubmit();
        });

    }

    return CommentForm;
})();
