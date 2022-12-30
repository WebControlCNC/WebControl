import * as THREE from "../node_modules/three/build/three.module.js";
import { action, settingRequest } from "./socketEmits.js";
import { OrbitControls } from "./OrbitControls.js";

settingRequest('Optical Calibration Settings','calibrationCurve');
settingRequest('Optical Calibration Settings','calibrationError');

var _xError = [];
var _yError = [];
var _xValues = [];
var xCurve = [];
var yCurve = [];
var colorwayLayout = ['#313131','#3D019D','#3810DC','#2D47F9','#2503FF','#2ADEF6','#60FDFA','#AEFDFF','#BBBBBB','#FFFDA9','#FAFD5B','#F7DA29','#FF8E25','#F8432D','#D90D39','#D7023D','#313131']

var orenderer;
var ow;
var oh;
var ocontainer;
var oimageShowing;

var ocamera
var ocontrols

var oview3D;
var oscene;
var olight;
var osledHorizontalLineSegments;
var osledHorizontalLine;
var osledVerticalLineSegments;
var osledVerticalLine;

var osledCircleGeometry;
var osledCircleEdges
var osledCircle;

var osled;

function oanimate() {
    requestAnimationFrame(oanimate);
    ocontrols.update();
    orenderer.render( oscene, ocamera );
}

function positionUpdateOptical(x,y,z){
    if ($("#units").text()=="MM"){
        x /= 25.4
        y /= 25.4
        z /= 25.4
    }
    if (osled !== undefined)
    {
        osled.position.set(x,y,z);
    }

}

function processPositionMessageOptical(data){
  positionUpdateOptical(data.xval,data.yval,data.zval);
}

function process(processName){
  var markerX = $("#markerX").val();
  var markerY = $("#markerY").val();
  var opticalCenterX = $("#opticalCenterX").val();
  var opticalCenterY = $("#opticalCenterY").val();
  var scaleX = $("#scaleX").val();
  var scaleY = $("#scaleY").val();
  var tlX = $("#tlX").val();
  var tlY = $("#tlY").val();
  var brX = $("#brX").val();
  var brY = $("#brY").val();
  var calibrationExtents = $("#calibrationExtents option:selected").val()
  var cannyLowValue = $("#cannyLowValue").val();
  var cannyHighValue = $("#cannyHighValue").val();
  var gaussianBlurValue = $("#gaussianBlurValue option:selected").val()
  var autoScanDirection = $("#autoScanDirection option:selected").val()
  var positionTolerance = $("#positionTolerance").val();
  var parameters = {markerX:markerX,
                    markerY:markerY,
                    opticalCenterX:opticalCenterX,
                    opticalCenterY:opticalCenterY,
                    scaleX:scaleX,
                    scaleY:scaleY,
                    tlX:tlX,
                    tlY:tlY,
                    brX:brX,
                    brY:brY,
                    calibrationExtents:calibrationExtents,
                    cannyLowValue:cannyLowValue,
                    cannyHighValue:cannyHighValue,
                    gaussianBlurValue:gaussianBlurValue,
                    autoScanDirection:autoScanDirection,
                    positionTolerance:positionTolerance
                    };
  if (processName=="testImage")
    action('testOpticalCalibration', parameters)
  else if (processName=="findCenter")
    action('findCenterOpticalCalibration', parameters)
  else
    action('optical_Calibrate',parameters);
}


function processCalibrationMessage(data){
    console.log("!!!!!!")
    console.log("Uncaught processCalibrationMessage");
    console.log("!!!!!!")
}

function updateOpticalCalibrationFindCenter(data){
    //data = JSON.parse(data.data)
    console.log(data)
    $("#opticalCenterX").val(data.opticalCenterX.toFixed(2))
    $("#opticalCenterY").val(data.opticalCenterY.toFixed(2))
}

