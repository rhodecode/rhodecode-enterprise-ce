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

var onSuccessFollow = function(target){
    var f = $(target);
    var f_cnt = $('#current_followers_count');

    if(f.hasClass('follow')){
        f.removeClass('follow');
        f.addClass('following');
        f.attr('title', _gettext('Stop following this repository'));
        $(f).html(_gettext('Unfollow'));
        if(f_cnt.length){
            var cnt = Number(f_cnt.html())+1;
            f_cnt.html(cnt);
        }
    }
    else{
        f.removeClass('following');
        f.addClass('follow');
        f.attr('title', _gettext('Start following this repository'));
        $(f).html(_gettext('Follow'));
        if(f_cnt.length){
            var cnt = Number(f_cnt.html())-1;
            f_cnt.html(cnt);
        }
    }
};

// TODO:: check if the function is needed. 0 usage found
var toggleFollowingUser = function(target,follows_user_id,token,user_id){
    var args = {
        'follows_user_id': follows_user_id,
        'auth_token': token,
        'csrf_token': CSRF_TOKEN
    };
    if(user_id != undefined){
        args.user_id = user_id
    }
    ajaxPOST(pyroutes.url('toggle_following'), args, function(){
        onSuccessFollow(target);
    });
    return false;
};

var toggleFollowingRepo = function(target,follows_repo_id,token,user_id){
    var args = {
        'follows_repo_id': follows_repo_id,
        'auth_token': token,
        'csrf_token': CSRF_TOKEN
    };
    if(user_id != undefined){
        args.user_id = user_id
    }
    ajaxPOST(pyroutes.url('toggle_following'), args, function(){
        onSuccessFollow(target);
    });
    return false;
};
