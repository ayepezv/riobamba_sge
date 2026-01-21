<!DOCTYPE HTML>
<html>
  <head>
</head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
%> 
<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:11px" WIDTH="15%">Fechas:</td>
    <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']}</td>    
  </tr>   
</table>	
<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:12px" align="center" WIDTH="85%"><b>PROFORMA PRESUPUESTARIA DE GASTOS</b></td>    
  </tr>  
  <tr>
    <td style="font-size:11px" align="center" WIDTH="15%"><b>PROGRAMA ${o.program_id.sequence} - ${o.program_id.name}</b></td>
  </tr>   
</table>	
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
      <th align="left" style="font-size:9px" WIDTH="7%">PARTIDA</th>
      <th align="center" style="font-size:9px" WIDTH="29%">DENOMINACION</th>
      <th align="center" style="font-size:9px" WIDTH="7%">ASIGNACION INCIAL <br>(1)</th>
  </thead>
  <%res=_get_totales(o)%>
  <%result_dic=res.values()%>
  <%import operator%>
  <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
  %for values in dic_ord:
%if values.has_key('final'):
  %if len(values['code'])<=6 and values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0):
      <tr style="border: 1px solid black; page-break-inside: avoid;">
        <td WIDTH="7%" align="left">${ values['code']}</td>
        <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
        <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
      </tr>
      %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
    <tr>
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right"></td>  
      <td WIDTH="29%" style="font-weight: bold;font-size:11px" align="right">TOTAL PROGRAMA</td>        
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    </tr>
    %if o.program_id.sequence in ('1.1','2.1','3.1','5.1'):
    <tr>
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right"></td>  
      <td WIDTH="29%" style="font-weight: bold;font-size:11px" align="right">TOTAL FUNCION</td>        
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(_get_total_funcion(o.program_id,o.poa_id))}</td>
    </tr>
    %endif
    %if o.program_id.sequence=='1.1':
    <tr>
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right"></td>  
      <td WIDTH="29%" style="font-weight: bold;font-size:11px" align="right">TOTAL PRESUPUESTO</td>        
      <td WIDTH="7%" style="font-weight: bold;font-size:11px" align="right">${'{:,.2f}'.format(o.poa_id.total_presupuesto)}</td>
    </tr>
    %endif
  <tfoot>
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:10px">
  </tr>
  <tr style="font-size:10px">
  </tr>  
</table>
</footer>
</html>
