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
RhodeCode JS Files
**/

if (typeof console == "undefined" || typeof console.log == "undefined"){
    console = { log: function() {} }
}

// TODO: move the following function to submodules

/**
 * show more
 */
var show_more_event = function(){
  $('table .show_more').click(function(e) {
    var cid = e.target.id.substring(1);
    var button = $(this);
    if (button.hasClass('open')) {
      $('#'+cid).hide();
      button.removeClass('open');
    } else {
      $('#'+cid).show();
      button.addClass('open one');
    }
  });
};

var compare_radio_buttons = function(repo_name, compare_ref_type){
    $('#compare_action').on('click', function(e){
        e.preventDefault();

        var source = $('input[name=compare_source]:checked').val();
        var target = $('input[name=compare_target]:checked').val();
        if(source && target){
            var url_data = {
                repo_name: repo_name,
                source_ref: source,
                source_ref_type: compare_ref_type,
                target_ref: target,
                target_ref_type: compare_ref_type,
                merge: 1
            };
            window.location = pyroutes.url('compare_url', url_data);
        }
    });
    $('.compare-radio-button').on('click', function(e){
        var source = $('input[name=compare_source]:checked').val();
        var target = $('input[name=compare_target]:checked').val();
        if(source && target){
            $('#compare_action').removeAttr("disabled");
            $('#compare_action').removeClass("disabled");
        }
    })
};

var showRepoSize = function(target, repo_name, commit_id, callback) {
    var container = $('#' + target);
    var url = pyroutes.url('repo_stats',
      {"repo_name": repo_name, "commit_id": commit_id});

    if (!container.hasClass('loaded')) {
        $.ajax({url: url})
            .complete(function (data) {
                var responseJSON = data.responseJSON;
                container.addClass('loaded');
                container.html(responseJSON.size);
                callback(responseJSON.code_stats)
            })
            .fail(function (data) {
                console.log('failed to load repo stats');
            });
    }

};

var showRepoStats = function(target, data){
    var container = $('#' + target);

    if (container.hasClass('loaded')) {
        return
    }

    var total = 0;
    var no_data = true;
    var tbl = document.createElement('table');
    tbl.setAttribute('class', 'trending_language_tbl');

    $.each(data, function(key, val){
        total += val.count;
    });

    var sortedStats = [];
    for (var obj in data){
        sortedStats.push([obj, data[obj]])
    }
    var sortedData = sortedStats.sort(function (a, b) {
        return b[1].count - a[1].count
    });
    var cnt = 0;
    $.each(sortedData, function(idx, val){
        cnt += 1;
        no_data = false;

        var hide = cnt > 2;
        var tr = document.createElement('tr');
        if (hide) {
            tr.setAttribute('style', 'display:none');
            tr.setAttribute('class', 'stats_hidden');
        }

        var key = val[0];
        var obj = {"desc": val[1].desc, "count": val[1].count};

        var percentage = Math.round((obj.count / total * 100), 2);

        var td1 = document.createElement('td');
        td1.width = 300;
        var trending_language_label = document.createElement('div');
        trending_language_label.innerHTML = obj.desc + " (.{0})".format(key);
        td1.appendChild(trending_language_label);

        var td2 = document.createElement('td');
        var trending_language = document.createElement('div');
        var nr_files = obj.count +" "+ _ngettext('file', 'files', obj.count);

        trending_language.title = key + " " + nr_files;

        trending_language.innerHTML = "<span>" + percentage + "% " + nr_files
                + "</span><b>" + percentage + "% " + nr_files + "</b>";

        trending_language.setAttribute("class", 'trending_language');
        $('b', trending_language)[0].style.width = percentage + "%";
        td2.appendChild(trending_language);

        tr.appendChild(td1);
        tr.appendChild(td2);
        tbl.appendChild(tr);
        if (cnt == 3) {
            var show_more = document.createElement('tr');
            var td = document.createElement('td');
            lnk = document.createElement('a');

            lnk.href = '#';
            lnk.innerHTML = _gettext('Show more');
            lnk.id = 'code_stats_show_more';
            td.appendChild(lnk);

            show_more.appendChild(td);
            show_more.appendChild(document.createElement('td'));
            tbl.appendChild(show_more);
        }
    });

    $(container).html(tbl);
    $(container).addClass('loaded');

    $('#code_stats_show_more').on('click', function (e) {
        e.preventDefault();
        $('.stats_hidden').each(function (idx) {
            $(this).css("display", "");
        });
        $('#code_stats_show_more').hide();
    });

};


// Toggle Collapsable Content
function collapsableContent() {

    $('.collapsable-content').not('.no-hide').hide();

    $('.btn-collapse').unbind(); //in case we've been here before
    $('.btn-collapse').click(function() {
        var button = $(this);
        var togglename = $(this).data("toggle");
        $('.collapsable-content[data-toggle='+togglename+']').toggle();
        if ($(this).html()=="Show Less")
            $(this).html("Show More");
        else
            $(this).html("Show Less");
    });
};

var timeagoActivate = function() {
    $("time.timeago").timeago();
};

