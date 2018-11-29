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

function positionUpdateOptical(x,y,z){
  var _x, _y =0
  //console.log(x)
  if ($("#units").text()=="MM"){
    _x = originXOptical+x/25.4
    _y = originYOptical-y/25.4
  }
  else{
    _x = originXOptical+x;
    _y = originYOptical-y;
  }
  //console.log(sledOptical)
  if (sledOptical!=null) {
    //console.log(_y)
    sledOptical.center(_x, _y);  
  }

}

function processPositionMessageOptical(msg){

  var json = JSON.parse(msg.data);
  //$('#positionMessageOptical').html('<p>XPos:'+json.xval+' Ypos:'+json.yval+' ZPos:'+json.zval+'</p>');
  positionUpdateOptical(json.xval,json.yval,json.zval);
}
