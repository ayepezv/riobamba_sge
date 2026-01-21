<html>
<head>
  <style type="text/css">
    #container {
    width : 600px;
    height: 384px;
    margin: 8px auto;
    }
    td {
    padding:2px 4px 2px 4px;
    font-size:10px;
    }
    table th {
	padding:3px 8px 6px 8px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:11px;
    }
  </style>
</head>
 <body>
   %for o in objects:
   <table width="100%">
     <tr>
     </tr>
     <tr>
       <th style="font-size:12px;" colspan="2">${ o.department_id.name }</th>
     </tr>
     <tr>
       <th width="15%">PROYECTO:</td>
       <th style="font-size:11px;" width="85%">${ o.name }</td>
     </tr>
   </table>
   <style type="text/css">
     #container_${o.id} {
     width : 600px;
     height: 384px;
     margin: ${objects.index(o) * 8}px auto;
     }
   </style>
   <div id="container_${o.id}"></div>
    <!--[if IE]>
    <script type="text/javascript" src="/static/lib/FlashCanvas/bin/flashcanvas.js"></script>
    <![endif]-->
    <script type="text/javascript" src="http://humblesoftware.com/static/js/hsd-flotr2.js?d3fa1"></script>
    <script type="text/javascript">
(function basic_bars(container, horizontal) {

  var
    horizontal = (horizontal ? true : false), // Show horizontal bars
    d1 = [],                                  // First data series
    d2 = [],                                  // Second data series
    point,                                    // Data point variable declaration
    i;

  d1.push([1,${ formatLang(get_scope(o), digits=2) }], [2,${ formatLang(get_time(o), digits=2) }],[3,${ formatLang(get_money(o), digits=2)}]);
  markers = {data: d1,
             markers: {
                 show: true,
                 position: 'ct'
             }
            };
  // Draw the graph
  Flotr.draw(
    container,
    [d1,markers],
    {
      title: "AVANCE DE PROYECTO",
      bars : {
        show : true,
        horizontal : horizontal,
        shadowSize : 0,
        barWidth : 0.5,
      },
      xaxis : {
       ticks: [[1, "AMBITO %"],[2, "TIEMPO %"],[3,"DINERO %"]],
      },
      mouse : {
        track : true,
        relative : true
      },
      yaxis : {
        min : 0,
        autoscaleMargin : 1,
        title: "Avance Porcentual",
      }
    }
  );
})(document.getElementById( "container_${o.id}" ));
    </script>
    <h3 style="font-size:13px;" >Avance Total: ${ o.activity_progress }%</h3>
    <h3 style="font-size:13px;">Detalle de Información de Avance</h3>
    <table width="100%">
      <tr>
        <th colspan="4">AMBITO</th>
      </tr>
      <tr>
        <th width="70%">INDICADOR</th>
        <th width="10%">PESO</th>
        <th width="10%">META</th>
        <th width="10%" aling="right">AVANCE (%)</th>
      </tr>
      %for kpi in o.pointer_detail_ids:
      <tr>
        <td width="70%" align="left">${ kpi.kpi_id.name } (${kpi.kpi_id.formula})</td>
        <td width="10%" align="center">${ kpi.weight }</td>
        <td width="10%" align="center">${ kpi.planned }</td>
        <td width="10%" align="right">${ formatLang(kpi.progress, digits=2) }%</td>
      </tr>
      %endfor
    </table>
    <table width="100%">
      <tr>
        <th colspan="5">TIEMPO</th>
      </tr>
      <tr>
        <th width="68%">ACTIVIDAD</th>
        <th width="8%">FECHA INICIO</th>
        <th width="8%">FECHA FIN</th>
        <th width="8%">PESO</th>
        <th width="8%">AVANCE (%)</th>
      </tr>
      %for task in o.tasks:
      <tr>
        <td width="64%">${ task.name }</td>
        <td width="8%">${ task.date_start }</td>
        <td width="8%">${ task.date_end }</td>
        <td width="8%" align="center">${ task.weight }</td>
        <td width="8%" align="right">${ formatLang(task.progress_time, digits=2) }%</td>
      </tr>
      %endfor
    </table>

    <table width="100%">
      <tr>
        <th colspan="3">DINERO</th>
      </tr>
      <tr>
        <th width="74%">ACTIVIDAD</th>
        <th width="13%">PRESUPUESTO</th>
        <th width="13%">AVANCE (%)</th>
      </tr>
      %for task in o.tasks:
      <tr>
        <td width="74%">${ task.name }</td>
        <td width="13%" align="right">${ task.planned_amount }</td>
        <td width="13%" align="right">${ formatLang(task.progress_money2, digits=2) }%</td>
      </tr>
      %endfor
    </table>
    <p style="page-break-after:always"></p>
   %endfor
</body>
</html>
