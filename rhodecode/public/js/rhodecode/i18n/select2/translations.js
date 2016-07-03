// translate select2 components
select2Locales = {
   formatLoadMore: function(pageNumber) {
       return _gettext("Loading more results...");
   },
   formatSearching: function() {
       return _gettext("Searching...");
   },
   formatNoMatches: function() {
       return _gettext("No matches found");
   },
   formatAjaxError: function(jqXHR, textStatus, errorThrown) {
       return _gettext("Loading failed");
   },
   formatMatches: function(matches) {
       if (matches === 1) {
           return _gettext("One result is available, press enter to select it.");
       }
       return _gettext("{0} results are available, use up and down arrow keys to navigate.").format(matches);
   },
   formatInputTooShort: function(input, min) {
       var n = min - input.length;
       if (n === 1) {
           return _gettext("Please enter {0} or more character").format(n);
       }
       return _gettext("Please enter {0} or more characters").format(n);
   },
   formatInputTooLong: function(input, max) {
       var n = input.length - max;
       if (n === 1) {
           return _gettext("Please delete {0} character").format(n);
       }
       return _gettext("Please delete {0} characters").format(n);
   },
   formatSelectionTooBig: function(limit) {
       if (limit === 1) {
           return _gettext("You can only select {0} item").format(limit);
       }
       return _gettext("You can only select {0} items").format(limit);
   }
};

$.extend($.fn.select2.defaults, select2Locales);
