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
 * Search file list
 */
// global reference to file-node filter
var _NODEFILTER = {};

var fileBrowserListeners = function(node_list_url, url_base){
  var n_filter = $('#node_filter').get(0);

  _NODEFILTER.filterTimeout = null;
  var nodes = null;

  _NODEFILTER.fetchNodes = function(callback) {
    $.ajax({url: node_list_url, headers: {'X-PARTIAL-XHR': true}})
      .done(function(data){
        nodes = data.nodes;
        if (callback) {
          callback();
        }
      })
      .fail(function(data){
        console.log('failed to load');
      });
  };

  _NODEFILTER.fetchNodesCallback = function() {
    $('#node_filter_box_loading').hide();
    $('#node_filter_box').removeClass('hidden').show();
    n_filter.focus();
    if ($('#node_filter').hasClass('init')){
      n_filter.value = '';
      $('#node_filter').removeClass('init');
    }
  };

  _NODEFILTER.initFilter = function(){
    $('#node_filter_box_loading').removeClass('hidden').show();
    $('#search_activate_id').hide();
    $('#search_deactivate_id').removeClass('hidden').show();
    $('#add_node_id').hide();
    _NODEFILTER.fetchNodes(_NODEFILTER.fetchNodesCallback);
  };

  _NODEFILTER.resetFilter = function(){
    $('#node_filter_box_loading').hide();
    $('#node_filter_box').hide();
    $('#search_activate_id').show();
    $('#search_deactivate_id').hide();
    $('#add_node_id').show();
    $('#tbody').show();
    $('#tbody_filtered').hide();
    $('#node_filter').val('');
  };

  _NODEFILTER.fuzzy_match = function(filepath, query) {
    var highlight = [];
    var order = 0;
    for (var i = 0; i < query.length; i++) {
      var match_position = filepath.indexOf(query[i]);
      if (match_position !== -1) {
        var prev_match_position = highlight[highlight.length-1];
        if (prev_match_position === undefined) {
          highlight.push(match_position);
        } else {
          var current_match_position = prev_match_position + match_position + 1;
          highlight.push(current_match_position);
          order = order + current_match_position - prev_match_position;
        }
        filepath = filepath.substring(match_position+1);
      } else {
        return false;
      }
    }
    return {'order': order,
            'highlight': highlight};
  };

  _NODEFILTER.sortPredicate = function(a, b) {
    if (a.order < b.order) return -1;
    if (a.order > b.order) return 1;
    if (a.filepath < b.filepath) return -1;
    if (a.filepath > b.filepath) return 1;
    return 0;
  };

  _NODEFILTER.updateFilter = function(elem, e) {
    return function(){
      // Reset timeout
      _NODEFILTER.filterTimeout = null;
      var query = elem.value.toLowerCase();
      var match = [];
      var matches_max = 20;
      if (query !== ""){
        var results = [];
        for(var k=0;k<nodes.length;k++){
          var result = _NODEFILTER.fuzzy_match(
              nodes[k].name.toLowerCase(), query);
          if (result) {
            result.type = nodes[k].type;
            result.filepath = nodes[k].name;
            results.push(result);
          }
        }
        results = results.sort(_NODEFILTER.sortPredicate);
        var limit = matches_max;
        if (results.length < matches_max) {
          limit = results.length;
        }
        for (var i=0; i<limit; i++){
          if(query && results.length > 0){
            var n = results[i].filepath;
            var t = results[i].type;
            var n_hl = n.split("");
            var pos = results[i].highlight;
            for (var j = 0; j < pos.length; j++) {
                n_hl[pos[j]] = "<em>" + n_hl[pos[j]] + "</em>";
            }
            n_hl = n_hl.join("");
            var new_url = url_base.replace('__FPATH__',n);

            var typeObj = {
              dir: 'icon-folder browser-dir',
              file: 'icon-file browser-file'
            };
            var typeIcon = '<i class="{0}"></i>'.format(typeObj[t]);
            match.push('<tr class="browser-result"><td><a class="browser-{0} pjax-link" href="{1}">{2}{3}</a></td><td colspan="5"></td></tr>'.format(t,new_url,typeIcon, n_hl));
          }
        }
        if(results.length > limit){
          var truncated_count = results.length - matches_max;
          if (truncated_count === 1) {
            match.push('<tr><td>{0} {1}</td><td colspan="5"></td></tr>'.format(truncated_count, _TM['truncated result']));
          } else {
            match.push('<tr><td>{0} {1}</td><td colspan="5"></td></tr>'.format(truncated_count, _TM['truncated results']));
          }
        }
      }
      if (query !== ""){
        $('#tbody').hide();
        $('#tbody_filtered').show();

        if (match.length === 0){
          match.push('<tr><td>{0}</td><td colspan="5"></td></tr>'.format(_TM['No matching files']));
        }
        $('#tbody_filtered').html(match.join(""));
      }
      else{
        $('#tbody').show();
        $('#tbody_filtered').hide();
      }

    };
  };

  var scrollDown = function(element){
    var elementBottom = element.offset().top + $(element).outerHeight();
    var windowBottom = window.innerHeight + $(window).scrollTop();
    if (elementBottom > windowBottom) {
      var offset = elementBottom - window.innerHeight;
      $('html,body').scrollTop(offset);
      return false;
    }
    return true;
  };

  var scrollUp = function(element){
    if (element.offset().top < $(window).scrollTop()) {
      $('html,body').scrollTop(element.offset().top);
      return false;
    }
    return true;
  };

  $('#filter_activate').click(function() {
    _NODEFILTER.initFilter();
  });

  $('#filter_deactivate').click(function() {
    _NODEFILTER.resetFilter();
  });

  $(n_filter).click(function() {
    if ($('#node_filter').hasClass('init')){
      n_filter.value = '';
      $('#node_filter').removeClass('init');
    }
  });

  $(n_filter).keydown(function(e) {
    if (e.keyCode === 40){ // Down
      if ($('.browser-highlight').length === 0){
        $('.browser-result').first().addClass('browser-highlight');
      } else {
        var next = $('.browser-highlight').next();
        if (next.length !== 0) {
          $('.browser-highlight').removeClass('browser-highlight');
          next.addClass('browser-highlight');
        }
      }
      scrollDown($('.browser-highlight'));
    }
    if (e.keyCode === 38){ // Up
      e.preventDefault();
      if ($('.browser-highlight').length !== 0){
        var next = $('.browser-highlight').prev();
        if (next.length !== 0) {
          $('.browser-highlight').removeClass('browser-highlight');
          next.addClass('browser-highlight');
        }
      }
      scrollUp($('.browser-highlight'));
    }
    if (e.keyCode === 13){ // Enter
      if ($('.browser-highlight').length !== 0){
        var url = $('.browser-highlight').find('.pjax-link').attr('href');
        $.pjax({url: url, container: '#pjax-container', timeout: pjaxTimeout});
      }
    }
    if (e.keyCode === 27){ // Esc
      _NODEFILTER.resetFilter();
      $('html,body').scrollTop(0);
    }
  });
  var capture_keys = [40, 38, 39, 37, 13, 27];
  $(n_filter).keyup(function(e) {
    if ($.inArray(e.keyCode, capture_keys) === -1){
      clearTimeout(_NODEFILTER.filterTimeout);
      _NODEFILTER.filterTimeout = setTimeout(_NODEFILTER.updateFilter(n_filter, e),200);
    }
  });
};

