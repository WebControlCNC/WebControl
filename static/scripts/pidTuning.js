
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
      data = JSON.parse(msg.data);
      if (data.result == "velocity"){
          vErrorPlot = document.getElementById('vErrorPlot');
          console.log(data);
          if ($("#vErrorPlot").html()!="")
              while (vErrorPlot.data.length>0)
                  Plotly.deleteTraces(vErrorPlot, [0]);
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
            Plotly.plot(vErrorPlot, [{y: _setpoint }], {title: "Velocity Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(vErrorPlot, [{y: _input }], {title: "Velocity Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(vErrorPlot, [{y: _output }], {title: "Velocity Error", showlegend: false, colorway: colorwayLayout } );
          }
          else
            Plotly.plot(vErrorPlot, [{y: data.data }], {title: "Velocity Error", showlegend: false, colorway: colorwayLayout } );
      }
      if (data.result == "position") {
          pErrorPlot = document.getElementById('pErrorPlot');
          console.log(data);
          if ($("#pErrorPlot").html()!="")
              while (pErrorPlot.data.length>0)
                  Plotly.deleteTraces(pErrorPlot, [0]);
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
            Plotly.plot(pErrorPlot, [{y: _setpoint }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(pErrorPlot, [{y: _input }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(pErrorPlot, [{y: _output }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(pErrorPlot, [{y: _rpminput }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
            Plotly.plot(pErrorPlot, [{y: _voltage }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
          }
          else
              Plotly.plot(pErrorPlot, [{y: data.data }], {title: "Position Error", showlegend: false, colorway: colorwayLayout } );
      }
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

function vExecute(){
  var vMotor = $('#vMotor label.active input').val();
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
  action('executeVelocityPIDTest',parameters);
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
function pExecute(){
  var pMotor = $('#pMotor label.active input').val();
  var pStart= $("#pStart").val();
  var pStop= $("#pStop").val();
  var pSteps= $("#pSteps").val();
  var pTime= $("#pTime").val();
  var pVersion= $("#pVersion").val();
  var KpP = $('#KpP').val();
  var KiP = $('#KiP').val();
  var KdP = $('#KdP').val();
  var parameters = {pMotor: pMotor,
                    pStart: pStart,
                    pStop: pStop,
                    pSteps: pSteps,
                    pTime: pTime,
                    pVersion: pVersion,
                    KpP: KpP,
                    KiP: KiP,
                    KdP: KdP
                    };
  console.log(parameters);
  action('executePositionPIDTest',parameters);
}

