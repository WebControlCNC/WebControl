//checkForGCodeUpdate();

//setInterval(function(){ alert("Hello"); }, 3000);

var scale = 1;

var draw = SVG('workarea').size('100%','100%').panZoom({zoomMin: 1, zoomMax: 500, zoomFactor:2.5});
var viewbox = draw.viewbox();
var originX = viewbox.width/2;
var originY = viewbox.height/2;
var currentPosX = 0;
var currentPosY = 0;
var gcode = null;
//var rect = draw.rect(100,100).attr({fill: '#f06'})
//var sheet = draw.image('/static/images/materials/Plywood_texture.JPG',96,48).center(originX,originY)

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

var home = draw.group()
home.add(draw.line(1.5*scale,-0.0*scale,1.5*scale,3.0*scale).stroke({width:.1,color:"#0F0"}))
home.add(draw.line(-0.0*scale,1.5*scale,3.0*scale,1.5*scale).stroke({width:.1,color:"#0F0"}))
home.add(draw.circle(3*scale).stroke({width:.1,color:"#0F0"}).fill({color:"#fff",opacity:0}))
home.center(originX,originY)
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

function homePositionUpdate(x,y){
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
  //console.log("home:"+_x+", "+_y)
  home.center(_x, _y);
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
    settingRequest("homePosition");
    checkForGCodeUpdate();
});

function pauseRun(){
  if ($("#pauseButton").text()=="Pause"){
    action('pauseRun');
  }
  else {
    action('resumeRun');
  }
}

function processRequestedSetting(msg){
  console.log(msg);
  if (msg.setting=="pauseButtonSetting"){
    if(msg.value=="Resume")
        $('#pauseButton').removeClass('btn-warning').addClass('btn-info');
    else
        $('#pauseButton').removeClass('btn-info').addClass('btn-warning');
    $("#pauseButton").text(msg.value);
  }
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
  $('#positionMessage').html('<p>XPos:'+Math.round(json.xval,2)+' Ypos:'+Math.round(json.yval,2)+' ZPos:'+Math.round(json.zval,2)+'</p>');
  positionUpdate(json.xval,json.yval,json.zval);
}

function processHomePositionMessage(msg){
  var json = JSON.parse(msg.data);
  $('#homePositionMessage').html('<p>XPos:'+Math.round(json.xval,2)+' Ypos:'+Math.round(json.yval,2)+'</p>');
  homePositionUpdate(json.xval,json.yval);
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
