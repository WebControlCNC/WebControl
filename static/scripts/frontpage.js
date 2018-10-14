//checkForGCodeUpdate();

//setInterval(function(){ alert("Hello"); }, 3000);

var scale = 1;

var draw = SVG('workarea').size('100%','100%').panZoom({zoomMin: 10, zoomMax: 100, zoomFactor:2.5});
var viewbox = draw.viewbox();
var originX = viewbox.width/2;
var originY = viewbox.height/2;
var currentPosX = 0;
var currentPosY = 0;
var gcode = null;
//var rect = draw.rect(100,100).attr({fill: '#f06'})
//var sheet = draw.rect(768,384).fill(draw.image('/static/images/materials/Plywood_texture.JPG',768,384)).scale(96/768*scale,48/384*scale).center(originX,originY)

var gridLines = draw.group()
gridLines.add(draw.line(0*scale,0*scale,96*scale,0*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0*scale,48*scale,96*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0*scale,24*scale,96*scale,24*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0*scale,0*scale,0*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(24*scale,0*scale,24*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(48*scale,0*scale,48*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(72*scale,0*scale,72*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(96*scale,0*scale,96*scale,48*scale).stroke({width:.1, color: '#000'}))
gridLines.center(originX,originY)
//gridLines.scale(scale,scale)

var sled = draw.group()
sled.add(draw.line(1.5*scale,-0.0*scale,1.5*scale,3.0*scale).stroke({width:.1,color:"#F00"}))
sled.add(draw.line(-0.0*scale,1.5*scale,3.0*scale,1.5*scale).stroke({width:.1,color:"#F00"}))
sled.add(draw.circle(3*scale).stroke({width:.1,color:"#F00"}).fill({color:"#fff",opacity:0}))
sled.center(originX,originY)
//sled.center(vx,vy)
draw.zoom(10, {x:originX,y:originY});

function positionUpdate(x,y,z){
  var _x, _y =0
  //console.log(x)
  if ($("#units").text()=="MM"){
    _x = originX+x*scale/25.4
    _y = originY-y*scale/25.4
  }
  else{
    _x = originX+x*scale;
    _y = originY-y*scale
  }

  sled.center(_x, _y);
}

function unitSwitch(){
  if ( $("#units").text()=="MM") {
    $("#units").text("INCHES");
    distToMove = Math.round($("#distToMove").val()/25.4,3)
    $("#distToMove").val(distToMove);
    updateSetting('toInches',distToMove);
  } else {
    $("#units").text("MM");
    distToMove = Math.round($("#distToMove").val()*25.4,3)
    $("#distToMove").val(distToMove);
    updateSetting('toMM',distToMove);
  }
}

$(document).ready(function(){
    settingRequest("units");
    settingRequest("distToMove");
    checkForGCodeUpdate();
});

function pauseRun(){
  if ($("#pauseButton").text()=="Pause"){
    $("#pauseButton").text("Resume");
    action('pauseRun');
  }
  else {
    $("#pauseButton").text("Pause");
    action('resumeRun');
  }

}

function processRequestedSetting(msg){
  console.log(msg);
  if (msg.setting=="units"){
    console.log("requestedSetting:"+msg.value);
    $("#units").text(msg.value)
  }
  if (msg.setting=="distToMove"){
    console.log("requestedSetting for distToMove:"+msg.value);
    $("#distToMove").val(msg.value)
  }
  if (msg.setting=="unitsZ"){
    console.log("requestedSetting:"+msg.value);
    $("#unitsZ").text(msg.value)
  }
  if (msg.setting=="distToMoveZ"){
    console.log("requestedSetting for distToMoveZ:"+msg.value);
    $("#distToMoveZ").val(msg.value)
  }
}

function processPositionMessage(msg){
  var json = JSON.parse(msg.data);
  $('#positionMessage').html('<p>XPos:'+json.xval+' Ypos:'+json.yval+' ZPos:'+json.zval+'</p>');
  positionUpdate(json.xval,json.yval,json.zval);
}

function gcodeUpdate(msg){
  console.log("updating gcode");
  if (gcode!=null) {
    console.log("removing gcode");
    //gcode.remove();
    gcode.remove();
  }
  gcode = draw.group();
  var data = JSON.parse(msg.data)
  data.forEach(function(line) {
    console.log(line)
    if (line.type=='line'){
      if (line.dashed==true) {
        gcode.add(draw.polyline(line.points).fill('none').stroke({width:.1, color: '#AA0'}))
      } else {
        gcode.add(draw.polyline(line.points).fill('none').stroke({width:.1, color: '#00F'}))
      }
    }
    gcode.move(originX,originY)
  });
}

//sled.scale(scale,scale)
/*var sketch = function(p)
{
  p.setup= function(){
    p.createCanvas(640,480);
  }
  p.draw = function(){
    p.ellipse(50,50,80,80)
  }
};
new p5(sketch, 'workarea')
*/



/*
// Simple way to attach js code to the canvas is by using a function
function sketchProc(processing) {
  // Override draw function, by default it will be called 60 times per second
  processing.draw = function() {
    // determine center and max clock arm length
    var centerX = processing.width / 2, centerY = processing.height / 2;
    var maxArmLength = Math.min(centerX, centerY);

    function drawArm(position, lengthScale, weight) {
      processing.strokeWeight(weight);
      processing.line(centerX, centerY,
        centerX + Math.sin(position * 2 * Math.PI) * lengthScale * maxArmLength,
        centerY - Math.cos(position * 2 * Math.PI) * lengthScale * maxArmLength);
    }

    // erase background
    processing.background(224);

    var now = new Date();

    // Moving hours arm by small increments
    var hoursPosition = (now.getHours() % 12 + now.getMinutes() / 60) / 12;
    drawArm(hoursPosition, 0.5, 5);

    // Moving minutes arm by small increments
    var minutesPosition = (now.getMinutes() + now.getSeconds() / 60) / 60;
    drawArm(minutesPosition, 0.80, 3);

    // Moving hour arm by second increments
    var secondsPosition = now.getSeconds() / 60;
    drawArm(secondsPosition, 0.90, 1);
  };

}

var canvas = document.getElementById("workarea");
// attaching the sketchProc function to the canvas
var p = new Processing(canvas, sketchProc);
// p.exit(); to detach it
*/
/*var elem = document.getElementById('workarea');
var params = {width: 1000, height: 600};
var two = new Two(params).appendTo(elem);

var rectangle = two.makeRectangle(500,300,1000,600);
var texture = new Two.Texture("/static/images/materials/Plywood_texture.JPG", function() {
});
rectangle.fill = texture
two.update();
*/
