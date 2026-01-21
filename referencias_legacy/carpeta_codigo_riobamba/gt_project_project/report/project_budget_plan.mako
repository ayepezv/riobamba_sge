<html>
<head>
  <style type="text/css">
    ${css}
    tr.dept td {
    background-color: #454243;
    }
    table th {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ebebeb);
    font-size:12px;
    }
    .project {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ababab), to(#ababab));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
    .task {
	padding:3px 12px 9px 12px;
	border-top:1px solid #fafafa;
	background: -webkit-gradient(linear, left top, left bottom, from(#ebebeb), to(#ebebeb));
	background: -moz-linear-gradient(top,  #ededed,  #ababab);
    font-size:12px;
    }
  </style>
</head>
<body>
  
  <h1 style="text-align:center;" align="center">Reporte de Presupuesto de Proyectos</h1>
  <table class="basic_table" width="100%">
      <tr>
        <th width="55%"></th>
        <th width="15%">Asignación Inicial</th>
        <th width="15%">Comprometido</th>
        <th width="15%">Disponible</th>
      </tr>
  </table>
  %for data in browse_group(objects):
  <table class="basic_table" width="100%">
    <thead>
      <tr class="dept" align="right">
        <th width="55%" style="text-align:center;">${ data['name'] }</th>
        <th width="15%">${ formatLang(data['planned_amount'], digits=2) }</th>
        <th width="15%">${ formatLang(data['commited_amount'], digits=2) }</th>
        <th width="15%">${ formatLang(data['avai_amount'], digits=2) }</th>
      </tr>
    </thead>        
  </table>
  %for o in data['project_ids']:
  <table class="basic_table" width="100%">
    <tbody>
      <tr style="text-align:right;" class="project"> 
        <td style="text-align:left;" width="55%">${ o.name }</td>
        <td width="15%">${ formatLang(sum([t.planned_amount for t in o.tasks]), digits=2) }</td>

        <td width="15%">${ formatLang(commited(o.tasks), digits=2) }</td>
        <td width="15%">${ formatLang(o.amount_budget-commited(o.tasks), digits=2) }</td>
      </tr>
      %for task in o.tasks:
      <tr style="text-align:right;" class="task">
        <td width="55%" style="text-align:left;">${ task.name }</td>
        <td width="15%">${ formatLang(task.planned_amount, digits=2) }</td>
        <td width="15%">${ formatLang(commited([task]), digits=2) }</td>
        <td width="15%">${ formatLang(task.planned_amount-commited([task]), digits=2) }</td>
      </tr>
      <tr>
        <td>
            %for budget in task.budget_planned_ids:
            <tr style="right:0px;">
              <td style="text-align:left;">${ budget.acc_budget_id.code } - ${ budget.acc_budget_id.name } (${ budget.name })</td>
              <td style="text-align:right;">${ formatLang(budget.planned_amount, digits=2) }</td>
              <td style="text-align:right;">${ formatLang(budget.commited_amount, digits=2) }</td>
              <td style="text-align:right;">${ formatLang(budget.avai_amount, digits=2) }</td>
            </tr>
            %endfor
        </td>
      </tr>
      %endfor
    </tbody>
  </table>
  <br>
  %endfor
  %endfor
  <table width="100%">
    <tfoot>
      <% total = get_total(objects) %>
      <tr align="right">
        <th width="55%">TOTALES:</th>
        <th width="15%">${ formatLang(total['planned'], digits=2) }</th>
        <th width="15%">${ formatLang(total['commited'], digits=2) }</th>
        <th width="15%">${ formatLang(total['avai'], digits=2) }</th>
      </tr>
    </tfoot>
  </table>
</body>
</html>
