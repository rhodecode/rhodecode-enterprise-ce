var FlavoredCheckbox = (function($) {

"use strict";

// makes Markdown FlavoredCheckbox interactive
// `container` is either a DOM element, jQuery collection or selector containing
// the Markdown content
// `retriever` is a function being passed the respective checkbox and a
// callback - the latter is expected to be called with the container's raw
// Markdown source
// `storer` is a function being passed the updated Markdown content, the
// respective checkbox and a callback
// both functions' are invoked with the respective `FlavoredCheckbox` instance as
// execution context (i.e. `this`)
// use like that::
//       var retriever = function(checkbox, callback) {
//        var url = '/checkbox_update_url';
//        $.get(url, callback);
//       }
//
//       var storer = function(markdown_txt, checkbox, callback) {
//        var url = '/checkbox_update_url';
//        $.ajax({
//            type: "put",
//            url: url,
//            data: markdown_txt,
//            success: callback
//        });
//       }
//       new FlavoredCheckbox("article", retriever, storer);

function FlavoredCheckbox(container, retriever, storer) {
        this.container = container.jquery ? container : $(container);
        this.retriever = retriever;
        this.storer = storer;
        this._used_class = '.flavored_checkbox_list'

        var checkbox_objects = $(this._used_class, container);
        checkbox_objects.find(this.checkboxSelector).prop("disabled", false);
        var self = this;
        checkbox_objects.on("change", this.checkboxSelector, function() {
                var args = Array.prototype.slice.call(arguments);
                args.push(self);
                self.onChange.apply(this, args);
        });
}
FlavoredCheckbox.prototype.checkboxSelector = "> li > input:checkbox";
FlavoredCheckbox.prototype.onChange = function(ev, self) {
        var checkbox = $(this).prop("disabled", true);
        var index = $("ul" + self.checkboxSelector, self.container).index(this);
        var reactivate = function() { checkbox.prop("disabled", false); };
        self.retriever(checkbox, function(markdown) {
            markdown = self.toggleCheckbox(index, markdown);
            self.storer(markdown, checkbox, reactivate);
        });
};
FlavoredCheckbox.prototype.toggleCheckbox = function(index, markdown) {
        var pattern = /^([*-]) \[([ x])\]/mg; // XXX: duplicates server-side logic!?
        var count = 0;
        return markdown.replace(pattern, function(match, prefix, marker) {
            if(count === index) {
                    marker = marker === " " ? "x" : " ";
            }
            count++;
            return prefix + " [" + marker + "]";
        });
};

return FlavoredCheckbox;

}(jQuery));
