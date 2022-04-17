
var _zError = [];
var _zValues = [];
var colorwayLayout = ['#313131','#3D019D','#3810DC','#2D47F9','#2503FF','#2ADEF6','#60FDFA','#AEFDFF','#BBBBBB','#FFFDA9','#FAFD5B','#F7DA29','#FF8E25','#F8432D','#D90D39','#D7023D','#313131']

function updatezVErrorCurve(data) {
    console.log(data)
    zCurve = data.curveZ;
    $('#curveChartButton').removeClass('btn-secondary').addClass('btn-primary');
    $('#curveFitButton').removeClass('btn-primary').addClass('btn-secondary');
}

function updatezPIDData(msg){
  data = JSON.parse(msg.data);
  if (data.result == "zvelocity"){
      vErrorPlot = document.getElementById('zvErrorPlot');
      console.log(data);
      if ($("#zvErrorPlot").html()!="")
          while (zvErrorPlot.data.length>0)
              Plotly.deleteTraces(zvErrorPlot, [0]);
      if (data.version == "2")
      {
        var _setpoint = [];
        var _input = [];
        var _output = [];
        for (var x = 0; x<data.data.length; x++){
            var ss = data.data[x].split(",");
            _setpoint.push(parseFloat(ss[0]));
            _input.push(parseFloat(ss[1]));
            _output.push(parseFloat(ss[2]));
        }
        Plotly.plot(vErrorPlot, [{y: _setpoint }], {title: "zVelocity Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(vErrorPlot, [{y: _input }], {title: "zVelocity Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(vErrorPlot, [{y: _output }], {title: "zVelocity Error", showlegend: false, colorway: colorwayLayout } );
      }
      else
        Plotly.plot(vErrorPlot, [{y: data.data }], {title: "zVelocity Error", showlegend: false, colorway: colorwayLayout } );
  }
  if (data.result == "zposition") {
      pErrorPlot = document.getElementById('zpErrorPlot');
      console.log(data);
      if ($("#zpErrorPlot").html()!="")
          while (zpErrorPlot.data.length>0)
              Plotly.deleteTraces(zpErrorPlot, [0]);
      if (data.version == "2")
      {
        var _setpoint = [];
        var _input = [];
        var _output = [];
        var _rpminput = [];
        var _voltage = [];
        for (var x = 0; x<data.data.length; x++){
            var ss = data.data[x].split(",");
            _setpoint.push(parseFloat(ss[0]));
            _input.push(parseFloat(ss[1]));
            _output.push(parseFloat(ss[2]));
            _rpminput.push(parseFloat(ss[3]));
            _voltage.push(parseFloat(ss[4]));
        }
        Plotly.plot(zpErrorPlot, [{y: _setpoint }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(zpErrorPlot, [{y: _input }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(zpErrorPlot, [{y: _output }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(zpErrorPlot, [{y: _rpminput }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
        Plotly.plot(zpErrorPlot, [{y: _voltage }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
      }
      else
          Plotly.plot(pErrorPlot, [{y: data.data }], {title: "zPosition Error", showlegend: false, colorway: colorwayLayout } );
  }
}

$(document).ready(function () {

});

function zvExecute(){
  var zvMotor = $('#vMotor label.active input').val();
  var zvStart= $("#vStart").val();
  var zvStop= $("#vStop").val();
  var zvSteps= $("#vSteps").val();
  var zvVersion= $("#vVersion").val();
  var KpVZ = $('#KpVZ').val();
  var KiVZ = $('#KiVZ').val();
  var KdVZ = $('#KdVZ').val();
  var parameters = {zvMotor: zvMotor,
                    zvStart: zvStart,
                    zvStop: zvStop,
                    zvSteps: zvSteps,
                    zvVersion: zvVersion,
                    KpVZ: KpVZ,
                    KiVZ: KiVZ,
                    KdVZ: KdVZ
                    };
  console.log(parameters);
  action('executezVelocityPIDTest',parameters);
}

function zpExecute(){
  var zpMotor = $('#zpMotor label.active input').val();
  var zpStart= $("#zpStart").val();
  var zpStop= $("#pzStop").val();
  var zpSteps= $("#zpSteps").val();
  var zpTime= $("#zpTime").val();
  var zpVersion= $("#pVersion").val();
  var KpPZ = $('#KpPZ').val();
  var KiPZ = $('#KiPZ').val();
  var KdPZ = $('#KdPZ').val();
  var parameters = {zpMotor: zpMotor,
                    zpStart: zpStart,
                    zpStop: zpStop,
                    zpSteps: zpSteps,
                    zpTime: zpTime,
                    zpVersion: zpVersion,
                    KpPZ: KpPZ,
                    KiPZ: KiPZ,
                    KdPZ: KdPZ
                    };
  console.log(parameters);
  action('executezPositionPIDTest',parameters);
}

