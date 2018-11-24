//checkForGCodeUpdate();

//setInterval(function(){ alert("Hello"); }, 3000);



var renderer = new THREE.WebGLRenderer();
var w = $("#workarea").width()-10;
var h = $("#workarea").height()-10;
renderer.setSize( w, h );
console.log(w)

container = document.getElementById('workarea');
container.appendChild(renderer.domElement);


var gcode = new THREE.Group();

var camera = new THREE.PerspectiveCamera(45, w/h, 1, 500);
var controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.screenSpacePanning = true;

camera.position.set(0, 0, 100);
camera.lookAt(0,0,0);
var view3D = true;
toggle3DView(); // makes it not true and applies appropriate settings
//controls.update();
controls.saveState();

var scene = new THREE.Scene();
scene.background= new THREE.Color(0xdddddd);
var light = new THREE.AmbientLight( 0x404040 ); // soft white light
scene.add( light );
var material = new THREE.LineBasicMaterial( {color:0x0000ff });
var greenLineMaterial = new THREE.LineBasicMaterial( {color:0x00ff00 });
var redLineMaterial = new THREE.LineBasicMaterial( {color:0xff0000 });
var greenLineDashedMaterial = new THREE.LineDashedMaterial( {color:0x00ff00, dashSize:.1, gapSize: .1} );
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


var sledHorizontalLineSegments = new THREE.Geometry();
sledHorizontalLineSegments.vertices.push(new THREE.Vector3(-1.5, 0, 0));
sledHorizontalLineSegments.vertices.push(new THREE.Vector3(1.5, 0, 0));
var sledHorizontalLine = new THREE.LineSegments(sledHorizontalLineSegments, redLineMaterial);

var sledVerticalLineSegments = new THREE.Geometry();
sledVerticalLineSegments.vertices.push(new THREE.Vector3(0, -1.5, 0));
sledVerticalLineSegments.vertices.push(new THREE.Vector3(0, 1.5, 0));
var sledVerticalLine = new THREE.LineSegments(sledVerticalLineSegments, redLineMaterial);

var sledCircleGeometry = new THREE.CircleGeometry(1,32);
var sledCircleEdges = new THREE.EdgesGeometry(sledCircleGeometry)
var sledCircle = new THREE.LineSegments(sledCircleEdges,redLineMaterial);

var sled = new THREE.Group();
sled.add(sledHorizontalLine);
sled.add(sledVerticalLine);
sled.add(sledCircle);
sled.position.set(0,0,0);


var homeHorizontalLineSegments = new THREE.Geometry();
homeHorizontalLineSegments.vertices.push(new THREE.Vector3(-1.0, 0, 0));
homeHorizontalLineSegments.vertices.push(new THREE.Vector3(1.0, 0, 0));
var homeHorizontalLine = new THREE.LineSegments(homeHorizontalLineSegments, greenLineMaterial);

var homeVerticalLineSegments = new THREE.Geometry();
homeVerticalLineSegments.vertices.push(new THREE.Vector3(0, -1.0, 0));
homeVerticalLineSegments.vertices.push(new THREE.Vector3(0, 1.0, 0));
var homeVerticalLine = new THREE.LineSegments(homeVerticalLineSegments, greenLineMaterial);

var homeCircleGeometry = new THREE.CircleGeometry(.5,32);
var homeCircleEdges = new THREE.EdgesGeometry(homeCircleGeometry)
var homeCircle = new THREE.LineSegments(homeCircleEdges,greenLineMaterial);

var home = new THREE.Group();
home.add(homeHorizontalLine);
home.add(homeVerticalLine);
home.add(homeCircle);
home.position.set(0,0,0);


scene.add(sled);
scene.add(home);

animate();

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render( scene, camera );
}

function positionUpdate(x,y,z){
    if ($("#units").text()=="MM"){
        x /= 25.4
        y /= 25.4
    }
    sled.position.set(x,y,z);
}


