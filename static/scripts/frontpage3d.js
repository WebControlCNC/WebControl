//checkForGCodeUpdate();

//setInterval(function(){ alert("Hello"); }, 3000);



var renderer = new THREE.WebGLRenderer();
var w = $("#workarea").width()-20;
var h = $("#workarea").height()-20;
renderer.setSize( w, h );
//console.log(w)

container = document.getElementById('workarea');
container.appendChild(renderer.domElement);
var imageShowing = 1

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
var blueLineMaterial = new THREE.LineBasicMaterial( {color:0x0000ff });
var greenLineMaterial = new THREE.LineBasicMaterial( {color:0x00ff00 });
var redLineMaterial = new THREE.LineBasicMaterial( {color:0xff0000 });
var blackLineMaterial = new THREE.LineBasicMaterial( {color:0x000000 });

var greenLineDashedMaterial = new THREE.LineDashedMaterial( {color:0x00ff00, dashSize:.1, gapSize: .1} );
var blackDashedMaterial = new THREE.LineDashedMaterial( {color:0x000000, dashSize:.5, gapSize: .5} );

var outerFrameShape = new THREE.Geometry();
outerFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(48, 24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(48, -24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(-48, -24, 0));
outerFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
var outerFrame = new THREE.Line(outerFrameShape, blackLineMaterial);

var frameLineSegments = new THREE.Geometry();
frameLineSegments.vertices.push(new THREE.Vector3(-24, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(-24, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(0, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(0, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(24, 24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(24, -24, 0));
frameLineSegments.vertices.push(new THREE.Vector3(-48, 0, 0));
frameLineSegments.vertices.push(new THREE.Vector3(48, 0, 0));
var innerFrame = new THREE.LineSegments(frameLineSegments, blackDashedMaterial)
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


var gcodePosHorizontalLineSegments = new THREE.Geometry();
gcodePosHorizontalLineSegments.vertices.push(new THREE.Vector3(-1.0, 0, 0));
gcodePosHorizontalLineSegments.vertices.push(new THREE.Vector3(1.0, 0, 0));
var gcodePosHorizontalLine = new THREE.LineSegments(gcodePosHorizontalLineSegments, blackLineMaterial);

var gcodePosVerticalLineSegments = new THREE.Geometry();
gcodePosVerticalLineSegments.vertices.push(new THREE.Vector3(0, -1.0, 0));
gcodePosVerticalLineSegments.vertices.push(new THREE.Vector3(0, 1.0, 0));
var gcodePosVerticalLine = new THREE.LineSegments(gcodePosVerticalLineSegments, blackLineMaterial);

var gcodePosCircleGeometry = new THREE.CircleGeometry(.5,32);
var gcodePosCircleEdges = new THREE.EdgesGeometry(gcodePosCircleGeometry)
var gcodePosCircle = new THREE.LineSegments(gcodePosCircleEdges,blackLineMaterial);

var gcodePos = new THREE.Group();
gcodePos.add(gcodePosHorizontalLine);
gcodePos.add(gcodePosVerticalLine);
gcodePos.add(gcodePosCircle);
gcodePos.position.set(0,0,0);

scene.add(sled);
scene.add(home);
scene.add(gcodePos);

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
        z /= 25.4
    }
    sled.position.set(x,y,z);
    //console.log("x="+x+", y="+y+", z="+z)
}


function homePositionUpdate(x,y){
    if ($("#units").text()=="MM"){
        x /= 25.4
        y /= 25.4
    }
    home.position.set(x,y,0);
}

function gcodePositionUpdate(x,y){
    if ($("#units").text()=="MM"){
        x /= 25.4
        y /= 25.4
    }
    gcodePos.position.set(x,y,0);
    //console.log("x="+x+", y="+y)
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
    action("statusRequest","cameraStatus");
    checkForGCodeUpdate();
    var controllerMessage = document.getElementById('controllerMessage');
    controllerMessage.scrollTop = controllerMessage.scrollHeight;
    //var $controllerMessage = $("#controllerMessage");
    //$controllerMessage.scrollTop($controllerMessage[0].scrollHeight);

    $( "#workarea" ).contextmenu(function() {
        if (!view3D)
        {
            pos = cursorPosition();
            requestPage("screenAction",pos)
        }
    });
});

function pauseRun(){
  if ($("#pauseButton").text()=="Pause"){
    action('pauseRun');
  }
  else {
    action('resumeRun');
  }
}

function processRequestedSetting(data){
  //console.log(msg);
  if (data.setting=="pauseButtonSetting"){
    if(data.value=="Resume")
        $('#pauseButton').removeClass('btn-warning').addClass('btn-info');
    else
        $('#pauseButton').removeClass('btn-info').addClass('btn-warning');
    $("#pauseButton").text(data.value);
  }
  if (data.setting=="units"){
    console.log("requestedSetting:"+data.value);
    $("#units").text(data.value)
  }
  if (data.setting=="distToMove"){
    console.log("requestedSetting for distToMove:"+data.value);
    $("#distToMove").val(data.value)
  }
  if ((data.setting=="unitsZ") || (data.setting=="distToMoveZ")){
    if (typeof processZAxisRequestedSetting === "function") {
       processZAxisRequestedSetting(data)
    }
  }
}

function processPositionMessage(data){
  $('#positionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2)+' ZPos:'+parseFloat(data.zval).toFixed(2));
  $('#percentComplete').html(data.pcom)
  $('#machineState').html(data.state)
  positionUpdate(data.xval,data.yval,data.zval);
}

function processHomePositionMessage(data){
  $('#homePositionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2));
  homePositionUpdate(data.xval,data.yval);
}

function processGCodePositionMessage(data){
  $('#gcodePositionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2));
  $('#gcodeLine').html(data.gcodeLine);
  $('#gcodeLineIndex').val(data.gcodeLineIndex)
  gcodePositionUpdate(data.xval,data.yval);
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
function gcodeUpdateCompressed(data){
  console.log("updating gcode compressed");
  console.log(gcode.length);
  if (gcode.children.length!=0) {
    for (var i = gcode.children.length -1; i>=0; i--){
        gcode.remove(gcode.children[i]);
    }
  }

  var gcodeLineSegments = new THREE.Geometry();
  var gcodeDashedLineSegments = new THREE.Geometry();

  if (data!=null){
    var uncompressed = pako.inflate(data);
    var _str = ab2str(uncompressed);
    var data = JSON.parse(_str)
    var pX, pY, pZ = -99999.9
    data.forEach(function(line) {
      if (line.type=='line'){
        //console.log("Line length="+line.points.length+", dashed="+line.dashed);
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
    var gcodeUndashed = new THREE.Line(gcodeLineSegments, blueLineMaterial)
    gcode.add(gcodeDashed);
    gcode.add(gcodeUndashed);
    scene.add(gcode);
    console.log(gcodeUndashed);
  }
  $("#fpCircle").hide();

}
/*
function gcodeUpdateCompressed(msg){

  //This routine was an attempt at seeing if individual line segments could be stored such
  //that we could change their color as the cut progresses.  It worked on small gcode but
  //crashed on a large file.  will need to find another way.
  console.log("updating gcode compressed");
  console.log(gcode.length);
  if (gcode.children.length!=0) {
    for (var i = gcode.children.length -1; i>=0; i--){
        gcode.remove(gcode.children[i]);
    }
  }


  var gcodeLineSegments = new THREE.Geometry();
  var gcodeDashedLineSegments = new THREE.Geometry();

  var gcodeDashed = []
  var gcodeUndashed = []

  index1 = 0
  index2 = 0
  if (msg.data!=null){
    var uncompressed = pako.inflate(msg.data);
    var _str = ab2str(uncompressed);
    var data = JSON.parse(_str)
    var pX, pY, pZ = -99999.9
    data.forEach(function(line) {
      if (line.type=='line'){
        //console.log("Line length="+line.points.length+", dashed="+line.dashed);
        if (line.dashed==true) {
          line.points.forEach(function(point) {
            gcodeDashedLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
            if (index1 != 0) {
                gcodeDashedLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
                gcodeDashed[index1]=new THREE.Line(gcodeDashedLineSegments, greenLineDashedMaterial)
                gcodeDashed[index1].computeLineDistances();
                gcodeDashedLineSegments = new THREE.Geometry();
            }
            index1=index1+1
          })
        } else {
          line.points.forEach(function(point) {
            gcodeLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
            if (index2 != 0) {
                gcodeLineSegments.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
                gcodeUndashed[index2]=new THREE.Line(gcodeLineSegments, blueLineMaterial)
                gcodeUndashedLineSegments = new THREE.Geometry();
            }
            index2=index2+1
          })
        }
      }
    });
    //gcode.move(originX,originY)
    gcodeDashed.forEach(function(line){
        gcode.add(line);
    })
    gcodeUndashed.forEach(function(line){
        gcode.add(line);
    })


    scene.add(gcode);
  }
  $("#fpCircle").hide();

}
*/

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
        if (isMobile)
        {
            $("#mobilebutton3D").removeClass('btn-primary').addClass('btn-secondary');
        }
        else
        {
            $("#button3D").removeClass('btn-primary').addClass('btn-secondary');
        }
        console.log("toggled off");
    } else {
        controls.enableRotate = true;
        controls.mouseButtons = {
            LEFT: THREE.MOUSE.RIGHT,
            MIDDLE: THREE.MOUSE.MIDDLE,
            RIGHT: THREE.MOUSE.LEFT
        }
        view3D=true;
        if (isMobile)
        {
            $("#mobilebutton3D").removeClass('btn-secondary').addClass('btn-primary');
        }
        else
        {
            $("#button3D").removeClass('btn-secondary').addClass('btn-primary');
        }
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
    //console.log(pos);
    return(pos);
}

function processCameraMessage(data){
    if(data.command=="cameraImageUpdated"){
        var newImg = new Image();
        if (imageShowing==1)
        {
            newImg.onload = function() {
                document.getElementById("cameraImage2").setAttribute('src',this.src);
                if (isMobile){
                    document.getElementById("mobileCameraDiv2").style.zIndex = "95";
                    document.getElementById("mobileCameraDiv1").style.zIndex = "94";
                } else {
                    document.getElementById("cameraDiv2").style.zIndex = "95";
                    document.getElementById("cameraDiv1").style.zIndex = "94";
                }
                imageShowing = 2
            }
        }
        else
        {
            newImg.onload = function() {
                document.getElementById("cameraImage1").setAttribute('src',this.src);
                if (isMobile){
                    document.getElementById("mobileCameraDiv1").style.zIndex = "95";
                    document.getElementById("mobileCameraDiv2").style.zIndex = "94";
                } else {
                    document.getElementById("cameraDiv1").style.zIndex = "95";
                    document.getElementById("cameraDiv2").style.zIndex = "94";
                }
                imageShowing = 1
            }
        }
        newImg.setAttribute('src', 'data:image/png;base64,'+data.data)

    }
    if(data.command=="updateCamera")
    {
        if (data.data=="on"){
            $("#videoStatus svg.feather.feather-video-off").replaceWith(feather.icons.video.toSvg());
            feather.replace();
            console.log("video on");
            document.getElementById("cameraImage1").style.display = "block"
            document.getElementById("cameraImage2").style.display = "block"
            if (isMobile)
                document.getElementById("mobileCameraArea").style.display = "block"
        }

        if (data.data=="off"){
            $("#videoStatus svg.feather.feather-video").replaceWith(feather.icons["video-off"].toSvg());
            feather.replace();
            console.log("video off")
            document.getElementById("cameraImage1").style.display = "none";
            document.getElementById("cameraImage2").style.display = "none"
            if (isMobile)
                document.getElementById("mobileCameraArea").style.display = "none"
        }
    }
}

function processControllerMessage(data){
    if (controllerMessages.length >100)
        controllerMessages.shift();
    controllerMessages.push(data);
    $('#controllerMessage').html('');
    controllerMessages.forEach(function(message){
        $('#controllerMessage').append(message+"<br>");
    });
    $('#controllerMessage').scrollBottom();
}