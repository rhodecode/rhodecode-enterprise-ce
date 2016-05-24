/* COMMON */
var select2RefFilterResults  = function(queryTerm, data) {
  var filteredData = {results: []};
  //filter results
  $.each(data.results, function() {
    var section = this.text;
    var children = [];
    $.each(this.children, function() {
      if (queryTerm.length === 0 || this.text.toUpperCase().indexOf(queryTerm.toUpperCase()) >= 0) {
        children.push(this);
      }
    });

    if (children.length > 0) {
      filteredData.results.push({
        'text': section,
        'children': children
      });
    }
  });

  return filteredData
};


var select2RefBaseSwitcher = function(targetElement, loadUrl, initialData){
  var formatResult = function(result, container, query) {
    return formatSelect2SelectionRefs(result);
  };

  var formatSelection = function(data, container) {
    return formatSelect2SelectionRefs(data);
  };

  $(targetElement).select2({
    cachedDataSource: {},
    dropdownAutoWidth: true,
    formatResult: formatResult,
    width: "resolve",
    containerCssClass: "drop-menu",
    dropdownCssClass: "drop-menu-dropdown",
    query: function(query) {
      var self = this;
      var cacheKey = '__ALLREFS__';
      var cachedData = self.cachedDataSource[cacheKey];
      if (cachedData) {
        var data = select2RefFilterResults(query.term, cachedData);
        query.callback({results: data.results});
      } else {
        $.ajax({
          url: loadUrl,
          data: {},
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            self.cachedDataSource[cacheKey] = data;
            query.callback({results: data.results});
          }
        });
      }
    },

    initSelection: function(element, callback) {
      callback(initialData);
    },

    formatSelection: formatSelection
  });

};

/* WIDGETS */
var select2RefSwitcher = function(targetElement, initialData) {
  var loadUrl = pyroutes.url('repo_refs_data',
    {'repo_name': templateContext.repo_name});
  select2RefBaseSwitcher(targetElement, loadUrl, initialData);
};

var select2FileHistorySwitcher = function(targetElement, initialData, state) {
  var loadUrl = pyroutes.url('files_history_home',
    {'repo_name': templateContext.repo_name, 'revision': state.rev,
     'f_path': state.f_path});
  select2RefBaseSwitcher(targetElement, loadUrl, initialData);
};
