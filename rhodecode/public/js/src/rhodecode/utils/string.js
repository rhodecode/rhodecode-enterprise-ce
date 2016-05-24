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
 * INJECT .format function into String
 * Usage: "My name is {0} {1}".format("Johny","Bravo")
 * Return "My name is Johny Bravo"
 * Inspired by https://gist.github.com/1049426
 */
String.prototype.format = function() {

  function format() {
    var str = this;
    var len = arguments.length+1;
    var safe = undefined;
    var arg = undefined;

    // For each {0} {1} {n...} replace with the argument in that position.  If
    // the argument is an object or an array it will be stringified to JSON.
    for (var i=0; i < len; arg = arguments[i++]) {
      safe = typeof arg === 'object' ? JSON.stringify(arg) : arg;
      str = str.replace(new RegExp('\\{'+(i-1)+'\\}', 'g'), safe);
    }
    return str;
  }

  // Save a reference of what may already exist under the property native.
  // Allows for doing something like: if("".format.native) { /* use native */ }
  format.native = String.prototype.format;

  // Replace the prototype property
  return format;
}();

String.prototype.strip = function(char) {
  if(char === undefined){
      char = '\\s';
  }
  return this.replace(new RegExp('^'+char+'+|'+char+'+$','g'), '');
};

String.prototype.lstrip = function(char) {
  if(char === undefined){
      char = '\\s';
  }
  return this.replace(new RegExp('^'+char+'+'),'');
};

String.prototype.rstrip = function(char) {
  if(char === undefined){
      char = '\\s';
  }
  return this.replace(new RegExp(''+char+'+$'),'');
};

String.prototype.capitalizeFirstLetter = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};


/**
 * Escape html characters in string
 */
var entityMap = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': '&quot;',
  "'": '&#39;',
  "/": '&#x2F;'
};

function escapeHtml(string) {
  return String(string).replace(/[&<>"'\/]/g, function (s) {
    return entityMap[s];
  });
}

/** encode/decode html special chars**/
var htmlEnDeCode = (function() {
  var charToEntityRegex,
      entityToCharRegex,
      charToEntity,
      entityToChar;

  function resetCharacterEntities() {
    charToEntity = {};
    entityToChar = {};
    // add the default set
    addCharacterEntities({
        '&amp;'     :   '&',
        '&gt;'      :   '>',
        '&lt;'      :   '<',
        '&quot;'    :   '"',
        '&#39;'     :   "'"
    });
  }

  function addCharacterEntities(newEntities) {
    var charKeys = [],
        entityKeys = [],
        key, echar;
    for (key in newEntities) {
        echar = newEntities[key];
        entityToChar[key] = echar;
        charToEntity[echar] = key;
        charKeys.push(echar);
        entityKeys.push(key);
    }
    charToEntityRegex = new RegExp('(' + charKeys.join('|') + ')', 'g');
    entityToCharRegex = new RegExp('(' + entityKeys.join('|') + '|&#[0-9]{1,5};' + ')', 'g');
  }

  function htmlEncode(value){
    var htmlEncodeReplaceFn = function(match, capture) {
      return charToEntity[capture];
    };

    return (!value) ? value : String(value).replace(charToEntityRegex, htmlEncodeReplaceFn);
  }

  function htmlDecode(value) {
    var htmlDecodeReplaceFn = function(match, capture) {
        return (capture in entityToChar) ? entityToChar[capture] : String.fromCharCode(parseInt(capture.substr(2), 10));
    };

    return (!value) ? value : String(value).replace(entityToCharRegex, htmlDecodeReplaceFn);
  }

  resetCharacterEntities();

  return {
    htmlEncode: htmlEncode,
    htmlDecode: htmlDecode
  };
})();
