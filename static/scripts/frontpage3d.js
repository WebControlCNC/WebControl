//checkForGCodeUpdate();

//setInterval(function(){ alert("Hello"); }, 3000);



var renderer = new THREE.WebGLRenderer();
var w = $("#workarea").width()-10;
var h = $("#workarea").height()-10;
renderer.setSize( w, h );
console.log(w)

container = document.getElementById('workarea');
container.appendChild(renderer.domElement);



var camera = new THREE.PerspectiveCamera(45, w/h, 1, 500);
camera.position.set(0, 0, 100);
camera.lookAt(0,0,0);

var scene = new THREE.Scene();
scene.background= new THREE.Color(0xeeeeee);
var light = new THREE.AmbientLight( 0x404040 ); // soft white light
scene.add( light );
var material = new THREE.LineBasicMaterial( {color:0x0000ff });
var dashedMaterial = new THREE.LineDashedMaterial( {color:0x0000ff, dashSize:.5, gapSize: .5} );
var outerFrameShape = new THREE.Geometry();
outerFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(48, 24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(48, -24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(-48, -24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
var outerFrame = new THREE.Line(outerFrameShape, material);

var frameLineSegments = new THREE.Geometry();
frameLineSegments.vertices.push(new THREE.Vector3(-24, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(-24, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(0, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(0, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(24, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(24, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(-48, 0, 0));
frameLineSegments.vertices.push(new THREE.Vector3(48, 0, 0));
var innerFrame = new THREE.LineSegments(frameLineSegments, dashedMaterial)
innerFrame.computeLineDistances();

scene.add(outerFrame);
scene.add(innerFrame);
renderer.render( scene, camera );

/*var gcode = null;
//var rect = draw.rect(100,100).attr({fill: '#f06'})
//var sheet = draw.image('/static/images/materials/Plywood_texture.JPG',96,48).center(originX,originY)

var gridLines = draw.group()
gridLines.add(draw.line(0*scale,0*scale,96*scale,0*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(0*scale,48*scale,96*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(0*scale,24*scale,96*scale,24*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(0*scale,0*scale,0*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(24*scale,0*scale,24*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(48*scale,0*scale,48*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(72*scale,0*scale,72*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.add(draw.line(96*scale,0*scale,96*scale,48*scale).stroke({width:startWidth, color: '#000'}))
gridLines.center(originX,originY)
//gridLines.scale(scale,scale)

var sled = draw.group()
sled.add(draw.line(1.5*scale,-0.0*scale,1.5*scale,3.0*scale).stroke({width:startWidth,color:"#F00"}))
sled.add(draw.line(-0.0*scale,1.5*scale,3.0*scale,1.5*scale).stroke({width:startWidth,color:"#F00"}))
sled.add(draw.circle(3*scale).stroke({width:startWidth,color:"#F00"}).fill({color:"#fff",opacity:0}))
sled.center(originX,originY)

var home = draw.group()
home.add(draw.line(0.75*scale,-0.0*scale,0.75*scale,1.5*scale).stroke({width:startWidth,color:"#0F0"}))
home.add(draw.line(-0.0*scale,0.75*scale,1.5*scale,0.75*scale).stroke({width:startWidth,color:"#0F0"}))
home.add(draw.circle(1.5*scale).stroke({width:startWidth,color:"#0F0"}).fill({color:"#fff",opacity:0}))
home.center(originX,originY)
/

draw.zoom(10, {x:originX,y:originY});
var startZoom = draw.zoom();

draw.on('pinchZoomEnd', function(ev){
    setTimeout(rescale,0.01)
})

draw.on('zoom', function(box, focus){
  setTimeout(rescale,0.01)
})

function rescale(){
  width = startWidth*startZoom/draw.zoom();
  draw.each(function(_i, _children){
      this.each(function(i,children){
        this.attr({'stroke-width':width});
      })
  })
}

function positionUpdate(x,y,z){
  var _x, _y =0
  if ($("#units").text()=="MM"){
    _x = originX+x*scale/25.4
    _y = originY-y*scale/25.4
    _z = z*scale/25.4/2*360
  }
  else{
    _x = originX+x*scale;
    _y = originY-y*scale
    _z = z*scale/2*360
  }
  sled.front()
  sled.center(_x, _y)
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
  home.center(_x, _y);
}
*/

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
    settingRequest("Computed Settings","units");
    settingRequest("Computed Settings","distToMove");
    settingRequest("Computed Settings","homePosition");
    checkForGCodeUpdate();
    var controllerMessage = document.getElementById('controllerMessage');
    controllerMessage.scrollTop = controllerMessage.scrollHeight;
    //var $controllerMessage = $("#controllerMessage");
    //$controllerMessage.scrollTop($controllerMessage[0].scrollHeight);
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
  if ((msg.setting=="unitsZ") || (msg.setting=="distToMoveZ")){
    if (typeof processZAxisRequestedSetting === "function") {
       processZAxisRequestedSetting(msg)
    }
  }
}

function processPositionMessage(msg){
  var _json = JSON.parse(msg.data);
  $('#positionMessage').html('XPos:'+parseFloat(_json.xval).toFixed(2)+' Ypos:'+parseFloat(_json.yval).toFixed(2)+' ZPos:'+parseFloat(_json.zval).toFixed(2));
  $('#percentComplete').html(_json.pcom)
//  positionUpdate(_json.xval,_json.yval,_json.zval);
}

function processHomePositionMessage(msg){
  var _json = JSON.parse(msg.data);
  console.log(_json.xval)
  $('#homePositionMessage').html('XPos:'+parseFloat(_json.xval).toFixed(2)+' Ypos:'+parseFloat(_json.yval).toFixed(2));
//  homePositionUpdate(_json.xval,_json.yval);
}

function gcodeUpdate(msg){
  console.log("updating gcode");
/*  if (gcode!=null) {
    //console.log("removing gcode");
    gcode.remove();
  }
  width = startWidth*startZoom/draw.zoom();
  gcode = draw.group();
  var data = JSON.parse(msg.data)
  data.forEach(function(line) {
    //console.log(line)
    if (line.type=='line'){
      if (line.dashed==true) {
        gcode.add(draw.polyline(line.points).fill('none').stroke({width:width, color: '#AA0'}))
      } else {
        gcode.add(draw.polyline(line.points).fill('none').stroke({width:width, color: '#00F'}))
      }
    }
    gcode.move(originX,originY)
  });
  */
}

function gcodeUpdateCompressed(msg){
  console.log("updating gcode compressed");
  /*if (gcode!=null) {
    //console.log("removing gcode");
    gcode.remove();
  }
  width = startWidth*startZoom/draw.zoom();
  gcode = draw.group();
  //console.log(msg.data);
  if (msg.data!=null){
    var uncompressed = pako.inflate(msg.data);
    var _str = ab2str(uncompressed);
    //var _str = new TextDecoder("utf-8").decode(uncompressed);
    //console.log(_str);
    var data = JSON.parse(_str)
    data.forEach(function(line) {
      //console.log(line)
      if (line.type=='line'){
        if (line.dashed==true) {
          gcode.add(draw.polyline(line.points).fill('none').stroke({width:width, color: '#AA0'}))
        } else {
          gcode.add(draw.polyline(line.points).fill('none').stroke({width:width, color: '#00F'}))
        }
      }
      gcode.move(originX,originY)
    });
  }
  $("#fpCircle").hide();
  */
}

function ab2str(buf) {
    var bufView = new Uint16Array(buf);
    var unis =""
    for (var i = 0; i < bufView.length; i++) {
        unis=unis+String.fromCharCode(bufView[i]);
    }
    return unis
}

function showFPSpinner(msg){
    $("#fpCircle").show();
}