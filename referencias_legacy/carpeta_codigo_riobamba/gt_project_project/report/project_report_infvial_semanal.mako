<html>
  <style type="text/css">
    .title {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:12px;
    }
    h1, h2 {
    text-align: center;
    }
    th {
    text-align: left;
    }
    tr {
    font-size: 11px;
    }
    .title_bold {
    font-weight: bold;
    }
    .td_line {
    border-bottom: solid 1px black;
    }
    .color_inverted {
    background-color: black;
    color: white;
    }
    .underline {
    text-decoration: underline;
    font-size: 10px;
    }
    .title4 {
    font-size:10px;
    }
    .centered {
    text-align: center;
    }
    .right {
    text-align: right;
    }
  </style>
  <head>
    <meta charset="UTF-8">
  </head>
  <body>
    <%
    STATES_LOG = {'done_poa': 'Cerrado por Ejercicio Fiscal',
                  'plan_done': u'Planificación Terminada',
                  'exec': u'Ejecución',
                  'exec_ok': u'Ejecución Aprobada',
                  'exec_done': u'Ejecución Terminada',
                  'plan_ok': u'Planificación Aprobada',
                  'cancelled': 'Cancelado', 'expost_done': 'ExPost Terminado',
                  'done': 'Finalizado', 'template': 'Template',
                  'done_wo_end': 'Cerrado sin Terminar',
                  'expost_ok': 'ExPost Aprobado',
                  'expost': 'ExPOST', 'open': u'Planificación',
                  'pending': 'Suspendido'}    
    %>
    <h2 style="font-size:15px">GOBIERNO PROVINCIAL DEL AZUAY</h2>
    <h2 style="font-size:14px">INFRAESTRUCTURA VIAL</h2>
    <h2 style="font-size:14px">INFORME DE AVANCES DE OBRA POR PROGRAMA</h2>
    <h3 style="font-size:13px; text-align:left;">Semana: ${ data['week']} - ${ data['fy'] }</h3>
    <table>
      <thead>
	<tr>
	  <th>Canton</th>
	  <th>Parroquia</th>
	  <th>Obra</th>
	  <th>Proyecto</th>
	  <th>Estado</th>
	  <th>Indole</th>
	  <th>Cantidad</th>
	  <th>% Año Actual</th>
	  <th>% Acum.</th>
	  <th>Resp.</th>
	  <th colspan="12">Indicadores</th>
	  <th>Avance Año Act.(km)</th>
	  <th>Avance Total(km)</th>
	  <th>Inversión Año Act.($)</th>
	  <th>Inversión a la Fecha($)</th>
	</tr>
      </thead>
      <tbody>
	% for datos in process(objects, data):
        <tr>
          <th colspan="3"><h2 class="color_inverted" colspan="1" style="text-align: left; text-decoration: underline; font-size:11px;">${ datos['program_name'] }</h2></th>
        </tr>
        <tr><br></tr>
	% for o in datos['projects']:
        <tr>
	  <td width="8%">${ o.canton_id.name }</td>
          <td width="7%">${ o.parish_id.name }</td>
          <td width="15%">${ o.build_type_id.name }</td>
          <td width="30%">${ o.name }</td>
          <td width="5%">${ STATES_LOG[o.state] }</td>
          <td width="7%">${ o.build_indole_id.name }</td>
	  <td width="8%" style="text-align:right;">${ formatLang(o.activity_progress, digits=2) } %</td>
	  <td width="10%" style="text-align:right;">${ formatLang(o.avance_percent_anterior, digits=2) } %</td>
	  <td width="10%" style="text-align:right;">${ formatLang(o.activity_progress+o.avance_percent_anterior, digits=2) } %</td>
	  <td width="10%">${ o.user_id.login }</td>
	  <td colspan="12">
	    <table>
	    <tr>
	  % for kpi in o.pointer_detail_ids:
	  % if kpi.kpi_id.to_report:
	      <td width="5%" style="font-size:8px;text-align:left;">${ kpi.kpi_id.name }</td>
	      <td width="5%">-</td>
	  % endif
	  % endfor
	    </tr>
	    </table>
	  </td>
	  <td style="text-align:right;">0.00</td>
	  <td style="text-align:right;">0.00</td>
	  <td style="text-align:right;">0.00</td>
          <td style="text-align:right;" width="5%">${ formatLang(o.inversion_periodo_anterior+o.amount_budget, digits=2) }</td>
        </tr>	
	% endfor
	<tr>
	  <td colspan="9"></td>
	  <td class="color_inverted" style="text-align-right;">TOTALES</td>
	  <td colspan="12">
	    <table>
	    <tr>
	  % for kpi in group_kpis(datos['projects']):
	  <td width="5%" style="font-size:8px;text-align:left;">${ kpi['name'] }</td>
	  <td width="5%">${ kpi['valor'] }</td>
	  % endfor
	    </tr>
	    </table>
	  </td>	  
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>	  
	</tr>
	% endfor
	<tr>
	  <td colspan="9"></td>
	  <td class="color_inverted" style="text-align-right;">TOTALES GENERALES</td>
	  <td colspan="12">
	    <table>
	    <tr>
	  % for kpi in group_kpis(datos['projects']):
	      <td width="5%">0.00</td>
	  % endfor
	    </tr>
	    </table>
	  </td>
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>
	  <td style="text-align:right;"><strong>0.00</strong></td>	  
	</tr>
      </tbody>
    </table>
  </body>
</html>
