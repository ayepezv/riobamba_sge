<html>
<head>
    <style type="text/css">
      .line {
      border-bottom:1pt solid black;
      }
      .title {
      font-size: 10px;
      }
      .lines {
      font-size: 12px;
      }
    </style>
</head>
 <body>
   %for o in objects:
   <h3 style="text-align:center;" align="center">DIRECCION FINANCIERA</h3>
   <h3 style="text-align:center;" align="center">CEDULA PRESUPUESTARIA AUXILIAR DE GASTOS</h3>
   <%
      tsc1=tsd1=ti1=tr1=tcodif1=tcomp1=td1=te1=0
      %>
   %for programa in o.line_ids:
   <h3 style="text-align:center;" align="center">PROGRAMA : ${programa.program_id.sequence} - ${programa.program_id.name}</h3>
   <table WIDTH="100%" border="1" cellpadding="0" cellspacing="0"  bordercolor="0" style="border-collapse:collapse;font-size:12px">
     <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
     <tr>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
       <td></td>
     </tr>
       <tr style="border-collapse:collapse;font-size:12px">
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Partida</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Denominacion</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Inicial</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Reforma</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Codificado</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Comprometido</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Saldo Comprometer</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Devengado</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Ejecutado</b></td>
	 <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Saldo Devengar</b></td>
       </tr>
     </thead>
     <%
	tsc=tsd=ti=tr=tcodif=tcomp=td=te=0
	%>
     %for line in programa.line_ids:
     <%
	ti+=line.planned_amount
	tr+=line.reform
	tcodif+=line.codificado
	tcomp+=line.compromiso
	td+=line.devengado
	te+=line.pagado
	tsc+=line.saldo_comprometer
	tsd+=line.saldo_devengar
	ti1+=line.planned_amount
	tr1+=line.reform
	tcodif1+=line.codificado
	tcomp1+=line.compromiso
	td1+=line.devengado
	te1+=line.pagado
	tsc1+=line.saldo_comprometer
	tsd1+=line.saldo_devengar
	%>
     <tr style="page-break-inside:avoid;font-size:12px">
       <td style="border-top: 1px solid #000000;font-size:12px; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${line.code}</td>
       <td style="border-top: 1px solid #000000;font-size:12px; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${line.partida.budget_post_id.name}</td>
       <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.planned_amount)}</td>
       <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.reform)}</td>
       <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.codificado)}</td>
       <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.compromiso)}</td>
       <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.saldo_comprometer)}</td>
      <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.devengado)}</td>
      <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.pagado)}</td>
      <td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(line.saldo_devengar)}</td>
    </tr>
    %endfor   
    <tr style="border-collapse:collapse;font-size:12px">
      <td width="9%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:10px;text-align:right"><b>TOTAL PROGRAMA</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(ti)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tr)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tcodif)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tcomp)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tsc)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(td)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(te)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tsd)}</b></td>
    </tr>
</table>
   %endfor

</table>
   %endfor
<br>
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr style="border-collapse:collapse;font-size:10px">
      <td width="9%" style="font-size:10px;text-align:right"><b>${}</b></td>
      <td width="35%" style="font-size:10px;text-align:right"><b>TOTALES GENERAL</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(ti1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tr1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tcodif1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tcomp1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tsc1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(td1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(te1)}</b></td>
      <td width="7%" style="font-size:10px;text-align:right"><b>${'{:,.2f}'.format(tsd1)}</b></td>
    </tr>
</table>
</table>
<br>
<br>
  <table width="100%">
    <tr style="height:14px">
      <th>__________________</th>
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:14px">
      <th width="33%">Maxima Autoridad</th>
      <th width="33%">Director Financiero</th>
      <th width="33%">Contador</th>
    </tr>  
  </table>
</body>
</html>
