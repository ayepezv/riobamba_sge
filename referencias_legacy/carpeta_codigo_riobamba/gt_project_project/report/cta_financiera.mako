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
  <table WIDTH="100%">
    <tr>
      <td width="100%" style="font-size:18;text-align:center;">CUENTA FINANCIERA ENTRE INGRESOS Y GASTOS COMPROMETIDO DEL ${o.name or  ''}</td>	  	  
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
    <td style="font-size:20px" align="left" WIDTH="85%"><b>Del: ${vars['date_from']} Al: ${vars['date_to']}</b></td>    
  </tr>   
</table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:16px">
    <thead style="display: table-header-group">
      <tr>
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
       p_tt = p_rt = p_ct = p_it = p_gt = p_st = 0
       %>
    <%res_code=_get_code(o)%>
    %for values_code in res_code:
    <%res=_get_totales(o,values_code)%>
    <%result_dic=res.values()%>
    <%import operator%>
    <%dic_ord=sorted(result_dic, key=operator.itemgetter('code'))%>
    <%
       p_t = p_r = p_c = p_i = p_g = p_s = 0
       %>
    %for values in dic_ord:
    <%
       p_t += values['planned_amount']
       p_r += values['reform']
       p_c += values['codificado']
       p_i += values['ingresos']
       p_g += values['gastos']
       p_s += values['saldo']
       %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:16px;text-align:center">${ values['code'] }</td>
      <td width="27%" style="font-size:16px;text-align:left">${ values['name'] }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['planned_amount']) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['reform']) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['codificado']) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['ingresos']) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['gastos']) }</td>
      <td width="8%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(values['saldo']) }</td>
      <td width="20%" style="font-size:16px;text-align:left">${ values['descripcion'] }</td>
    </tr>
    %endfor
    <%
       p_tt += p_t
       p_rt += p_r
       p_ct += p_c
       p_it += p_i
       p_gt += p_g
       p_st += p_s
       %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:16px;text-align:center"><b></b> </td>
      <td width="27%" style="font-size:16px;text-align:left"><b>SUBTOTAL</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_t) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_r) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_c) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_i) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_g) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_s) }</b></td>
      <td width="20%" style="font-size:16px;text-align:left"></td>
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:16px;text-align:center"><b></b> </td>
      <td width="27%" style="font-size:16px;text-align:left"><b>TOTAL</b> </td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_tt) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_rt) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_ct) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_it) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_gt) }</b></td>
      <td width="8%" style="font-size:16px;text-align:right"><b>${ '{:,.2f}'.format(p_st) }</b></td>
      <td width="20%" style="font-size:16px;text-align:left"></td>
    </tr>
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:16px">
    <%
       sc_r = sc_g = sc_s = ra_r = ra_g = ra_s = tr_r = tr_g = tr_s = 0
       sc_r = _get_financia('SC','recaudado')
       sc_g = _get_financia('SC','gastado')
       sc_s = sc_r  - sc_g
       ra_r = _get_financia('ALL','recaudado')
       ra_g = _get_financia('ALL','gastado')
       ra_s = ra_r - ra_g
       tr_r = sc_r + ra_r
       tr_g = sc_g + ra_g
       tr_s = sc_s + ra_s
       %>
    <tr style="page-break-inside:avoid">
      <th width="65%" style="font-size:16px;text-align:left"></th>
      <th width="15%" style="font-size:16px;text-align:right"><b>RECAUDADO</b></th>
      <th width="15%" style="font-size:16px;text-align:right"><b>GASTADO</b></th>
      <th width="15%" style="font-size:16px;text-align:right"><b>SALDO</b></th>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="65%" style="font-size:16px;text-align:left"><b>Movimiento Saldo de Caja Bancos</b></td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(sc_r) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(sc_g) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(sc_s) }</td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="65%" style="font-size:16px;text-align:left"><b>Recaudacion Anio Actual</b></td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(ra_r) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(ra_g) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(ra_s) }</td>
    </tr>
    <tr style="page-break-inside:avoid">
      <td width="65%" style="font-size:16px;text-align:left"><b>Total de Recaudacion</b></td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(tr_r) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(tr_g) }</td>
      <td width="15%" style="font-size:16px;text-align:right">${ '{:,.2f}'.format(tr_s) }</td>
    </tr>
  </table>
  %endfor
</html>
