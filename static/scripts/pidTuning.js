
var _xError = [];
var _yError = [];
var _xValues = [];
var colorwayLayout = ['#313131','#3D019D','#3810DC','#2D47F9','#2503FF','#2ADEF6','#60FDFA','#AEFDFF','#BBBBBB','#FFFDA9','#FAFD5B','#F7DA29','#FF8E25','#F8432D','#D90D39','#D7023D','#313131']





function updateVErrorCurve(data) {
    console.log(data)
    xCurve = data.curveX;
    yCurve = data.curveY;
    $('#curveChartButton').removeClass('btn-secondary').addClass('btn-primary');
    $('#curveFitButton').removeClass('btn-primary').addClass('btn-secondary');
}

function updatePIDData(msg){
      vErrorPlot = document.getElementById('vErrorPlot');
      data = JSON.parse(msg.data)
      console.log(data);
      if ($("#vErrorPlot").html()!="")
          while (vErrorPlot.data.length>0)
              Plotly.deleteTraces(vErrorPlot, [0]);
      Plotly.plot(vErrorPlot, [{y: data.data }], {title: "Velocity Error", showlegend: false, colorway: colorwayLayout } );
}



$(document).ready(function () {

});



function vExecute(){
  var vMotor = $('#vMotor input:radio:checked').val();
  var vStart= $("#vStart").val();
  var vStop= $("#vStop").val();
  var vSteps= $("#vSteps").val();
  var vVersion= $("#vVersion").val();
  var KpV = $('#KpV').val();
  var KiV = $('#KiV').val();
  var KdV = $('#KdV').val();
  var parameters = {vMotor: vMotor,
                    vStart: vStart,
                    vStop: vStop,
                    vSteps: vSteps,
                    vVersion: vVersion,
                    KpV: KpV,
                    KiV: KiV,
                    KdV: KdV
                    };
  console.log(parameters);
  action('vExecute',parameters);
}

