// # Copyright (C) 2016-2016  RhodeCode GmbH
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

i18nLog = Logger.get('i18n');

var _gettext = function (s) {
    if (_TM.hasOwnProperty(s)) {
        return _TM[s];
    }
    i18nLog.error(
        'String `' + s + '` was requested but cannot be ' +
        'found in translation table');
    return s
};

var _ngettext = function (singular, plural, n) {
    if (n === 1) {
        return _gettext(singular)
    }
    return _gettext(plural)
};
