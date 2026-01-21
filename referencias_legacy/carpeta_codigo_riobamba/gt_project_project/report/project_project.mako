<html>
  <head>
    <style type="text/css">
      table {
	  font-family:Arial, Helvetica, sans-serif;
	  color:#666;
	  font-size:12px;
	  margin:15px;
	  -moz-border-radius:2px;
	  -webkit-border-radius:1px;
	  -moz-box-shadow: 0 1px 2px #d1d1d1;
	  -webkit-box-shadow: 0 0px 0px #d1d1d1;
      }
      table th {
	  padding:3px 12px 9px 12px;
	  border-top:1px solid #fafafa;
	  background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	  background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
      }
      table th:first-child {
	  text-align: left;
	  padding-left:20px;
      }
      table td {
	  padding:5px;
      }
      h1 {
      font-size:12px;
      }
    </style>
</head>
<body>
  %for o in objects:
  <table cellpadding="0" cellspacing="0" border="0" width="100%">
      <tr>
        <th><b>Componente Operativo</b></th>
        <th><b>Responsable</b></th>
      </tr>
      <tr>
        <td>${ o.department_id.name }</td>
        <td>${ o.user_id.name }</td>
      </tr>
      <tr>
        <th colspan="2">PROYECTO: ${ o.name }</th>
      </tr>
  </table>
  <table cellspacing="0" cellpaddgin="0" border="0" width="100%">
    <thead>
      <th><b>Componente Estratégico</b></th>
      <th><b>Política Pública</b></th>
      <th><b>Programa</b></th>
    </thead>
    <tbody>
      <tr>
        <td>${ o.axis_id.name }</td>
        <td>${ o.estrategy_id.name }</td>
        <td>${ o.program_id.name }</td>        
      </tr>
    </tbody>
  </table>
  <table width="100%">
      <tr>
        <td><b>Antecedentes</b></td>
      </tr>
      <tr>
        <td>${ o.background }</td>
      </tr>
      <tr>
        <td><b>Justificación</b></td>
      </tr>
      <tr>
        <td>${ o.justification }</td>
      </tr>
      <tr>
        <td><b>Objetivo General</b></td>
      </tr>
      <tr>
        <td>${ o.general_objective }</td>
      </tr>
      <tr>
        <td><b>Objectivo Específico</b></td>
      </tr>
      <tr>
        <td>${ o.specific_objectives }</td>
      </tr>
  </table>
  <table width="100%">
      %if o.pointer_detail_ids:
      <tr>
        <td><b>Indicadores y Metas</b></td>
      </tr>
      <tr style="text-align:center;">
        <td width="30%"><b>Nombre</b></td>
        <td width="10%"><b>Tipo</b></td>
        <td width="30%"><b>Fórmula</b></td>
        <td width="10%"><b>META</b></td>
        <td width="20%"><b>Detalle</b></td>
      </tr>
      %for kpi in o.pointer_detail_ids:
      <tr>
        <td>${ kpi.kpi_id.name }</td>
        %if kpi.type_internal=='3avance':
            <td style="text-align:center;">Avance</td>
        %elif kpi.type_internal=='2economico':
            <td style="text-align:center;">Económico ($)</td>
        %elif kpi.type_internal=='1general':
            <td style="text-align:center;">General</td>
        %elif kpi.type_internal=='0impacto':
            <td style="text-align:center;">De Impacto</td>
        %endif
        <td style="text-align:center;">${ kpi.kpi_id.numerador } / ${ kpi.kpi_id.denominador }</td>
        <td style="text-align:center;">${ kpi.planned } (${ kpi.uom_id.name })</td>
        %if kpi.detail:
            <td style="text-align:center;">${ kpi.detail }</td>
        %else:
            <td></td>
        %endif
      </tr>
      %endfor
      %endif
      %if o.close_condition_ids:
      <tr><td><b>Condiciones de Cierre</b></td></tr>
      %for con in o.close_condition_ids:
      <tr><td>${con.name}</td></tr>
      %endfor
      %endif
  </table>
  <table>
    <thead>
      <th>Presupuesto del Proyecto:</th>
      <th></th>
      <th></th>
      <th></th>
      <th>${ o.amount_budget }</th>      
    </thead>    
  </table>
  <table width="100%">
    <tbody>
      %for task in o.tasks:
      <thead>
	<th>Actividad</th>
	<th>Fecha Inicio</th>
	<th>Fecha Fin</th>
	<th>Peso (%)</th>
	<th>Asignado ($)</th>
      </thead>
      <tr>
        <td width="50%" style="text-align:left;">${ task.name }</td>
        <td width="10%" style="text-align:center;">${ task.date_start }</td>
        <td width="10%" style="text-align:center;">${ task.date_end }</td>
        <td width="15%" style="text-align:center;">${ task.weight }</td>
        <td width="15%" style="text-align:right;"><b>${ task.planned_amount }</b></td>
      </tr>
      <tr>
        <td>
          %for budget in task.budget_planned_ids:
          <tr style="font-style:italic;right:0px;">
            <td width="50%" style="text-align:left;">${ budget.budget_post_id.code } - ${ budget.budget_post_id.name }</td>
            <td width="10%"></td>              
            <td width="10%" style="text-align:center;"></td>
            <td width="15%"></td>              
            <td width="15%" style="text-align:right;">${ budget.planned_amount }</td>
            </tr>
          %endfor
        </td>
      </tr>
      %endfor
    </tbody>
  </table>
  <!--table width="100%">
    <tr style="text-align:center;">
      <td style="border: 1px;">Responsable</td>
      <td style="border: 1px;">Aprobado por</td>
    </tr>
  </table-->
  %endfor
</body>
</html>
