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
    <th style="font-size:16px" WIDTH="100%">REFORMA DE ${o.tipo}</th>
  </tr>  
  <tr>
    <th style="font-size:16px" WIDTH="100%">PROGRAMA: ${o.program_id.sequence} -  ${o.program_id.name}</th>
  </tr>  
</table>
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
      <th align="left" style="font-size:9px" WIDTH="20%">PARTIDA</th>
      <th align="center" style="font-size:9px" WIDTH="30%">DENOMINACION</th>
      <th align="center" style="font-size:9px" WIDTH="8%">ASIGNACION INCIAL</th>
      <th align="center" style="font-size:9px" WIDTH="8%">SUPLEMENTO</th>
      <th align="center" style="font-size:9px" WIDTH="8%">REDUCCIONES</th>
      <th align="center" style="font-size:9px" WIDTH="8%">TRASPASO AUMENTO</th>
      <th align="center" style="font-size:9px" WIDTH="8%">TRASPASO DISMINUCION</th>
      <th align="center" style="font-size:9px" WIDTH="8%">NUEVO PRESUPUESTO</th>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  <% planned_p = aumento_p = disminucion_p = suplemento_p = reduccion_p = final_p = 0 %>
  %for values in dic_ord:
  %if values.has_key('nivel') and values['nivel']==0:
  <%
     aux_total = 0
     planned_p = values['planned_amount']
     aumento_p =  values['suplemento']
     disminucion_p = values['disminucion']
     suplemento_p = values['traspaso_aumento']
     reduccion_p = values['traspaso_disminucion']
     #final_p = values['total']
     final_p = planned_p + aumento_p - disminucion_p + suplemento_p - reduccion_p
     %>
  %endif
  %if values['code']!=0 and values['nivel']<=5 and values['nivel']>0 and (values['suplemento']!=0 or values['disminucion']!=0 or values['traspaso_aumento']!=0 or values['traspaso_disminucion']!=0):
    <%
       aux_total=values['planned_amount']+values['suplemento']-values['disminucion']+values['traspaso_aumento']-values['traspaso_disminucion']
       %>
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" align="left"> ${o.program_id.sequence}.${ values['code']}</td>
    <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['suplemento'])}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['disminucion'])}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['traspaso_aumento'])}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['traspaso_disminucion'])}</td>
    <td WIDTH="7%" align="right">${'{:,.2f}'.format(aux_total)}</td>
    <!--td WIDTH="7%" align="right">${'{:,.2f}'.format(values['total'])}</td-->
  </tr>
  %endif
  %endfor
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" align="left"></td>
    <td WIDTH="29%" align="left"><b>TOTAL PROGRAMA</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(planned_p)}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(aumento_p)}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(disminucion_p)}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(suplemento_p)}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(reduccion_p)}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(final_p)}</b></td>
  </tr>
  <!--tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" align="left"></td>
    <td WIDTH="29%" align="left"><b>TOTAL FUNCION</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'planned'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'aumento'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'disminucion'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'suplemento'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'reduccion'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_funcion(o,'final'))}</b></td>
  </tr-->
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" align="left"></td>
    <td WIDTH="29%" align="left"><b>TOTAL GENERAL</b></td>
    %if o.tipo=='GASTO':
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(o.rfg_id.inicial)}</b></td>
    %elif o.tipo=='INGRESO':
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(o.rfi_id.inicial)}</b></td>
    %else:
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'planned'))}</b></td>
    %endif
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'aumento'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'disminucion'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'suplemento'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'reduccion'))}</b></td>
    <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(_get_general(o,'final'))}</b></td>
  </tr>
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th width="33%">_____________________</th>
    <th width="33%">_____________________</th>
    <th width="33%">_____________________</th>
  </tr>
  <tr style="font-size:13px">
    <th width="33%">JEFE PRESUPUESTOS</th>
    <th width="33%">DIRECTOR FINANCIERO</th>
    <th width="33%">ALCALDE</th>
  </tr>  
  <tr style="font-size:13px">
    <th width="33%"></th>
    <th width="33%"></th>
    <th width="33%"></th>
  </tr>  
</table>
</footer>
</html>
