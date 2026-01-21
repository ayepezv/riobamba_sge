<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h2 style="text-align:center;" align="center">DIRECCION FINANCIERA</h1>
   <h4 style="text-align:center;" align="center">PRESUPUESTO ESIGEF DETALLADO</h4>
   <h5 style="text-align:center;" align="center">INGRESOS</h5>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
     <thead>
       <tr>
	 <td style="font-size:14px" WIDTH="5%"><b>Fechas:</b></td>
	 <td style="font-size:14px" align="left" WIDTH="35%"><b>Del: ${o.date_start} Al: ${o.date_stop}</b></td>    
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
       <tr style="border-collapse:collapse;font-size:14px">
	 <td width="5%">Codigo</td>
	 <td width="35%">Denominacion</td>
	 <td width="7%">Inicial</td>
	 <td width="7%">Reforma</td>
	 <td width="7%">Codificado</td>
	 <td width="7%">Comprometido</td>
	 <td width="7%">Devengado</td>
	 <td width="7%">Ejecutado</td>
	 <td width="5%">R4</td>
	 <td width="5%">R6</td>
	 <td width="5%">R7</td>
	 <td width="5%">R8</td>
       </tr>
     </thead>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
    <%
       ti=tr=tcodif=tcomp=td=te=0
       %>
    %for line in o.line_ids:
    <%
       ti+=line.inicial
       tr+=line.reforma
       tcodif+=line.codificado
       tcomp+=line.comprometido
       td+=line.devengado
       te+=line.ejecutado
       %>
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <td width="5%" style="font-size:14px;text-align:left">${line.code}</td>
      <td width="35%" style="font-size:14px;text-align:left">${line.post_id.name}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.inicial)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.reforma)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.codificado)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.comprometido)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.devengado)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.ejecutado)}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r4}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r6}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r7}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r8}</td>
    </tr>
    %endfor   
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <td width="5%" style="font-size:14px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:14px;text-align:right"><b>TOTALES INGRESOS</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(ti)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tr)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcodif)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcomp)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(td)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(te)}</b></td>
    </tr>
   </table>
</table>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<h5 style="text-align:center;" align="center">GASTOS</h5>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
  <thead>
    <tr>
      <td style="font-size:14px" WIDTH="5%"><b>Fechas:</b></td>
      <td style="font-size:14px" align="left" WIDTH="35%"><b>Del: ${o.date_start} Al: ${o.date_stop}</b></td>    
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
    <tr style="border-collapse:collapse;font-size:14px">
      <td width="5%">Codigo</td>
      <td width="35%">Denominacion</td>
      <td width="7%">Inicial</td>
      <td width="7%">Reforma</td>
      <td width="7%">Codificado</td>
      <td width="7%">Comprometido</td>
      <td width="7%">Devengado</td>
      <td width="7%">Ejecutado</td>
      <td width="5%">R4</td>
      <td width="5%">R6</td>
      <td width="5%">R7</td>
      <td width="5%">R8</td>
     </tr>
  </thead>
</table>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:14px">
  <%
     ti=tr=tcodif=tcomp=td=te=0
     %>
  %for line in o.line_ids2:
    <%
       ti+=line.inicial
       tr+=line.reforma
       tcodif+=line.codificado
       tcomp+=line.comprometido
       td+=line.devengado
       te+=line.ejecutado
       %>
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <td width="5%" style="font-size:14px;text-align:left">${line.code}</td>
      <td width="35%" style="font-size:14px;text-align:left">${line.post_id.name}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.inicial)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.reforma)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.codificado)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.comprometido)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.devengado)}</td>
      <td width="7%" style="font-size:14px;text-align:right">${'{:,.2f}'.format(line.ejecutado)}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r4}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r6}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r7}</td>
      <td width="5%" style="font-size:14px;text-align:right">${line.r8}</td>
    </tr>
    %endfor   
    <tr style="border: 1px solid black; page-break-inside: avoid;">
      <td width="5%" style="font-size:14px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:14px;text-align:right"><b>TOTALES GASTOS</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(ti)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tr)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcodif)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(tcomp)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(td)}</b></td>
      <td width="7%" style="font-size:14px;text-align:right"><b>${'{:,.2f}'.format(te)}</b></td>
    </tr>
   </table>
   %endfor
</table>
<br>
<br>
  <table width="100%">
    <tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:22px">
      <th width="33%">Maxima Autoridad</th>
      <th width="33%">Director Financiero</th>
      <th width="33%">Contador</th>
    </tr>  
  </table>
</body>
</html>