var getIdentNode = function(n){
  // iterate through nodes until matched interesting node
  if (typeof n === 'undefined'){
    return -1;
  }
  if(typeof n.id !== "undefined" && n.id.match('L[0-9]+')){
    return n;
  }
  else{
    return getIdentNode(n.parentNode);
  }
};

var getSelectionLink = function(e) {
  // get selection from start/to nodes
  if (typeof window.getSelection !== "undefined") {
    s = window.getSelection();

    from = getIdentNode(s.anchorNode);
    till = getIdentNode(s.focusNode);

    f_int = parseInt(from.id.replace('L',''));
    t_int = parseInt(till.id.replace('L',''));

    if (f_int > t_int){
      // highlight from bottom
      offset = -35;
      ranges = [t_int,f_int];
    }
    else{
      // highligth from top
      offset = 35;
      ranges = [f_int,t_int];
    }
    // if we select more than 2 lines
    if (ranges[0] !== ranges[1]){
      if($('#linktt').length === 0){
        hl_div = document.createElement('div');
        hl_div.id = 'linktt';
      }
      hl_div.innerHTML = '';

      anchor = '#L'+ranges[0]+'-'+ranges[1];
      var link = document.createElement('a');
      link.href = location.href.substring(0,location.href.indexOf('#'))+anchor;
      link.innerHTML = _TM['Selection link'];
      hl_div.appendChild(link);
      $('#codeblock').append(hl_div);

      var xy = $(till).offset();
      $('#linktt').addClass('hl-tip-box tip-box');
      $('#linktt').offset({top: xy.top + offset, left: xy.left});
      $('#linktt').css('visibility','visible');
    }
    else{
      $('#linktt').css('visibility','hidden');
    }
  }
};