function updateCalibrationImage(data){
    //console.log(data)
    //data = JSON.parse(data)
    if (data.command=="OpticalCalibrationImageUpdated")
        $("#imageDiv").html("<img width='100%' src='data:image/png;base64,"+data.data+"'></html>");
    if (data.command=="OpticalCalibrationTestImageUpdated")
        $("#testImageDiv").html("<img width='100%' src='data:image/png;base64,"+data.data+"'></html>");
}

function updateOpticalCalibrationCurve(data) {
    console.log(data)
    xCurve = data.curveX;
    yCurve = data.curveY;
    $('#curveChartButton').removeClass('btn-secondary').addClass('btn-primary');
    $('#curveFitButton').removeClass('btn-primary').addClass('btn-secondary');
}

function updateOpticalCalibrationError(data) {
    //data = JSON.parse(data);
    console.log(data);
    var x = data.errorX;
    var y = data.errorY;
    xErrorPlot = document.getElementById('xErrorPlot');
    yErrorPlot = document.getElementById('yErrorPlot');
    for(var i = 0; i<15; i++){
        _xError[i]=[];
        _yError[i]=[];
        for(var j =0; j<31; j++){
            _xError[i][j]=x[j][i];
            _yError[i][j]=y[j][i];
            _xValues[j]=j;
        }
    }
    $('#errorChartButton').removeClass('btn-secondary').addClass('btn-primary');
    $('#curveFitButton').removeClass('btn-secondary').addClass('btn-primary');
}

function redrawCurveCharts(chart){
      xCurvePlot = document.getElementById('xCurvePlot');
      yCurvePlot = document.getElementById('yCurvePlot');
      if ($("#xCurvePlot").html()!="")
          while (xCurvePlot.data.length>0)
              Plotly.deleteTraces(xCurvePlot, [0]);
      if ($("#yCurvePlot").html()!="")
          while (yCurvePlot.data.length>0)
              Plotly.deleteTraces(yCurvePlot, [0]);
      var _x = [];
      var _y = [];
      console.log(xCurve)
      for(var i = 0; i<15; i++){
        _y[i]=[]
        for(var j =0; j<31; j++){
          var temp=calSurface(xCurve, j-15, i-7);
          _y[i][j]=temp
          _x[j]=j
        }
        if (window.isMobile)
          Plotly.plot(xCurvePlot, [{x: _x, y: _y[i] }], {title: "X-Curve", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4}, colorway: colorwayLayout } );
        else
          Plotly.plot(xCurvePlot, [{x: _x, y: _y[i] }], {title: "X-Curve" , colorway: colorwayLayout } );

      }

      console.log(yCurve)
      for(var i = 0; i<15; i++){
        _y[i]=[]
        for(var j =0; j<31; j++){
          var temp=calSurface(yCurve, j-15, i-7);
          _y[i][j]=temp
          _x[j]=j
        }
        if (window.isMobile)
          Plotly.plot(yCurvePlot, [{x: _x, y: _y[i] }], {title: "Y-Curve", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4}, colorway: colorwayLayout } );
        else
          Plotly.plot(yCurvePlot, [{x: _x, y: _y[i] }], {title: "Y-Curve" , colorway: colorwayLayout} );
      }

      $('#curveChartButton').removeClass('btn-primary').addClass('btn-secondary');
}

