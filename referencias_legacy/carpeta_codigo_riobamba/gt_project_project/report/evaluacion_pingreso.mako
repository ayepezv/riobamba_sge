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
    <th style="font-size:16px" WIDTH="100%">EVALUACION PRESUPUESTARIA DE INGRESOS</th>
  </tr>  
</table>
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
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
      <td align="left" style="font-size:12px" WIDTH="7%"><b>PARTIDA</b></td>
      <td align="center" style="font-size:12px" WIDTH="29%"><b>DENOMINACION</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>ASIGNACION INCIAL</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>REFORMAS</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>FINAL</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>RECAUDADO</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>% RECAUDADO</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>SALDO ACUMULADO</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>% SALDO</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>SUPERAVIT</b></td>
      <td align="center" style="font-size:12px" WIDTH="7%"><b>% SUPERAVIT</b></td>
    </tr>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
  %if (vars['nivel'] > 0 and values['nivel']== vars['nivel']) or vars['nivel']==0:
  <%
     porcentaje = 0
     if values['codif_amount']>0:
  porcentaje = (values['superavit'] * 100) / values['codif_amount']
  %>
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" style="font-size:12px" align="left">${ values['code']}</td>
    <td WIDTH="29%" style="font-size:12px" align="left">${ values['general_budget_name']}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['percent_rec'])}</td>
    %if values['superavit']>0:
    <%
       aux_saldo = values['to_rec'] #+ values['superavit']
       #aux_saldo = 0 
       #aux_saldo = values['codif_amount'] - values['paid_amount']
       %>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(aux_saldo)}</td>
    %else:
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['to_rec'])}</td>
    %endif
    %if (100-values['percent_rec'])<0:
				      `<td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(0)}</td>
				      %else:				      
				      <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(100-values['percent_rec'])}</td>
				      %endif
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(values['superavit'])}</td>
    <td WIDTH="7%" style="font-size:12px" align="right">${'{:,.2f}'.format(porcentaje)}</td>
  </tr>
  %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
    <%
       por_pagado = 0
       if res['total']['codif_amount']>0:
           por_pagado = abs((res['total']['paid_amount']*100) / res['total']['codif_amount'])
       saldo_acumulado = abs(res['total']['codif_amount'] - res['total']['paid_amount'])
       por_saldo = 100 - por_pagado
    %>
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right"></td>  
      <td WIDTH="29%" style="font-weight: bold;font-size:12px" align="right">TOTALES</td>        
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(por_pagado)}</td>    
      <!--td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(saldo_acumulado)}</td-->    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['to_rec'])}</td>    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(por_saldo)}</td>    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['superavit'])}</td>    
      <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['percent_super'])}</td>    
      <tfoot>
</table>
%endfor
</body>
<footer>
</footer>
</html>
