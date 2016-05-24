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
 * TOOLTIP IMPL.
 */

var TTIP = {};

TTIP.main = {
    offset:     [15,15],
    maxWidth:   600,

    set_listeners: function(tt){
        $(tt).mouseover(tt, yt.show_tip);
        $(tt).mousemove(tt, yt.move_tip);
        $(tt).mouseout(tt, yt.close_tip);
    },

    init: function(){
        $('#tip-box').remove();
        yt.tipBox = document.createElement('div');
        document.body.appendChild(yt.tipBox);
        yt.tipBox.id = 'tip-box';

        $(yt.tipBox).hide();
        $(yt.tipBox).css('position', 'absolute');
        if(yt.maxWidth !== null){
          $(yt.tipBox).css('max-width', yt.maxWidth+'px');
        }

        var tooltips = $('.tooltip');
        var ttLen = tooltips.length;

        for(i=0;i<ttLen;i++){
            yt.set_listeners(tooltips[i]);
        }
    },

    show_tip: function(e, el){
        e.stopPropagation();
        e.preventDefault();
        var el = e.data || el;
        if(el.tagName.toLowerCase() === 'img'){
            yt.tipText = el.alt ? el.alt : '';
        } else {
            yt.tipText = el.title ? el.title : '';
        }

        if(yt.tipText !== ''){
            // save org title
            $(el).attr('tt_title', yt.tipText);
            // reset title to not show org tooltips
            $(el).attr('title', '');

            yt.tipBox.innerHTML = yt.tipText;
            $(yt.tipBox).show();
        }
    },

    move_tip: function(e, el){
        e.stopPropagation();
        e.preventDefault();
        var el = e.data || el;
        var movePos = [e.pageX, e.pageY];
        $(yt.tipBox).css('top', (movePos[1] + yt.offset[1]) + 'px')
        $(yt.tipBox).css('left', (movePos[0] + yt.offset[0]) + 'px')
    },

    close_tip: function(e, el){
        e.stopPropagation();
        e.preventDefault();
        var el = e.data || el;
        $(yt.tipBox).hide();
        $(el).attr('title', $(el).attr('tt_title'));
        $('#tip-box').hide();
    }
};

/**
 * tooltip activate
 */
var tooltip_activate = function(){
    yt = TTIP.main;
    $(document).ready(yt.init);
};

/**
 * show changeset tooltip
 */
var show_changeset_tooltip = function(){
    $('.lazy-cs').mouseover(function(e) {
        var target = e.currentTarget;
        var rid = $(target).attr('raw_id');
        var repo_name = $(target).attr('repo_name');
        var ttid = 'tt-'+rid;
        var success = function(o){
            $(target).addClass('tooltip')
            $(target).attr('title', o['message']);
            TTIP.main.show_tip(e, target);
        }
        if(rid && !$(target).hasClass('tooltip')){
            $(target).attr('id', ttid);
            $(target).attr('title', _TM['loading ...']);
            TTIP.main.set_listeners(target);
            TTIP.main.show_tip(e, target);
            var url = pyroutes.url('changeset_info', {"repo_name":repo_name, "revision": rid});
            ajaxGET(url, success);
        }
    });
};
