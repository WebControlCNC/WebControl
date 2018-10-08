/*var elem = document.getElementById('workarea');
var params = {width: 1000, height: 600};
var two = new Two(params).appendTo(elem);

var rectangle = two.makeRectangle(500,300,1000,600);
var texture = new Two.Texture("/static/images/materials/Plywood_texture.JPG", function() {
});
rectangle.fill = texture
two.update();
*/
var draw = SVG('workarea').size('100%','100%')
//var rect = draw.rect(100,100).attr({fill: '#f06'})
var image = draw.image('/static/images/materials/Plywood_texture.JPG').loaded(function(loader){
  this.size(96,48).scale(12,12).translate(100,60)
})

var gridLines = draw.group()
gridLines.add(draw.line(0,0,96,0).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,48,96,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,24,96,24).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(0,0,0,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(24,0,24,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(48,0,48,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(72,0,72,48).stroke({width:.1, color: '#000'}))
gridLines.add(draw.line(96,0,96,48).stroke({width:.1, color: '#000'}))
gridLines.scale(12,12).translate(100,60)

var sled = draw.group()
sled.add(draw.circle(3).stroke({width:.2,color:"#F00"}).fill({color:"#fff",opacity:0}))
sled.add(draw.line(1.5,-0.5,1.5,3.5).stroke({width:.2,color:"#F00"}))
sled.add(draw.line(-0.5,1.5,3.5,1.5).stroke({width:.2,color:"#F00"}))
sled.translate(-1.5,-1.5)
sled.scale(12,12).translate(100,60)
