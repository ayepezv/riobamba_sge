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
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:18px">
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
      <td></td>
    </tr>
    <tr>
    <td align="left" style="font-size:18px" WIDTH="10%">Partida</td>
    <td align="center" style="font-size:18px" WIDTH="20%">Denominacion</td>
    <td align="center" style="font-size:18px" WIDTH="9%">Inicial</td>
    <td align="center" style="font-size:18px" WIDTH="9%">Reforma</td>
    <td align="center" style="font-size:18px" WIDTH="9%">Final</td>
    <td align="center" style="font-size:18px" WIDTH="8%">Pagado Mes</td>
    <td align="center" style="font-size:18px" WIDTH="4%">%</td>
    <td align="center" style="font-size:18px" WIDTH="8%">Pagado</td>
    <td align="center" style="font-size:18px" WIDTH="4%">%</td>
    <td align="center" style="font-size:18px" WIDTH="8%">Saldo</td>
    <td align="center" style="font-size:18px" WIDTH="4%">%</td>
    <td align="center" style="font-size:18px" WIDTH="20%">Financiamiento($)</td>
    </tr>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
  %if vars['completo']:
  <tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="10%" align="left">${ values['code']}</td>
    <td WIDTH="20%" align="left">${ values['general_budget_name']}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['paid_amount_mes'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_rec_mes'])}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_rec'])}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['to_rec'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_sal'])}</td>
    <td WIDTH="20%" align="right">${_get_anio(values['code'],values['general_budget_name'])}</td>
  </tr>
  %elif (values['nivel']  == 5 or values['nivel'] in (8,9)):
  %if values['nivel']  == 5:
  <tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="10%" align="left"><b>${ values['code']}</b></td>
    <td WIDTH="20%" align="left"><b>${ values['general_budget_name']}</b></td>
    <td WIDTH="9%" align="right"><b>${'{:,.2f}'.format(values['planned_amount'])}</b></td>
    <td WIDTH="9%" align="right"><b>${'{:,.2f}'.format(values['reform_amount'])}</b></td>
    <td WIDTH="9%" align="right"><b>${'{:,.2f}'.format(values['codif_amount'])}</b></td>
    <td WIDTH="8%" align="right"><b>${'{:,.2f}'.format(values['paid_amount_mes'])}</b></td>
    <td WIDTH="4%" align="right"><b>${'{:,.2f}'.format(values['percent_rec_mes'])}</b></td>	  
    <td WIDTH="8%" align="right"><b>${'{:,.2f}'.format(values['paid_amount'])}</b></td>
    <td WIDTH="4%" align="right"><b>${'{:,.2f}'.format(values['percent_rec'])}</b></td>	    
    <td WIDTH="8%" align="right"><b>${'{:,.2f}'.format(values['to_rec'])}</b></td>
    <td WIDTH="4%" align="right"><b>${'{:,.2f}'.format(values['percent_sal'])}</b></td>
    <td WIDTH="20%" align="right"><b></b></td>
  </tr>
  %else:
  <tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="10%" align="left">${ values['code']}</td>
    <td WIDTH="20%" align="left">${ values['general_budget_name']}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['paid_amount_mes'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_rec_mes'])}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_rec'])}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(values['to_rec'])}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(values['percent_sal'])}</td>
    <td WIDTH="20%" align="right">${_get_anio(values['code'],values['general_budget_name'])}</td>
  </tr>
  %endif
  %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
    <%
       if res['total']['codif_amount']>0:
           por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
           por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
       else:
           por_pagado = res['total']['paid_amount']
           por_pagado_mes = res['total']['paid_amount_mes']
       saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
       por_saldo = 100 - por_pagado
       %>
    <td WIDTH="10%" style="font-weight: bold;font-size:18px" align="right"></td>  
    <td WIDTH="20%" style="font-weight: bold;font-size:18px" align="right">TOTALES</td>        
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    %if abs(res['total']['reform_amount'])>0.01:
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    %else:
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(0)}</td>
    %endif
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>  
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['paid_amount_mes'])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_pagado_mes)}</td>     
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_pagado)}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(saldo_acumulado)}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_saldo)}</td>  
    <td WIDTH="20%" style="font-weight: bold;font-size:18px" align="right"></td>    
    
  <tfoot>

</table>
%endfor
</body>
<footer>
</footer>
</html>
