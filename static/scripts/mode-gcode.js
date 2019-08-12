define(function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
// defines the parent mode
var TextMode = require("./text").Mode;
var Tokenizer = require("../tokenizer").Tokenizer;
var MatchingBraceOutdent = require("./matching_brace_outdent").MatchingBraceOutdent;

// defines the language specific highlighters and folding rules
var MyNewHighlightRules = require("./gcode_highlight_rules").MyNewHighlightRules;
var MyNewFoldMode = require("./folding/gcode").MyNewFoldMode;

var Mode = function() {
    // set everything up
    this.HighlightRules = MyNewHighlightRules;
    this.$outdent = new MatchingBraceOutdent();
    this.foldingRules = new MyNewFoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    // configure comment start/end characters
    this.lineCommentStart = "//";
    this.blockComment = {start: "/*", end: "*/"};

    // special logic for indent/outdent.
    // By default ace keeps indentation of previous line
    this.getNextLineIndent = function(state, line, tab) {
        var indent = this.$getIndent(line);
        return indent;
    };

    this.checkOutdent = function(state, line, input) {
        return this.$outdent.checkOutdent(line, input);
    };

    this.autoOutdent = function(state, doc, row) {
        this.$outdent.autoOutdent(doc, row);
    };

    // create worker for live syntax checking
    this.createWorker = function(session) {
        var worker = new WorkerClient(["ace"], "ace/mode/gcode_worker", "NewWorker");
        worker.attachToDocument(session.getDocument());
        worker.on("errors", function(e) {
            session.setAnnotations(e.data);
        });
        return worker;
    };

}).call(Mode.prototype);

exports.Mode = Mode;
});