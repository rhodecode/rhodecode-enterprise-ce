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


var topics = {};
jQuery.Topic = function (id) {
    var callbacks, method,
        topic = id && topics[id];

    if (!topic) {
        callbacks = jQuery.Callbacks();
        topic = {
            unhandledData: [],
            publish: callbacks.fire,
            prepare: function(){
                for(var i=0; i< arguments.length; i++){
                    this.unhandledData.push(arguments[i]);
                }
            },
            prepareOrPublish: function(){
                if (callbacks.has() === true){
                    this.publish.apply(this, arguments);
                }
                else{
                    this.prepare.apply(this, arguments);
                }
            },
            processPrepared: function(){
                var data = this.unhandledData;
                this.unhandledData = [];
                for(var i=0; i< data.length; i++){
                    this.publish(data[i]);
                }
            },
            subscribe: callbacks.add,
            unsubscribe: callbacks.remove,
            callbacks: callbacks
        };
        if (id) {
            topics[id] = topic;
        }
    }
    return topic;
};