function redrawErrorCharts(chart){
    if ( (chart == "xError") || (chart=="all") ){
      xErrorPlot = document.getElementById('xErrorPlot');
      if ($("#xErrorPlot").html()!="")
         while (xErrorPlot.data.length>0)
              Plotly.deleteTraces(xErrorPlot, [0]);
      for(var i = 0; i<15; i++){
        if (window.isMobile)
          Plotly.plot(xErrorPlot, [{x: _xValues, y: _xError[i] }], {title: "X-Error", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4}, colorway: colorwayLayout } );
        else
          Plotly.plot(xErrorPlot, [{x: _xValues, y: _xError[i] }], {title: "X-Error", colorway: colorwayLayout } );
      }
    }
    if ( (chart == "yError") || (chart=="all") ){
      yErrorPlot = document.getElementById('yErrorPlot');
      if ($("#yErrorPlot").html()!="")
          while (yErrorPlot.data.length>0)
              Plotly.deleteTraces(yErrorPlot, [0]);
      for(var i = 0; i<15; i++){
        if (window.isMobile)
          Plotly.plot(yErrorPlot, [{x: _xValues, y: _yError[i] }], {title: "Y-Error", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4}, colorway: colorwayLayout } );
        else
          Plotly.plot(yErrorPlot, [{x: _xValues, y: _yError[i] }], {title: "Y-Error", colorway: colorwayLayout } );
      }
    }
    if ( (chart == "xyError") || (chart=="all") ){
      xyErrorPlot = document.getElementById('xyErrorPlot');
      if ($("#xyErrorPlot").html()!="")
          while (xyErrorPlot.data.length>0)
              Plotly.deleteTraces(xyErrorPlot, [0]);
      x0 = []
      y0 = []
      for(var i=0; i<15; i++){
         for(var j=0; j<31; j++){
            x0[i*31+j]=3*j*25.4;
            y0[i*31+j]=3*i*25.4;
         }
      }
      x1 = []
      y1 = []
      //Plotly.plot(xyErrorPlot, [{x: x0, y: y0, mode:'markers', type:'scatter'}], {title: "XY-Error" } );
      if (window.isMobile)
        Plotly.plot(xyErrorPlot, [{x: x0, y: y0, mode:'markers', type:'scatter'}], {title: "XY-Error", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4} } );
      else
        Plotly.plot(xyErrorPlot, [{x: x0, y: y0, mode:'markers', type:'scatter'}], {title: "XY-Error"} );

      for(var i=0; i<15; i++){
         for(var j=0; j<31; j++){
            x1[i*31+j]=3*j*25.4+_xError[i][j]
            y1[i*31+j]=3*i*25.4+_yError[i][j]
         }
      }
      //Plotly.plot(xyErrorPlot, [{x: x1, y: y1, mode:'markers', type:'scatter'}] );
      if (window.isMobile)
        Plotly.plot(xyErrorPlot, [{x: x1, y: y1, mode:'markers', type:'scatter'}], {title: "XY-Error", showlegend: false, margin: {l: 20,r: 20, b: 40, t: 40, pad: 4} } );
      else
        Plotly.plot(xyErrorPlot, [{x: x1, y: y1, mode:'markers', type:'scatter'}], {title: "XY-Error"} );
    }
    $('#errorChartButton').removeClass('btn-primary').addClass('btn-secondary');
}

function calSurface(x, i, j){
   i = i*3*25.4
   j = j*3*25.4
   retVal = x[4]*i**2.0 + x[5]*j**2.0 + x[3]*i*j + x[1]*i + x[2]*j + x[0]
   return retVal
}

$(document).ready(function () {
    $('#calibrationExtents').change(function(){
      selected = $("#calibrationExtents option:selected").val()
      console.log(selected);
      switch(selected) {
        case "Top Left":
          $("#tlX").val(-15);
          $("#tlY").val(7);
          $("#brX").val(0);
          $("#brY").val(0);
          enableCustomExtents(true);
          break;
        case "Bottom Left":
          $("#tlX").val(-15);
          $("#tlY").val(0);
          $("#brX").val(0);
          $("#brY").val(-7);
          enableCustomExtents(true);
          break;
        case "Top Right":
          $("#tlX").val(0);
          $("#tlY").val(7);
          $("#brX").val(15);
          $("#brY").val(0);
          enableCustomExtents(true);
          break;
        case "Bottom Right":
          $("#tlX").val(0);
          $("#tlY").val(0);
          $("#brX").val(15);
          $("#brY").val(-7);
          enableCustomExtents(true);
          break;
        case "Full Area":
          $("#tlX").val(-15);
          $("#tlY").val(7);
          $("#brX").val(15);
          $("#brY").val(-7);
          enableCustomExtents(true);
          break;
        case "Custom":
          enableCustomExtents(false);
          break;

        default:
          $("#tlX").val(-15);
          $("#tlY").val(7);
          $("#brX").val(0);
          $("#brY").val(0);
          break;
      }
    });
    console.log("here1");
    setupDisplay();
});

