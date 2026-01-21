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
    <h2 style="font-size:14px">GOBIERNO PROVINCIAL DEL AZUAY</h2>
    <h2 style="font-size:13px">INFRAESTRUCTURA VIAL</h2>
    <h2 style="font-size:12px">Informe de Labores al: ${ data['date_report'] }</h2>
    <h3 style="font-size:11px">Responsable: ${ data['responsable'] }</h3>
    % for datos in process(objects, data):
    <table style="width:100%">
        <tr>
          <th colspan="11"><h2 style="text-align: left; text-decoration: underline; font-size:11px;">${ datos['program_name'] }</h2></th>
        </tr>
        <% 
        avance_actual_program = {}
        avance_anterior_program = {}
        avance_acumulado_program = {}
        %>
        <tr><br></tr>
        % for project in datos['projects']:
        <tr>
          <th class="color_inverted" colspan="1">${ project['canton'] }</th>
          <% 
          avance_actual_cantones = {}
          avance_acumulado_cantones = {}
          avance_anterior_cantones = {}
           %>
        </tr>
        <tr class="title_bold">
          <td width="7%" class="underline">PARROQUIA</td>
          <td width="40%" class="underline">PROYECTO</td>
          <td width="7%" class="underline">INDOLE</td>
          <td width="15%" class="underline">OBRA</td>
          <td width="5%" class="underline">CANTIDAD</td>
          <td width="5%" class="underline">ANCHO</td>
          <td width="5%" class="underline">MONTO ($)</td>
          <td width="5%" class="underline">MODALIDAD</td>
          <td width="5%" class="underline">F. INICIO</td>
          <td width="5%" class="underline">F. FIN</td>
          <td width="5%" class="underline">ESTADO</td>
        </tr>
        % for o in project['projs']:
        <tr class="title">
          <td width="7%">${ o.parish_id.name }</td>
          <td width="40%">${ o.name }</td>
          <td width="7%">${ o.build_indole_id.name }</td>
          <td width="15%">${ o.build_type_id.name }</td>
          <td width="5%">${ o.amount_long_obra and o.amount_long_obra or 0.00 } (${o.uom_id.name})</td>
          <td width="5%">${ o.ancho_obra and o.ancho_obra or 0.00 }</td>
          <td width="5%">${ formatLang(o.inversion_periodo_anterior+o.amount_budget, digits=2) }</td>
          <td width="5%">${ o.build_mode_id.name }</td>
          <td width="5%"> ${ convert_date(o.date_start) } </td>
          <td width="5%"> ${ convert_date(o.date) } </td>
          <td width="5%">${ STATES_LOG[o.state] }</td>
        </tr>
        <tr>
          <td colspan="11">OBSERVACIONES: ${ o.description and o.description or '** Sin Observaciones **' }</td>          
        </tr>
        <tr>
          <td class="td_line" colspan="12">
        </tr>
        <tr>
          <table width="100%">
            <tbody>
            <tr>
              <td width="7%"></td>
              <%  
              cols = len(o.pointer_detail_ids)
              kpis = [kpi.id for kpi in o.pointer_detail_ids]
              %>
              % for kpi in o.pointer_detail_ids:
              <td width="7%" class="title4 centered"><strong>${ kpi.kpi_id.name } (${ kpi.uom_id.name })</strong></td>
              % endfor
            </tr>
            <tr>
              <td width="%">Avance Anterior:</td>
              % for kpi in o.pointer_detail_ids:
              <% 
              avance_anterior = get_before(kpi.id, kpi.project_id.id)
              base = 1
              if kpi.planned>0:
                  base = kpi.planned
              %>

              <%
              if avance_anterior_cantones.get(kpi.id):
                  avance_anterior_cantones[kpi.id] += avance_anterior
              else:
                  avance_anterior_cantones[kpi.id] = avance_anterior

              if avance_anterior_program.get(kpi.id):
                  avance_anterior_program[kpi.id] += avance_anterior
              else:
                  avance_anterior_program[kpi.id] = avance_anterior                  
              %>

              <td class="right" width="7%">${ formatLang(avance_anterior) } - ${ formatLang(avance_anterior*100.0/base) }%</td>
              % endfor
            </tr>
            <tr>
              <td width="7%">Avance Actual:</td>
              % for kpi in o.pointer_detail_ids:
              <%
              base = 1
              if kpi.planned>0:
                  base = kpi.planned               
              avance_actual = get_value(kpi.id,kpi.project_id.id) - get_before(kpi.id,kpi.project_id.id) 
              %>

              <%
              if avance_actual_cantones.get(kpi.id):
                  avance_actual_cantones[kpi.id] += avance_actual
              else:
                  avance_actual_cantones[kpi.id] = avance_actual

              if avance_actual_program.get(kpi.id):
                  avance_actual_program[kpi.id] += avance_actual
              else:
                  avance_actual_program[kpi.id] = avance_actual                  
              %>

              <td class="right" width="7%">${ formatLang( avance_actual ) } - ${ formatLang(avance_actual*100.0/base) }%</td>
              % endfor
            </tr>
            <tr>
              <td width="7%">ACUMULADO:</td>
              % for kpi in o.pointer_detail_ids:
              <% 
              base = 1
              if kpi.planned>0:
                  base = kpi.planned              
              avance_acumulado = get_value(kpi.id,kpi.project_id.id) 
              %>

              <%
              if avance_acumulado_cantones.get(kpi.id):
                  avance_acumulado_cantones[kpi.id] += avance_acumulado
              else:
                  avance_acumulado_cantones[kpi.id] = avance_acumulado

              if avance_acumulado_program.get(kpi.id):
                  avance_acumulado_program[kpi.id] += avance_acumulado
              else:
                  avance_acumulado_program[kpi.id] = avance_acumulado                  
              %>              
              <td class="td_line right" width="7%">${ formatLang(avance_acumulado) } - ${ formatLang(avance_acumulado*100.0/base) }%</td>
              % endfor
            </tr>
          </tbody>
          </table>
        </tr>
        % endfor  <!-- fin proyectos por canton -->
        <tr>
          <table width="100%">
            <tbody>
            <!-- total por canton  -->
              <tr>
                <td width="7%" class="color_inverted" colspan="1">TOTAL ${ o.canton_id.name }</td>
                <td width="7%"></td>              
              </tr>
              <tr>
                <td width="7%" class="centered">Avance Anterior:</td>
                % for i in kpis:
                <td class="right" width="7%">${ formatLang(avance_anterior_cantones[i]) }</td>
                % endfor
              </tr>
              <tr>
                <td width="7%" class="centered">Avance Actual:</td>
                % for i in kpis:
                <td class="right" width="7%">${ formatLang(avance_actual_cantones[i]) }</td>
                % endfor
              </tr>
              <tr>
                <td class="td_line centered" width="7%">ACUMULADO:</td>
                % for i in kpis:
                <td class="td_line right" width="7%">${ formatLang(avance_acumulado_cantones[i]) }</td>
                % endfor
              </tr> 
            </tbody>
          </table>
        </tr>
        % endfor <!-- fin de cantones-->        
        <!-- totales por programa -->
        <tr>
          <table width="100%">
            <tbody>
              <tr>
                <td width="7%" class="color_inverted" colspan="${len(kpis)+1}">TOTAL ${o.build_program_id.name}</td>
              </tr>
              <tr>
                <td width="7%" class="right">Avance Anterior:</td>            
                % for i in kpis:
                <td class="right" width="7%">${ formatLang(avance_anterior_program[i]) }</td>
                % endfor
              </tr>
              <tr>
                <td width="7%" class="right">Avance Actual:</td>
                % for i in kpis:
                <td class="right" width="7%">${ formatLang(avance_actual_program[i]) }</td>
                % endfor
              </tr>
              <tr>
                <td class="td_line right" width="7%">ACUMULADO:</td>
                % for i in kpis:
                <td class="td_line right" width="7%">${ formatLang(avance_acumulado_program[i]) }</td>
                % endfor
              </tr>
            </tbody>
          </table>
        </tr>
    </table>
    % endfor
    <p style="page-break-after:always"></p>
  </body>
</html>
