<html>
<head>
    <style type="text/css">
    </style>
</head>
 <body>
   %for o in objects:
   <h5 style="text-align:center;" align="center">DIRECCION FINANCIERA</h5>
   <h6 style="text-align:center;" align="center">PRESUPUESTOS</h6>
   <h6 style="text-align:center;" align="center">MOVIMIENTO DE PARTIDA PRESUPUESTARIA</h6>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
     %if o.partner_id:
     <tr>
       <td>Beneficiario: ${ o.partner_id.ced_ruc } - ${ o.partner_id.name }</td>
     </tr>
     %endif
     <tr>
       <td>Partida: ${ o.budget_id.code } - ${ o.budget_id.name }</td>
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
     <tr>
       <td>Desde: ${ o.date_start }</td>
       <td>Hasta: ${ o.date_end }</td>
     </tr>
   </table>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
     <tr>
       <td>Asignacion Inicial: ${ o.inicial }</td>
       <td>Codificado: ${ o.codificado }</td>
       <td>Comprometido: ${ o.comprometido }</td>
       <td>Devengado: ${ o.devengado }</td>
     </tr>
     <tr>
       <td>Pagado: ${ o.pagado }</td>
       <td>Disponible: ${ o.disponible }</td>
       <td>Saldo Comprometer: ${ o.saldo_comp }</td>
       <td>Saldo Pagar: ${ o.saldo_pay }</td>
     </tr>
   </table>
   <br>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
    <thead style="display: table-header-group">
     <tr>
       <th width="4%">Num.</th>
       <th width="5%">Fecha</th>
       <th width="15%">Beneficiario</th>
       <th width="8%">Num. Compromiso</th>
       <th width="8%">Num. Comprobante</th>
       <th width="40%">Concepto</th>
       <th width="7%">Comprometido</th>
       <th width="7%">Devengado</th>
       <th width="7%">Pagado</th>
     </tr>
    </thead>
    <%
       total_dev = total_pag = total_cp = aux = 0
       %>
    %for line in o.line_ids:
    <%
       total_dev+=line.devengado
       total_pag+=line.pagado
       total_cp+=line.comprometido
       aux += 1
       %>
    <tr style="page-break-inside:avoid">
      <td width="4%" style="font-size:9px;text-align:left">${aux}</td>
      <td width="5%" style="font-size:9px;text-align:left">${line.date}</td>
      <td width="15%" style="font-size:9px;text-align:left">${line.partner_id.name}</td>
      <td width="8%" style="font-size:9px;text-align:left">${line.cp_id}</td>
      <td width="8%" style="font-size:9px;text-align:left">${line.move_id}</td>
      <td width="40%" style="font-size:9px;text-align:left">${line.desc}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.comprometido}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.devengado}</td>
      <td width="7%" style="font-size:9px;text-align:right">${line.pagado}</td>
    </tr>
    %endfor   
    <tr style="page-break-inside:avoid">
      <td width="4%" style="font-size:11px;text-align:left">${}</td>
      <td width="5%" style="font-size:11px;text-align:left">${}</td>
      <td width="15%" style="font-size:11px;text-align:right">${}</td>
      <td width="8%" style="font-size:11px;text-align:left">${}</td>
      <td width="8%" style="font-size:11px;text-align:left">${}</td>
      <td width="40%" style="font-size:11px;text-align:right"><b>TOTALES</b></td>
      <td width="7%" style="font-size:11px;text-align:right"><b>${'{:,.2f}'.format(total_cp)}</b></td>
      <td width="7%" style="font-size:11px;text-align:right"><b>${'{:,.2f}'.format(total_dev)}</b></td>
      <td width="7%" style="font-size:11px;text-align:right"><b>${'{:,.2f}'.format(total_pag)}</b></td>
    </tr>
   </table>
   %endfor
   <br>
   <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:9px">
     <tr>
       <td width="80%" style="font-size:11px;text-align:right">Saldo Comprometer</td>
       <td width="20%" style="font-size:11px;text-align:right">${o.saldo_comp}</td>
     </tr>
     <tr>
       <td width="80%" style="font-size:11px;text-align:right">Saldo Pagar</td>
       <td width="20%" style="font-size:11px;text-align:right">${o.saldo_pay}</td>
     </tr>
   </table>
</table>
</body>
</html>
