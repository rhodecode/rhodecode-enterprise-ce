// translate select2 components
select2Locales = {
   formatLoadMore: function(pageNumber) {
       return _TM["Loading more results..."];
   },
   formatSearching: function() {
       return _TM["Searching..."];
   },
   formatNoMatches: function() {
       return _TM["No matches found"];
   },
   formatAjaxError: function(jqXHR, textStatus, errorThrown) {
       return _TM["Loading failed"];
   },
   formatMatches: function(matches) {
       if (matches === 1) {
           return _TM["One result is available, press enter to select it."];
       }
       return _TM["{0} results are available, use up and down arrow keys to navigate."].format(matches);
   },
   formatInputTooShort: function(input, min) {
       var n = min - input.length;
       return "Please enter {0} or more character".format(n) + (n === 1 ? "" : "s");
   },
   formatInputTooLong: function(input, max) {
       var n = input.length - max;
       return "Please delete {0} character".format(n) + (n === 1 ? "" : "s");
   },
   formatSelectionTooBig: function(limit) {
       return "You can only select {0} item".format(limit) + (limit === 1 ? "" : "s");
   }
};

$.extend($.fn.select2.defaults, select2Locales);
