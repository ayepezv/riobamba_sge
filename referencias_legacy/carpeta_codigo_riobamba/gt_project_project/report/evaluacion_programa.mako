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
    </tr>
    <tr>
      <td style="font-size:14px" WIDTH="15%"><b>Proyecto:</b></td>
      <td style="font-size:14px" align="left" WIDTH="85%"><b>${vars['program_name']}</b></td>    
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
      <td align="left" style="font-size:18px" WIDTH="10%"><b>Partida</b></td>
      <td align="center" style="font-size:18px" WIDTH="20%"><b>Denominacion</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Inicial</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Reforma</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Final</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Pagado Mes</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Pagado</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Saldo</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
    </tr>
  </thead>
  <%res=_get_totales(o)%>
  <%res_f=_get_totales_funcion(o)%>
  <%res_e=_get_totales_egreso(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
  %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['paid_amount']!=0):
  %if values['nivel']<=5:
  <tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
      <%
       aux1 = len(values['code'])
       %>
    %if aux1>6 and aux1<=9:
    <%
       aux = values['code'][0:]
       %>
    <td WIDTH="10%" align="left">${ aux }</td>
    %elif aux1>9:
      <%
       aux = values['code'][0:]
       %>
      <td WIDTH="10%" align="left">${ aux }</td>
    %else:
    <td WIDTH="10%" align="left">${ values['code']}</td>
    %endif
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
  </tr>
  %endif
  %endif
  %endfor
<tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <%
       por_pagado = por_pagado_mes = saldo_acumulado = 0
       if res['total']['codif_amount']:
           por_pagado = (res['total']['paid_amount']*100) / res['total']['codif_amount']
       if res['total']['codif_amount']:
           por_pagado_mes = (res['total']['paid_amount_mes']*100) / res['total']['codif_amount']
       saldo_acumulado = res['total']['codif_amount'] - res['total']['paid_amount']
       por_saldo = 100 - por_pagado
       %>
    <td WIDTH="10%" style="font-weight: bold;font-size:18px" align="right"></td>  
    <td WIDTH="20%" style="font-weight: bold;font-size:18px" align="right">TOTALES</td>        
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['paid_amount_mes'])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_pagado_mes)}</td>     
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_pagado)}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(saldo_acumulado)}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(por_saldo)}</td>    
</tr>
    %if res_f:
<tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="10%" style="font-weight: bold;font-size:18px" align="right"></td>  
    <td WIDTH="20%" style="font-weight: bold;font-size:18px" align="right">TOTAL FUNCION</td>        
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[0])}</td>
    %if abs(res_f[1])>0.01:
    <td WIDTH="9%" style="font-weight: bold;font-size:14px" align="right">${'{:,.2f}'.format(res_f[1])}</td>
    %else:
    <td WIDTH="9%" style="font-weight: bold;font-size:14px" align="right">${'{:,.2f}'.format(0)}</td>
    %endif
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[2])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[3])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[4])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[5])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[6])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[7])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_f[8])}</td>    
</tr>
    %endif
    %if res_e:
<tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="10%" style="font-weight: bold;font-size:18px" align="right"></td>  
    <td WIDTH="20%" style="font-weight: bold;font-size:18px" align="right">TOTAL EGRESOS</td>        
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[0])}</td>
    %if abs(res_e[1])>0.01:
    <td WIDTH="9%" style="font-weight: bold;font-size:14px" align="right">${'{:,.2f}'.format(res_e[1])}</td>
    %else:
    <td WIDTH="9%" style="font-weight: bold;font-size:14px" align="right">${'{:,.2f}'.format(0)}</td>
    %endif
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[2])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[3])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[4])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[5])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[6])}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[7])}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(res_e[8])}</td>    
</tr>
    %endif
</table>
%endfor
</body>
<footer>
</footer>
</html>
