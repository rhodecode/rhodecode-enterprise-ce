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
 *  autocomplete formatter that uses gravatar
 * */
var autocompleteFormatResult = function(data, value, org_formatter) {
  var value_display = data.value_display;
  var escapeRegExChars = function (value) {
    return value.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
  };
  var pattern = '(' + escapeRegExChars(value) + ')';
  value_display = value_display.replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>');
  var tmpl = '<div class="ac-container-wrap"><img class="gravatar" src="{0}"/>{1}</div>';
  if (data.icon_link === "") {
    tmpl = '<div class="ac-container-wrap">{0}</div>';
    return tmpl.format(value_display);
  }
  return tmpl.format(data.icon_link, value_display);
};

/**
 * autocomplete filter that uses display value to filter
 */
var autocompleteFilterResult = function (suggestion, originalQuery, queryLowerCase) {
  return suggestion.value_display.toLowerCase().indexOf(queryLowerCase) !== -1;
};
