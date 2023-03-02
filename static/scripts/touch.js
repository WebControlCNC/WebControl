import "jquery";

import { requestPage } from "./socketEmits.js";

var timer;
var touchduration = 1500; //length of time we want the user to touch before we do something
var lastTouchEvent = null;

function onlongtouch(e) { 
    console.log("long touch detected", e.touches[0].clientX, e.touches[0].clientY);
    // TODO: the global `event` is deprecated, this needs replacing
    event = {
    	clientX: e.touches[0].clientX,
	    clientY: e.touches[0].clientY
    }
    var pos = cursorPosition();
    x = pos.x;
    x = x.toFixed(4);
    pos.x = x;

    y = pos.y;
    y = y.toFixed(4);
    pos.y = y;
    requestPage("screenAction", pos);
};

function touchstart(e) {
    e.preventDefault();
    lastTouchEvent = e;
    if (!timer) {
        timer = setTimeout(function() {
		    onlongtouch(lastTouchEvent);
		    timer = null;
		    lastTouchEvent = null;
	    }, touchduration);
    }
}

function touchend(e) {
    //stops short touches from firing the event
    if (timer) {
        clearTimeout(timer);
        timer = null;
        lastTouchEvent = null;
    }
}

document.addEventListener("DOMContentLoaded", function(event) { 
    $("#workarea")[0].addEventListener("touchstart", touchstart, false);
    $("#workarea")[0].addEventListener("touchend", touchend, false);
});
