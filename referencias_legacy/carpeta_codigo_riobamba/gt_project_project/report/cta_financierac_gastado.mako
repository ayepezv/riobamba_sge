<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:18;text-align:center;">CUENTA FINANCIERA ENTRE INGRESOS Y GASTOS GASTADO DEL ${o.poa_id.name or  ''} : ${o.tipo or  ''}</td>	  	  
    </tr>
    <tr>
      <td width="100%" style="font-size:18;text-align:center;">GESTION FINANCIERA</td>	
    </tr>
    <tr>
      <td width="100%" style="font-size:18;text-align:center;">PRESUPUESTOS</td>	
    </tr>	
  </table>
<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:20px" WIDTH="15%"><b>Fechas:</b></td>
    <td style="font-size:20px" align="left" WIDTH="85%"><b>Del: ${o.date_from} Al: ${o.date_to}</b></td>    
  </tr>   
</table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:16px">
    <thead style="display: table-header-group">
      <tr BGCOLOR="#D8D8D8">
	<th style="font-size:16px" width="5%">Codigo</th>
        <th style="font-size:16px" width="27%">Cuenta Financiera</th>
        <th style="font-size:16px" width="8%">Pres. Inicial</th>
        <th style="font-size:16px" width="8%">Reformas</th>
        <th style="font-size:16px" width="8%">Pres. Final</th>
        <th style="font-size:16px" width="8%">Ingresos</th>
        <th style="font-size:16px" width="8%">Compromisos</th>
        <th style="font-size:16px" width="8%">Saldos</th>
        <th style="font-size:16px" width="20%">Partida Gasto</th>
      </tr>
    </thead>
    <%
       aux_i = aux_r = aux_f = aux_ing = aux_comp = aux_saldo = 0
       %>
    %for f_id in o.line_ids:
    %for line in f_id.line_ids:
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:16px;text-align:center">${ line.financia_id.name }</td>
      <td width="27%" style="font-size:16px;text-align:left">${ line.financia_id.desc }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.inicial) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.reformas) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.final) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.ingresos) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.compromisos) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(line.saldos) }</td>
      <td width="20%" style="font-size:16px;text-align:left">${ line.desc }</td>
    </tr>
    %endfor
    <%
       aux_i += f_id.inicial
       aux_r += f_id.reformas
       aux_f += f_id.final
       aux_ing += f_id.ingresos
       aux_comp += f_id.compromisos
       aux_saldo += f_id.saldos
       %>
    %if f_id.final!=0:
    <tr style="page-break-inside:avoid" BGCOLOR="#D8D8D8">
      <td width="5%" style="font-size:16px;text-align:center"><b></b> </td>
      <td width="27%" style="font-size:16px;text-align:left"><b>SUBTOTAL</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.inicial) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.reformas) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.final) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.ingresos) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.compromisos) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(f_id.saldos) }</b></td>
      <td width="20%" style="font-size:16px;text-align:left"></td>
    </tr>
    %endif
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:16px;text-align:center"><b></b> </td>
      <td width="27%" style="font-size:16px;text-align:left"><b>TOTAL</b> </td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_i) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_r) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_f) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_ing) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_comp) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(aux_saldo) }</b></td>
      <td width="20%" style="font-size:16px;text-align:left"></td>
    </tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr style="page-break-inside:avoid" BGCOLOR="#D8D8D8">
      <th width="50%" style="font-size:16px;text-align:left"></th>
      <th width="20%" style="font-size:16px;text-align:right"><b>RECAUDADO</b></th>
      <th width="20%" style="font-size:16px;text-align:right"><b>GASTADO</b></th>
      <th width="20%" style="font-size:16px;text-align:right"><b>SALDO</b></th>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:16px;text-align:left"><b>Movimiento Saldo de Caja Bancos</b></td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.recaudado_sc) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.gastado_sc) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.saldo_sc) }</td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:16px;text-align:left"><b>Recaudacion Anio Actual</b></td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.recaudado) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.gastado) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.saldo) }</td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="50%" style="font-size:16px;text-align:left"><b>Total de Recaudacion</b></td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.recaudado_t) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.gastado_t) }</td>
      <td width="20%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(o.saldo_t) }</td>
    </tr>
  </table>
  %endfor
</html>
