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

var _run_callbacks = function(callbacks){
    if (callbacks !== undefined){
        var _l = callbacks.length;
        for (var i=0;i<_l;i++){
            var func = callbacks[i];
            if(typeof(func)=='function'){
                try{
                    func();
                }catch (err){};
            }
        }
    }
};

var deleteNotification = function(url, notification_id,callbacks){
    var callback = function(o){
            var obj = $("#notification_"+notification_id);
            obj.remove();
            _run_callbacks(callbacks);
    };
    var postData = {'_method': 'delete', 'csrf_token': CSRF_TOKEN};
    var sUrl = url.replace('__NOTIFICATION_ID__',notification_id);
    var request = $.post(sUrl, postData)
                        .done(callback)
                        .fail(function(data, textStatus, errorThrown){
                            alert("Error while deleting notification.\nError code {0} ({1}). URL: {2}".format(data.status,data.statusText,$(this)[0].url));
                        });
};

var readNotification = function(url, notification_id,callbacks){
    var callback = function(o){
            var obj = $("#notification_"+notification_id);
            obj.removeClass('unread');
            var r_button = $('.read-notification',obj)[0];
            r_button.remove();

            _run_callbacks(callbacks);
    };
    var postData = {'_method': 'put', 'csrf_token': CSRF_TOKEN};
    var sUrl = url.replace('__NOTIFICATION_ID__',notification_id);
    var request = $.post(sUrl, postData)
                        .done(callback)
                        .fail(function(data, textStatus, errorThrown){
                            alert("Error while saving notification.\nError code {0} ({1}). URL: {2}".format(data.status,data.statusText,$(this)[0].url));
                        });
};