function setupDisplay(){
    orenderer = new THREE.WebGLRenderer();
    ow = $("#workareaOptical").width();
    oh = $("#workareaOptical").height();
    orenderer.setSize( ow, oh );
    console.log(ow);
    console.log(oh);

    ocontainer = document.getElementById('workareaOptical');
    ocontainer.appendChild(orenderer.domElement);
    oimageShowing = 1

    ocamera = new THREE.PerspectiveCamera(45, ow/oh, 1, 500);
    ocontrols = new OrbitControls(ocamera, orenderer.domElement);
    ocontrols.screenSpacePanning = true;

    ocamera.position.set(0, 0, 100);
    ocamera.lookAt(0,0,0);
    oview3D = false;
    ocontrols.enableRotate = false;
    ocontrols.mouseButtons = {
        LEFT: THREE.MOUSE.RIGHT,
        MIDDLE: THREE.MOUSE.MIDDLE,
        RIGHT: THREE.MOUSE.LEFT
    }
    ocontrols.saveState();

    oscene = new THREE.Scene();
    oscene.background= new THREE.Color(0xdddddd);
    olight = new THREE.AmbientLight( 0x404040 ); // soft white light
    oscene.add( light );

    var oouterFrameShape = new THREE.Geometry();
    oouterFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
    oouterFrameShape.vertices.push(new THREE.Vector3(48, 24, 0));
    oouterFrameShape.vertices.push(new THREE.Vector3(48, -24, 0));
    oouterFrameShape.vertices.push(new THREE.Vector3(-48, -24, 0));
    oouterFrameShape.vertices.push(new THREE.Vector3(-48, 24, 0));
    var oouterFrame = new THREE.Line(oouterFrameShape, blackLineMaterial);

    var oframeLineSegments = new THREE.Geometry();
    oframeLineSegments.vertices.push(new THREE.Vector3(-24, 24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(-24, -24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(0, 24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(0, -24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(24, 24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(24, -24, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(-48, 0, 0));
    oframeLineSegments.vertices.push(new THREE.Vector3(48, 0, 0));
    var oinnerFrame = new THREE.LineSegments(oframeLineSegments, blackDashedMaterial)
    oinnerFrame.computeLineDistances();

    oscene.add(oouterFrame);
    oscene.add(oinnerFrame);


    osledHorizontalLineSegments = new THREE.Geometry();
    osledHorizontalLineSegments.vertices.push(new THREE.Vector3(-1.5, 0, 0));
    osledHorizontalLineSegments.vertices.push(new THREE.Vector3(1.5, 0, 0));
    osledHorizontalLine = new THREE.LineSegments(sledHorizontalLineSegments, redLineMaterial);

    osledVerticalLineSegments = new THREE.Geometry();
    osledVerticalLineSegments.vertices.push(new THREE.Vector3(0, -1.5, 0));
    osledVerticalLineSegments.vertices.push(new THREE.Vector3(0, 1.5, 0));
    osledVerticalLine = new THREE.LineSegments(sledVerticalLineSegments, redLineMaterial);

    osledCircleGeometry = new THREE.CircleGeometry(1,32);
    osledCircleEdges = new THREE.EdgesGeometry(sledCircleGeometry)
    osledCircle = new THREE.LineSegments(sledCircleEdges,redLineMaterial);

    osled = new THREE.Group();
    osled.add(osledHorizontalLine);
    osled.add(osledVerticalLine);
    osled.add(osledCircle);
    osled.position.set(0,0,0);

    oscene.add(osled);
    osled.position.set(0,0,0);

    oanimate();
}

function enableCustomExtents(value){
    $("#tlX").prop("disabled", value);
    $("#tlY").prop("disabled", value);
    $("#brX").prop("disabled", value);
    $("#brY").prop("disabled", value);
}

function saveConfiguration(){
  var markerX = $("#markerX").val();
  var markerY = $("#markerY").val();
  var opticalCenterX = $("#opticalCenterX").val();
  var opticalCenterY = $("#opticalCenterY").val();
  var scaleX = $("#scaleX").val();
  var scaleY = $("#scaleY").val();
  var tlX = $("#tlX").val();
  var tlY = $("#tlY").val();
  var brX = $("#brX").val();
  var brY = $("#brY").val();
  var calibrationExtents = $("#calibrationExtents option:selected").val()
  var cannyLowValue = $("#cannyLowValue").val();
  var cannyHighValue = $("#cannyHighValue").val();
  var gaussianBlurValue = $("#gaussianBlurValue option:selected").val();
  var autoScanDirection = $("#autoScanDirection option:selected").val();
  var positionTolerance = $("#positionTolerance").val();
  var parameters = {markerX:markerX,
                    markerY:markerY,
                    opticalCenterX:opticalCenterX,
                    opticalCenterY:opticalCenterY,
                    scaleX:scaleX,
                    scaleY:scaleY,
                    tlX:tlX,
                    tlY:tlY,
                    brX:brX,
                    brY:brY,
                    calibrationExtents:calibrationExtents,
                    cannyLowValue:cannyLowValue,
                    cannyHighValue:cannyHighValue,
                    gaussianBlurValue:gaussianBlurValue,
                    autoScanDirection:autoScanDirection,
                    positionTolerance:positionTolerance
                    };
  action('saveOpticalCalibrationConfiguration',parameters);
}

/*
var drawOptical;
var viewboxOptical;
var originXOptical;
var originYOptical;
var currentPosXOptical;
var currentPosYOptical;
var gridLinesOptical
var sledOptical = null

function drawCalibration(){
    drawOptical = SVG('workareaOptical').size('100%','100%').panZoom({zoomMin: 1, zoomMax: 500, zoomFactor:2.5});
    viewboxOptical = drawOptical.viewbox();
    originXOptical = viewboxOptical.width/2;
    originYOptical = viewboxOptical.height/2;
    currentPosXOptical = 0;
    currentPosYOptical = 0;

    gridLinesOptical = drawOptical.group()
    gridLinesOptical.add(drawOptical.line(0,0,96,0).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(0,48,96,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(0,24,96,24).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(0,0,0,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(24,0,24,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(48,0,48,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(72,0,72,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.add(drawOptical.line(96,0,96,48).stroke({width:.1, color: '#000'}))
    gridLinesOptical.center(originXOptical,originYOptical)
    //gridLines.scale(scale,scale)

    sledOptical = drawOptical.group()
    sledOptical.add(drawOptical.line(1.5,-0.0,1.5,3.0).stroke({width:.1,color:"#F00"}))
    sledOptical.add(drawOptical.line(-0.0,1.5,3.0,1.5).stroke({width:.1,color:"#F00"}))
    sledOptical.add(drawOptical.circle(3).stroke({width:.1,color:"#F00"}).fill({color:"#fff",opacity:0}))
    sledOptical.center(originXOptical,originYOptical)
    //sled.center(vx,vy)
    drawOptical.zoom(10, {x:originXOptical,y:originYOptical});
}
*/

export {
  processPositionMessageOptical,
  updateCalibrationImage,
  updateOpticalCalibrationCurve,
  updateOpticalCalibrationError,
  updateOpticalCalibrationFindCenter,
};
