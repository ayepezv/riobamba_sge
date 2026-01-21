<!DOCTYPE HTML>
<html>
  <head>
</head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
%> 
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:16px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
    <tr>
      <td style="font-size:14px" WIDTH="15%"><b>Fechas:</b></td>
      <td style="font-size:14px" align="left" WIDTH="85%"><b>Del: ${vars['date_from']} Al: ${vars['date_to']}</b></td>    
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td style="font-size:14px" WIDTH="15%"><b>Obra:</b></td>
      %if vars.has_key('mayor_name'):
      <td style="font-size:14px" align="left" WIDTH="85%"><b>${vars['mayor_name']} - ${vars['proyecto_code']}</b></td>
      %else:
      <td style="font-size:14px" align="left" WIDTH="85%"><b>${vars['proyecto_code']}</b></td>    
      %endif
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td style="font-size:14px" WIDTH="15%"><b>Proyecto:</b></td>
      <td style="font-size:14px" align="left" WIDTH="85%"><b>${vars['project_name']}</b></td>    
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td align="left" style="font-size:16px" WIDTH="15%">PARTIDA</td>
      <td align="center" style="font-size:16px" WIDTH="36%">DENOMINACION</td>
      <td align="center" style="font-size:16px" WIDTH="7%">ASIGNACION INCIAL</td>
      <td align="center" style="font-size:16px" WIDTH="7%">REFORMAS</td>
      <td align="center" style="font-size:16px" WIDTH="7%">FINAL</td>
      <td align="center" style="font-size:18px" WIDTH="8%">GAST. Mes</td>
      <td align="center" style="font-size:18px" WIDTH="4%">%</td>
      <td align="center" style="font-size:16px" WIDTH="7%">GAST. Corte</td>
      <td align="center" style="font-size:16px" WIDTH="7%">% </td>
      <td align="center" style="font-size:16px" WIDTH="7%">SALDO ACUMULADO</td>
      <td align="center" style="font-size:16px" WIDTH="7%">% SALDO</td>
    </tr>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0':
  %if (values['nivel'] == 7 or values['nivel'] == 8) and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td style="font-size:18px" WIDTH="15%" align="left">${ values['code']}</td>
    <td style="font-size:18px" WIDTH="36%" align="left">${ values['general_budget_name']}</td>
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['paid_amount_mes'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_rec_mes'])}</td>	    
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['percent_rec'])}</td>	    
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['to_rec'])}</td>
    <td style="font-size:16px" WIDTH="7%" align="right">${'{:,.2f}'.format(values['percent_sal'])}</td>
  </tr>
  %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
<%
   por_pagado = 0
   if res['total']['codif_amount']>0:
       por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
   por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
   saldo_acumulado = res['total']['to_rec']
   por_saldo = 100 - por_pagado
   %>
    <td WIDTH="15%" style="font-weight: bold;font-size:16px" align="right"></td>  
    <td WIDTH="36%" style="font-weight: bold;font-size:18px" align="right">TOTALES</td>        
    <td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>   
<td WIDTH="8%" align="right">${'{:,.2f}'.format(res['total']['paid_amount_mes'])}</td>
<td WIDTH="4%" align="right">${'{:,.2f}'.format(por_pagado_mes)}</td>	    
<td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>    
<td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(por_pagado)}</td>    
    <td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(saldo_acumulado)}</td>    
    <td WIDTH="7%" style="font-weight: bold;font-size:16px" align="right">${'{:,.2f}'.format(por_saldo)}</td>    
  <tfoot>

</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
</table>
</footer>
</html>