function homePositionUpdate(x,y){
    if ($("#units").text()=="MM"){
        x /= 25.4
        y /= 25.4
    }
    home.position.set(x,y,0);
}

function unitSwitch(){
  if ( $("#units").text()=="MM") {
    //$("#units").text("INCHES");
    distToMove = Math.round($("#distToMove").val()/25.4,3)
    //$("#distToMove").val(distToMove);
    updateSetting('toInches',distToMove);
  } else {
    //$("#units").text("MM");
    distToMove = Math.round($("#distToMove").val()*25.4,3)
    //$("#distToMove").val(distToMove);
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

    /*$( "#workarea" ).contextmenu(function() {
        pos = cursorPosition();
        requestPage("screenAction",pos)
        //alert( "Handler for "+pos+" called." );
    });*/
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
  positionUpdate(_json.xval,_json.yval,_json.zval);
}

function processHomePositionMessage(msg){
  var _json = JSON.parse(msg.data);
  console.log(_json.xval)
  $('#homePositionMessage').html('XPos:'+parseFloat(_json.xval).toFixed(2)+' Ypos:'+parseFloat(_json.yval).toFixed(2));
  homePositionUpdate(_json.xval,_json.yval);
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
  console.log(gcode.length);
  if (gcode.children.length!=0) {
    for (var i = gcode.children.length -1; i>=0; i--){
        gcode.remove(gcode.children[i]);
    }
  }

  var gcodeLineSegments = new THREE.Geometry();
  var gcodeDashedLineSegments = new THREE.Geometry();

  if (msg.data!=null){
    var uncompressed = pako.inflate(msg.data);
    var _str = ab2str(uncompressed);
    var data = JSON.parse(_str)
    var pX, pY, pZ = -99999.9
    data.forEach(function(line) {
      if (line.type=='line'){
        console.log("Line length="+line.points.length+", dashed="+line.dashed);
        if (line.dashed==true) {
          line.points.forEach(function(point) {
            gcodeDashedLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
          })
        } else {
          line.points.forEach(function(point) {
            gcodeLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
          })
        }
      }
    });
    //gcode.move(originX,originY)
    var gcodeDashed = new THREE.Line(gcodeDashedLineSegments, greenLineDashedMaterial)
    gcodeDashed.computeLineDistances();
    var gcodeUndashed = new THREE.Line(gcodeLineSegments, material)
    gcode.add(gcodeDashed);
    gcode.add(gcodeUndashed);
    scene.add(gcode);
  }
  $("#fpCircle").hide();

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

function toggle3DView()
{
    console.log("toggling");
    if (view3D){
        controls.enableRotate = false;
        controls.mouseButtons = {
            LEFT: THREE.MOUSE.RIGHT,
            MIDDLE: THREE.MOUSE.MIDDLE,
            RIGHT: THREE.MOUSE.LEFT
        }
        view3D=false;
        console.log("toggled off");
    } else {
        controls.enableRotate = true;
        controls.mouseButtons = {
            LEFT: THREE.MOUSE.RIGHT,
            MIDDLE: THREE.MOUSE.MIDDLE,
            RIGHT: THREE.MOUSE.LEFT
        }
        view3D=true;
        console.log("toggled on");
    }
    controls.update();
}

function resetView(){
    controls.reset();
}

function cursorPosition(){
    var rect = renderer.domElement.getBoundingClientRect();
    var vec = new THREE.Vector3(); // create once and reuse
    var pos = new THREE.Vector3(); // create once and reuse
    vec.set(
        ( ( event.clientX - rect.left ) / ( rect.width - rect.left ) ) * 2 - 1,
        - ( ( event.clientY - rect.top ) / ( rect.bottom - rect.top) ) * 2 + 1,
        0.5 );


    vec.unproject( camera );

    vec.sub( camera.position ).normalize();

    var distance = - camera.position.z / vec.z;

    pos.copy( camera.position ).add( vec.multiplyScalar( distance ) );
    console.log(pos);
    return(pos);
}