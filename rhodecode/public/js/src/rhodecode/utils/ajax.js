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
* turns objects into GET query string
*/
var toQueryString = function(o) {
  if(typeof o !== 'object') {
    return false;
  }
  var _p, _qs = [];
  for(_p in o) {
    _qs.push(encodeURIComponent(_p) + '=' + encodeURIComponent(o[_p]));
  }
  return _qs.join('&');
};

/**
* ajax call wrappers
*/
var ajaxGET = function(url, success) {
  var sUrl = url;
  var request = $.ajax({url: sUrl, headers: {'X-PARTIAL-XHR': true}})
  .done(function(data){
    success(data);
  })
  .fail(function(data, textStatus, xhr){
    alert("error processing request: " + textStatus);
  });
  return request;
};
var ajaxPOST = function(url,postData,success) {
  var sUrl = url;
  var postData = toQueryString(postData);
  var request = $.ajax({type: 'POST', data: postData, url: sUrl,
    headers: {'X-PARTIAL-XHR': true}})
  .done(function(data){
    success(data);
  })
  .fail(function(data, textStatus, xhr){
    alert("error processing request: " + textStatus);
  });
  return request;
};
