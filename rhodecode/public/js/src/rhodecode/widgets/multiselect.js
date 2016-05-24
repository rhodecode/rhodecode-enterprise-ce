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
 * Multi select widget
 */
var MultiSelectWidget = function(selected_id, available_id, form_id){
  // definition of containers ID's
  var selected_container = selected_id;
  var available_container = available_id;
  // temp container for selected storage.
  var cache = [];
  var av_cache = [];
  var c = $('#'+selected_container).get(0);
  var ac = $('#'+available_container).get(0);
  // get only selected options for further fullfilment
  for (var i = 0; node = c.options[i]; i++){
    if (node.selected){
      // push selected to my temp storage left overs :)
      cache.push(node);
    }
  }
  // get all available options to cache
  for (i = 0; node = ac.options[i]; i++){
    // push selected to my temp storage left overs :)
    av_cache.push(node);
  }
  // fill available only with those not in chosen
  ac.options.length = 0;
  tmp_cache = [];

  for (i = 0; node = av_cache[i]; i++){
    var add = true;
    for (var i2 = 0; node_2 = cache[i2]; i2++){
      if (node.value === node_2.value){
        add=false;
        break;
      }
    }
    if(add){
      tmp_cache.push(new Option(node.text, node.value, false, false));
    }
  }
  for (i = 0; node = tmp_cache[i]; i++){
    ac.options[i] = node;
  }
  function prompts_action_callback(e){
    var chosen  = $('#'+selected_container).get(0);
    var available = $('#'+available_container).get(0);
    // get checked and unchecked options from field
    function get_checked(from_field){
      // temp container for storage.
      var sel_cache = [];
      var oth_cache = [];

      for (i = 0; node = from_field.options[i]; i++){
        if(node.selected){
          // push selected fields :)
          sel_cache.push(node);
        }
        else {
          oth_cache.push(node);
        }
      }
      return [sel_cache,oth_cache];
    }
    // fill the field with given options
    function fill_with(field,options){
      // clear firtst
      field.options.length=0;
      for (var i = 0; node = options[i]; i++){
        field.options[i] = new Option(node.text, node.value, false, false);
      }
    }
    // adds to current field
    function add_to(field,options){
      for (i = 0; node = options[i]; i++){
        field.appendChild(new Option(node.text, node.value, false, false));
      }
    }
    // add action
    if (this.id ==='add_element'){
      var c = get_checked(available);
      add_to(chosen,c[0]);
      fill_with(available,c[1]);
    }
    // remove action
    if (this.id ==='remove_element'){
      c = get_checked(chosen);
      add_to(available,c[0]);
      fill_with(chosen,c[1]);
    }
    // add all elements
    if(this.id === 'add_all_elements'){
      for (i=0; node = available.options[i]; i++){
        chosen.appendChild(new Option(node.text, node.value, false, false));
      }
      available.options.length = 0;
    }
    // remove all elements
    if (this.id === 'remove_all_elements'){
      for (i=0; node = chosen.options[i]; i++){
        available.appendChild(new Option(node.text, node.value, false, false));
      }
      chosen.options.length = 0;
    }
  }
  $('#add_element, #remove_element, #add_all_elements, #remove_all_elements').click(prompts_action_callback);
  if (form_id !== undefined) {
    $('#'+form_id).submit(function(){
      var chosen  = $('#'+selected_container).get(0);
      for (i = 0; i < chosen.options.length; i++) {
        chosen.options[i].selected = 'selected';
      }
    });
  }
};
