<html>
<head>
    <style type="text/css">
      body h2 {
      font-size:14px;
      }
      h2 {
      align:center;
      }
      #container {
        width : 600px;
        height: 384px;
        margin: 8px auto;
      }
    </style>
</head>
<title>Reporte de Indicadores por Proyecto</title>
 <body>
   %for o in objects:
   <table>
     <tr>
       <td><h2>REPORTE DE INDICADORES POR PROYECTO</h2></td>
     </tr>
     <tr>
       <td><h2>PROYECTO: ${ o.name }</h2></td>
     </tr>
   </table>
   <table width="100%">
     %for kpi in o.pointer_detail_ids:
    <div id="container"></div>
    <!--[if IE]>
    <script type="text/javascript" src="/static/lib/FlashCanvas/bin/flashcanvas.js"></script>
    <![endif]-->
    <script type="text/javascript" src="https://raw.github.com/HumbleSoftware/Flotr2/master/flotr2.min.js"></script>
    <script type="text/javascript">
(function basic_bars(container, horizontal) {

  var
    horizontal = (horizontal ? true : false), // Show horizontal bars
    d1 = [],                                  // First data series
    d2 = [],                                  // Second data series
    point,                                    // Data point variable declaration
    i;

//    d1 = [[0,100], [1,60]];
//    d2 = [[2,20], [3,12]];

  for (i = 0; i < 4; i++) {

    if (horizontal) { 
      point = [Math.ceil(Math.random()*10), i];
    } else {
      point = [i, Math.ceil(Math.random()*10)];
    }

    d1.push(point);
    console.log(d1);     
    if (horizontal) { 
      point = [Math.ceil(Math.random()*10), i+0.5];
    } else {
      point = [i+0.5, Math.ceil(Math.random()*10)];
    }

    d2.push(point);
  };
   

  // Draw the graph
  Flotr.draw(
    container,
    [d1, d2],
    {
      bars : {
        show : true,
        horizontal : horizontal,
        shadowSize : 0,
        barWidth : 0.5
      },
      mouse : {
        track : true,
        relative : true
      },
      yaxis : {
        min : 0,
        autoscaleMargin : 1
      }
    }
  );
})(document.getElementById("container"));
    </script>
     <thead style="align-text:center;">
       <tr>
         <th><b>INDICADOR</b></th>
         <th><b>FORMULA</b></th>
         <th><b>META</b></th>
       </tr>
       <tr>
         <th>${ kpi.kpi_id.name }</th>
         <th>${ kpi.kpi_id.formula }</th>
         <th>${ kpi.planned } (${ kpi.uom_id.name })</th>
       </tr>
       <tr><td>Detalle de Avance</td></tr>
     </thead>
     <tbody style="text-align:center;">
       <tr>
       </tr>
       %for work in kpi.work_ids:
       <tr>
         <td>${ work.date }</td>
         <td>${ work.name }</td>
         <td>${ work.exec_done } (${ work.uom_id.name })</td>
       </tr>
       %endfor
       <tr>
         <td></td>
       </tr>
     </tbody>
     %endfor
   </table>
   %endfor
</body>
</html>
