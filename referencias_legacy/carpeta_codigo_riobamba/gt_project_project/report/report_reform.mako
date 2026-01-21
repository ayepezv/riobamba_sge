<!DOCTYPE HTML>
<html>
  <head>
</head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
%> 
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:16px" WIDTH="100%">${ user.company_id.name }</th>
  </tr>
  <tr>
    <th style="font-size:16px" WIDTH="100%">REPORTE DE REFORMA</th>
  </tr>  
</table>

<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:11px" WIDTH="15%">Fechas:</td>
    <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_to']}</td>    
  </tr>   
</table>	
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
      <th align="left" style="font-size:9px" WIDTH="7%">PARTIDA</th>
      <th align="center" style="font-size:9px" WIDTH="29%">DENOMINACION</th>
      <th align="center" style="font-size:9px" WIDTH="7%">ASIGNACION INCIAL</th>
      <th align="center" style="font-size:9px" WIDTH="7%">SUPLEMENTO</th>
      <th align="center" style="font-size:9px" WIDTH="7%">REDUCCION</th>
      <th align="center" style="font-size:9px" WIDTH="7%">TRASPASO AUMENTO</th>
      <th align="center" style="font-size:9px" WIDTH="7%">TRASPASO DISMINUCION</th>
      <th align="center" style="font-size:9px" WIDTH="7%">TOTAL</th>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['devengado_amount']!=0 or values['paid_amount']!=0):
       %if (vars['nivel'] > 0 and values['nivel']== vars['nivel']) or vars['nivel']==0:
	  <tr style="border: 1px solid black; page-break-inside: avoid;">
	    <td WIDTH="7%" align="left">${ values['code']}</td>
	    <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
	    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
	  </tr>
        %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right"></td>  
    <td WIDTH="29%" style="font-weight: bold;font-size:11px" align="right">TOTALES</td>        
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>    
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['devengado_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['devengado_balance'])}</td>           
  <tfoot>
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="font-size:13px">
    <th width="40%">IMPRESO POR</th>
    <th width="20%"></th>
    <th width="40%">DIRECTOR FINANCIERO</th>
  </tr>  
  <tr>
  </tr>
  <tr>
  </tr>
  <tr style="height:35px">
    <th width="40%">_____________________</th>
    <th width="20%"></th>
    <th width="40%">_____________________</th>
  </tr>
  <tr style="font-size:15px">
    <th width="40%">${user.employee_id.complete_name or ''}<br/>${user.employee_id.job_id and user.employee_id.job_id.name  or ''}</th>
    <th width="20%"></th>
    <th width="40%">${user.context_department_id.manager_id.complete_name or ''}</th>
  </tr>  
</table>
</footer>
</html>
