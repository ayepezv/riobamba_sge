<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h4 style="text-align:center;" align="center">DIRECCION FINANCIERA</h4>
   <h5 style="text-align:center;" align="center">PRESUPUESTOS</h5>
   <h6 style="text-align:center;" align="center">FONDOS PROGRAMA: ${ o.program_id.sequence } - ${ o.program_id.name }</h6>
   <table class="table_basic table_title">
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
    <thead style="display: table-header-group">
     <tr>
       <th width="4%">Num.</th>
       <th width="66%">Partida</th>
       <th width="10%">Inicial</th>
       <th width="10%">Comprometido</th>
       <th width="10%">Saldo</th>
     </tr>
    </thead>
    <%
       total_ini = total_c = total_s = aux = 0
       %>
    %for line in o.line_ids:
    <%
       total_ini+=line.inicial
       total_c+=line.comprometido
       total_s += line.saldo
       aux += 1
       %>
    <tr style="page-break-inside:avoid">
      <td width="4%" style="font-size:9px;text-align:center">${aux}</td>
      <td width="66%" style="font-size:9px;text-align:left">${line.budget_id.code} - ${line.budget_id.name}</td>
      <td width="10%" style="font-size:9px;text-align:right">${line.inicial}</td>
      <td width="10%" style="font-size:9px;text-align:right">${line.comprometido}</td>
      <td width="10%" style="font-size:9px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor   
    <tr style="page-break-inside:avoid">
      <td width="4%" style="font-size:11px;text-align:left">${}</td>
      <td width="66%" style="font-size:11px;text-align:left"><b>TOTALES</b></td>
      <td width="8%" style="font-size:11px;text-align:right"><b>${total_ini}</b></td>
      <td width="8%" style="font-size:11px;text-align:right"><b>${total_c}</b></td>
      <td width="8%" style="font-size:11px;text-align:right"><b>${total_s}</b></td>
    </tr>
   </table>
   %endfor
</table>
</body>
</html>
