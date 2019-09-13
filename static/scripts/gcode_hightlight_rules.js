define(function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var MyNewHighlightRules = function() {

    // regexp must not have capturing parentheses. Use (?:) instead.
    // regexps are ordered -> the first match is used
   this.$rules = {
        "start" : [
            {
                token: token, // String, Array, or Function: the CSS token to apply
                regex: regex, // String or RegExp: the regexp to match
                next:  next   // [Optional] String: next state to enter
            }
        ]
    };
};

oop.inherits(MyNewHighlightRules, TextHighlightRules);

exports.MyNewHighlightRules = MyNewHighlightRules;

});