var socket
var controllerMessages = [];
$(document).ready(function(){
  $("#workarea").width = $("#canvasColumn").width();
  $("#workarea").height = $("#canvascolumn").height();
    namespace = '/MaslowCNC'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function(msg) {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    socket.on('message', function(msg){
        //console.log(msg);
        $('#test').html('<p>' + msg + '</p>');
    });

    socket.on('controllerMessage', function(msg){
        if (controllerMessages.length >50)
          controllerMessages.shift();
        controllerMessages.push(msg.data);
        $('#controllerMessage').html('');
        controllerMessages.forEach(function(message){
          $('#controllerMessage').append(message+"<br>");
        });
    });

    socket.on('positionMessage', function(msg){
      var json = JSON.parse(msg.data);
      $('#positionMessage').html('<p>XPos:'+json.xval+'</p><p>XYos:'+json.yval+'</p><p>ZPos:'+json.zval+'</p>');
      positionUpdate(json.xval,json.yval,json.zval);
    });

    var canvas = new fabric.Canvas('workarea');

    var circle = new fabric.Circle({
      radius: 100,
      fill: '#eef',
      scaleY: 0.5,
      originX: 'center',
      originY: 'center'
    });

    var text = new fabric.Text('hello world', {
      fontSize: 30,
      originX: 'center',
      originY: 'center'
    });

    var group = new fabric.Group([ circle, text ], {
      left: 150,
      top: 100,
      angle: -10
    });

    canvas.add(group);

    function makeLine(coords){
      return new fabric.Line(coords, {
        fill: 'red',
        stroke: 'red',
        strokeWidth: 5,
        stroketable: false,
        evented: false,
      })
    }

    var line1 = makeLine([0,0,96,0]),
        line2 = makeLine([0,48,96,48]),
        line3 = makeLine([0,24,96,24]),
        line4 = makeLine([0,0,0,48]),
        line5 = makeLine([24,0,24,48]),
        line6 = makeLine([48,0,48,48]),
        line7 = makeLine([72,0,72,48]),
        line8 = makeLine([96,0,96,48])

    var gridLines = new fabric.Group([line1, line2, line3, line4, line5, line6, line7, line8], {
      left: 100,
      top: 100,
    });

    canvas.add(gridLines);



});
function action(command){
  //console.log(command);
  socket.emit('action',{data:command});
}



function positionUpdate(x,y,z){
  //_x = originX+x;
  //_y = originY+y
}


/*var scale = 10

var draw = SVG('workarea').size('100%','100%')
var viewbox = draw.viewbox()
var originX = viewbox.width/2
var originY = viewbox.height/2
var currentPosX = 0
var currentPosY = 0
//var rect = draw.rect(100,100).attr({fill: '#f06'})
//var sheet = draw.rect(768,384).fill(draw.image('/static/images/materials/Plywood_texture.JPG',768,384)).scale(96/768*scale,48/384*scale).center(originX,originY)

var gridLines = draw.group()
gridLines.add(draw.line(0,0,96,0).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,48,96,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,24,96,24).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,0,0,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(24,0,24,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(48,0,48,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(72,0,72,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(96,0,96,48).stroke({width:.1, color: '#000'}))
gridLines.center(originX,originY).scale(scale,scale)
//gridLines.scale(scale,scale)

var sled = draw.group()
sled.add(draw.circle(3).stroke({width:.2,color:"#F00"}).fill({color:"#fff",opacity:0}))
sled.add(draw.line(1.5,-0.5,1.5,3.5).stroke({width:.2,color:"#F00"}))
sled.add(draw.line(-0.5,1.5,3.5,1.5).stroke({width:.2,color:"#F00"}))
sled.translate(-1.5,-1.5)
console.log(originX);
console.log(originY);
sled.center(originX,originY).scale(scale,scale)
var vx = Math.floor((originX+10)/scale)
var vy = Math.floor((originY+10)/scale)
console.log(vx)
console.log(vy)
//sled.center(vx,vy)



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
