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

// creates new permission input box with autocomplete
var addNewPermInput = function(node, permission_type, cur_used_id){
    var _html = '<tr class="new_members" id="add_perm_input_{0}">'+
                '<td class="td-radio"><input type="radio" value="{1}.none"  name="perm_new_member_perm_{0}"></td>'+
                '<td class="td-radio"><input type="radio" value="{1}.read"  name="perm_new_member_perm_{0}" checked="checked"></td>'+
                '<td class="td-radio"><input type="radio" value="{1}.write" name="perm_new_member_perm_{0}"></td>'+
                '<td class="td-radio"><input type="radio" value="{1}.admin" name="perm_new_member_perm_{0}"></td>'+
                '<td class="ac">'+
                '    <div class="perm_ac" id="perm_ac_{0}">'+
                '        <input class="ac-input" id="perm_new_member_name_{0}" name="perm_new_member_name_{0}" value="" type="text" autocomplete="off">'+
                '        <input type="hidden" id="perm_new_member_id_{0}" name="perm_new_member_id_{0}" value="">'+
                '        <input type="hidden" id="perm_new_member_type_{0}" name="perm_new_member_type_{0}" value="">'+
                '        <div id="perm_container_{0}"></div>'+
                '    </div>'+
                '</td>'+
                '<td></td>'+
                '</tr>';
    var _next_id = 'new'+$('.new_members').length;
    _html = _html.format(_next_id, permission_type);
    $('#add_perm_input').before(_html);

    //autocomplete widget
    $('#perm_new_member_name_{0}'.format(_next_id)).autocomplete({
        serviceUrl: pyroutes.url('user_autocomplete_data'),
        minChars:2,
        maxHeight:400,
        width:300,
        deferRequestBy: 300, //miliseconds
        showNoSuggestionNotice: true,
        params: { user_id: cur_used_id, user_groups:true },
        formatResult: autocompleteFormatResult,
        lookupFilter: autocompleteFilterResult,
        onSelect: function(element, suggestion){
            $('#perm_new_member_id_{0}'.format(_next_id)).val(suggestion['id']);
            $('#perm_new_member_type_{0}'.format(_next_id)).val(suggestion['value_type']);
        }
    });

};

// marks current input for "revoke" action
var markRevokePermInput = function(node, permission_type){
    var obj_type = $(node).attr('member_type');
    var obj_id = $(node).attr('member');
    var tr = $(node).parent().parent();

    if(!tr.hasClass('to-delete')){
        tr.css({"text-decoration":"line-through", "opacity": 0.5});
        tr.addClass('to-delete');
        // inject special hidden input that we mark the user for deletion
        tr.append($('<input type="hidden" name="perm_del_member_id_{0}" value="{1}"/>'.format(obj_id, obj_id)));
        tr.append($('<input type="hidden" name="perm_del_member_type_{0}" value="{1}"/>'.format(obj_id, obj_type)));
    }
};