// Formatting values in a Select2 dropdown of commit references
var formatSelect2SelectionRefs = function(commit_ref){
  var tmpl = '';
  if (!commit_ref.text || commit_ref.type === 'sha'){
    return commit_ref.text;
  }
  if (commit_ref.type === 'branch'){
    tmpl = tmpl.concat('<i class="icon-branch"></i> ');
  } else if (commit_ref.type === 'tag'){
    tmpl = tmpl.concat('<i class="icon-tag"></i> ');
  } else if (commit_ref.type === 'book'){
    tmpl = tmpl.concat('<i class="icon-bookmark"></i> ');
  }
  return tmpl.concat(commit_ref.text);
};

// takes a given html element and scrolls it down offset pixels
function offsetScroll(element, offset){
    setTimeout(function(){
        console.log(element);
        var location = element.offset().top;
        // some browsers use body, some use html
        $('html, body').animate({ scrollTop: (location - offset) });
    }, 100);
}

/**
 * global hooks after DOM is loaded
 */
$(document).ready(function() {
    firefoxAnchorFix();

    $('.navigation a.menulink').on('click', function(e){
        var menuitem = $(this).parent('li');
        if (menuitem.hasClass('open')) {
            menuitem.removeClass('open');
        } else {
            menuitem.addClass('open');
            $(document).on('click', function(event) {
                if (!$(event.target).closest(menuitem).length) {
                    menuitem.removeClass('open');
                }
            });
        }
    });
    $('.compare_view_files').on(
        'mouseenter mouseleave', 'tr.line .lineno a',function(event) {
            if (event.type === "mouseenter") {
                $(this).parents('tr.line').addClass('hover');
            } else {
                $(this).parents('tr.line').removeClass('hover');
            }
        });

    $('.compare_view_files').on(
        'mouseenter mouseleave', 'tr.line .add-comment-line a',function(event){
            if (event.type === "mouseenter") {
                $(this).parents('tr.line').addClass('commenting');
            } else {
                $(this).parents('tr.line').removeClass('commenting');
            }
        });

    $('.compare_view_files').on(
        'click', 'tr.line .lineno a',function(event) {
            if ($(this).text() != ""){
                $('tr.line').removeClass('selected');
                $(this).parents("tr.line").addClass('selected');

                // Replace URL without jumping to it if browser supports.
                // Default otherwise
                if (history.pushState) {
                    var new_location = location.href;
                    if (location.hash){
                        new_location = new_location.replace(location.hash, "");
                    }

                    // Make new anchor url
                    var new_location = new_location+$(this).attr('href');
                    history.pushState(true, document.title, new_location);

                    return false;
                }
            }
        });

    $('.compare_view_files').on(
        'click', 'tr.line .add-comment-line a',function(event) {
            var tr = $(event.currentTarget).parents('tr.line')[0];
            injectInlineForm(tr);
            return false;
        });

    $('.collapse_file').on('click', function(e) {
        e.stopPropagation();
        if ($(e.target).is('a')) { return; }
        var node = $(e.delegateTarget).first();
        var icon = $($(node.children().first()).children().first());
        var id = node.attr('fid');
        var target = $('#'+id);
        var tr = $('#tr_'+id);
        var diff = $('#diff_'+id);
        if(node.hasClass('expand_file')){
            node.removeClass('expand_file');
            icon.removeClass('expand_file_icon');
            node.addClass('collapse_file');
            icon.addClass('collapse_file_icon');
            diff.show();
            tr.show();
            target.show();
        } else {
            node.removeClass('collapse_file');
            icon.removeClass('collapse_file_icon');
            node.addClass('expand_file');
            icon.addClass('expand_file_icon');
            diff.hide();
            tr.hide();
            target.hide();
        }
    });

    $('#expand_all_files').click(function() {
        $('.expand_file').each(function() {
            var node = $(this);
            var icon = $($(node.children().first()).children().first());
            var id = $(this).attr('fid');
            var target = $('#'+id);
            var tr = $('#tr_'+id);
            var diff = $('#diff_'+id);
            node.removeClass('expand_file');
            icon.removeClass('expand_file_icon');
            node.addClass('collapse_file');
            icon.addClass('collapse_file_icon');
            diff.show();
            tr.show();
            target.show();
        });
    });

    $('#collapse_all_files').click(function() {
        $('.collapse_file').each(function() {
            var node = $(this);
            var icon = $($(node.children().first()).children().first());
            var id = $(this).attr('fid');
            var target = $('#'+id);
            var tr = $('#tr_'+id);
            var diff = $('#diff_'+id);
            node.removeClass('collapse_file');
            icon.removeClass('collapse_file_icon');
            node.addClass('expand_file');
            icon.addClass('expand_file_icon');
            diff.hide();
            tr.hide();
            target.hide();
        });
    });

    // Mouse over behavior for comments and line selection

    // Select the line that comes from the url anchor
    // At the time of development, Chrome didn't seem to support jquery's :target
    // element, so I had to scroll manually
    if (location.hash) {
        var splitIx = location.hash.indexOf('/?/');
        if (splitIx !== -1){
            var loc  = location.hash.slice(0, splitIx);
            var remainder = location.hash.slice(splitIx + 2);
        }
        else{
            var loc  = location.hash;
            var remainder = null;
        }
        if (loc.length > 1){
            var lineno = $(loc+'.lineno');
            if (lineno.length > 0){
                var tr = lineno.parents('tr.line');
                tr.addClass('selected');

                tr[0].scrollIntoView();

                $.Topic('/ui/plugins/code/anchor_focus').prepareOrPublish({
                    tr:tr,
                    remainder:remainder});
            }
        }
    }

    collapsableContent();
});
