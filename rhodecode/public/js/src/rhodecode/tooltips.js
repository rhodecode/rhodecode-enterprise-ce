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

    setDeferredListeners: function(){
        $('body').on('mouseover', '.tooltip', yt.show_tip);
        $('body').on('mousemove', '.tooltip', yt.move_tip);
        $('body').on('mouseout', '.tooltip', yt.close_tip);
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
        yt.setDeferredListeners();
    },

    show_tip: function(e, el){
        e.stopPropagation();
        e.preventDefault();
        var el = e.data || e.currentTarget || el;
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
        var el = e.data || e.currentTarget || el;
        var movePos = [e.pageX, e.pageY];
        $(yt.tipBox).css('top', (movePos[1] + yt.offset[1]) + 'px')
        $(yt.tipBox).css('left', (movePos[0] + yt.offset[0]) + 'px')
    },

    close_tip: function(e, el){
        e.stopPropagation();
        e.preventDefault();
        var el = e.data || e.currentTarget || el;
        $(yt.tipBox).hide();
        $(el).attr('title', $(el).attr('tt_title'));
        $('#tip-box').hide();
    }
};

// activate tooltips
yt = TTIP.main;
if ($(document).data('activated-tooltips') !== '1'){
    $(document).ready(yt.init);
    $(document).data('activated-tooltips', '1');
}
