<!DOCTYPE HTML>
<html>
  <head>
</head>
<body>
%for o in objects:
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:18px" WIDTH="100%">EVALUACION PRESUPUESTARIA DE GASTOS POR PROGRAMA CONSOLIDADO - COMPROMETIDO</th>
  </tr>  
</table>
<p></p>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:18px">
  <tr>
    <td style="font-size:14px" WIDTH="15%"><b>Fechas:</b></td>
    <td style="font-size:14px" align="left" WIDTH="85%"><b>Del: ${o.date_from} Al: ${o.date_to}</b></td>    
  </tr>
</table>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:18px">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
    <tr>
      <td align="center" style="font-size:18px" WIDTH="30%"  BGCOLOR="#D8D8D8"><b>Programa</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Inicial</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Reforma</b></td>
      <td align="center" style="font-size:18px" WIDTH="9%"><b>Final</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Comp. Mes</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Comp.Corte</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
      <td align="center" style="font-size:18px" WIDTH="8%"><b>Saldo</b></td>
      <td align="center" style="font-size:18px" WIDTH="4%"><b>%</b></td>
    </tr>
  </thead>
  <%
     aux_inicial = aux_reforma = aux_codificado = aux_comp_mes = aux_por_mes = aux_comp_acum = aux_por_acum = aux_saldo = aux_por_saldo = 0
     %>
  %for line in o.line_ids:
  <%
     aux_inicial += line.inicial
     aux_reforma += line.reforma
     aux_codificado += line.final
     aux_comp_mes += line.com_mes
     aux_comp_acum += line.com_acum
     aux_saldo += line.saldo
     %>
  <tr style="border: 1px solid black; page-break-inside: avoid;font-size:14px">
    <td WIDTH="30%" align="left">${line.programa_id.sequence} - ${line.programa_id.name}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(line.inicial)}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(line.reforma)}</td>
    <td WIDTH="9%" align="right">${'{:,.2f}'.format(line.final)}</td>
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(line.com_mes)}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(line.por_mes)}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(line.com_acum)}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(line.por_acum)}</td>	    
    <td WIDTH="8%" align="right">${'{:,.2f}'.format(line.saldo)}</td>
    <td WIDTH="4%" align="right">${'{:,.2f}'.format(line.por_saldo)}</td>
  </tr>
  %endfor
  <%
     aux_por_mes = (aux_comp_mes * 100)/aux_codificado
     aux_por_acum = (aux_comp_acum * 100)/aux_codificado
     aux_por_saldo = (aux_saldo * 100)/aux_codificado
     %>
  <tfoot style="display: table-row-group"  BGCOLOR="#D8D8D8">
    <td WIDTH="30%" style="font-weight: bold;font-size:18px" align="right">TOTALES</td>        
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_inicial)}</td>
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_reforma)}</td>
    <td WIDTH="9%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_codificado)}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_comp_mes)}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_por_mes)}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_comp_acum)}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_por_acum)}</td>    
    <td WIDTH="8%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_saldo)}</td>    
    <td WIDTH="4%" style="font-weight: bold;font-size:18px" align="right">${'{:,.2f}'.format(aux_por_saldo)}</td>    
  <tfoot>
</table>
%endfor
</body>
<footer>
</footer>
</html>
