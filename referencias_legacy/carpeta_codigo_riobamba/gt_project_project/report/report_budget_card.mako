<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
%> 
<table cellspacing="0" cellpadding="1" WIDTH="100%"> 
  <tr>
    <th style="font-size:16px" WIDTH="100%">EJECUCIÓN PRESUPUESTARIA</th>
  </tr>  
</table>
%if data['project']:
<p style="font-weight: bold;">PROYECTO: ${ data['project_name']}</p>
%endif
<p></p>			
<table width="100%" border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:10px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <tr>
      <th></th>
      <th align="center" style="font-size:11px" WIDTH="35%">ACUMULADO HASTA: ${vars['end']}</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr>
      <th align="center" style="font-size:9px" WIDTH="7%">CÓDIGO</th>
      <th align="center" style="font-size:9px" WIDTH="35%">PARTIDA</th>
      <th align="center" style="font-size:9px" WIDTH="8%">CODIFICADO</th>
      <th align="center" style="font-size:9px" WIDTH="8%">DEVENGADO</th>
      <th align="center" style="font-size:8px" WIDTH="8%">DIFERENCIA %</th>
    </tr>
  </thead>
  <%
     project_id = data.get('project_id', False)
     res = _get_extra_data(o)
   %> 
  %for values in res:
  <tr style="border: 1px solid black; page-break-inside: avoid;">
    <td WIDTH="7%" align="center">${values['code']}</td>
    %if values['code']=="":
    <td style="font-size:12px;font-weight: bold;" WIDTH="35%" align="left">${values['general_budget_name']}</td>
    <td style="font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']), digits=2)}</td>
    <td style="font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['devengado_amount']), digits=2)}</td>	  
    <td style="font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']-values['devengado_amount']), digits=2)}</td>
    %elif values['code']==".":
    <td style="text-decoration: underline;font-size:12px;font-weight: bold;" WIDTH="35%" align="left">${values['general_budget_name']}</td>
    <td style="text-decoration: underline;font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']), digits=2)}</td>
    <td style="text-decoration: underline;font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['devengado_amount']), digits=2)}</td>	  
    <td style="text-decoration: underline;font-weight: bold;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']-values['devengado_amount']), digits=2)}</td>
    %else:
    <td style="font-size:8px;" WIDTH="35%" align="left">${values['general_budget_name']}</td>
    <td style="font-size:8px;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']), digits=2)}</td>
    <td style="font-size:8px;" WIDTH="8%" align="right">${formatLang(float(values['devengado_amount']), digits=2)}</td>	  
    <td style="font-size:8px;" WIDTH="8%" align="right">${formatLang(float(values['codif_amount']-values['devengado_amount']), digits=2)}</td>	      
    %endif
  </tr>
  %endfor  
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
    <th width="33%">________________________</th>
    <th width="33%">________________________</th>
    <th width="33%">________________________</th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">CONTADOR GENERAL</th>
    <th width="33%">DIRECTOR FINANCIERO</th>
    <th width="33%">${get_firmas('mx_a')}</th>
  </tr>  
  <tr style="font-size:12px">
    <th width="33%">${get_firmas('cg')}</th>
    <th width="33%">${get_firmas('df')}</th>
    <th width="33%">${get_firmas('ma')}</th>
  </tr>  
</table>
</footer>
</html>
