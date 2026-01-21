<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
      .line {
      border-bottom:1pt solid black;
      }
      .title {
      font-size: 9px;
      }
      .lines {
      font-size: 10px;
      }
    </style>  
  </head>
<body>
%for o in objects:
<% vars = _vars(o)  %>
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:16px" WIDTH="100%">ESTADO DE RESULTADOS</th>
  </tr>  
</table>
<%res=lineas(o)%>
<%res_act=res['act']%>
<%res_ant=res['ant']%>
<table cellspacing="0" border="0">
	<colgroup width="117"></colgroup>
	<colgroup width="133"></colgroup>
	<colgroup width="453"></colgroup>
	<colgroup span="2" width="151"></colgroup>
	<thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	  <tr>
	    <td style="font-size:11px" WIDTH="15%">Fechas:</td>
	    <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_end']}</td>    
	    <td></td>
	    <td></td>
	  </tr>   
	</thead>
	<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><b><font face="Arial" color="#000000">Guía *</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">CUENTAS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">DENOMINACION</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Vigente</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Anterior</font></b></td>
	</tr>
	<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DE EXPLOTACIÓN</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_explotacion']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_explotacion']['balance'])}</font></b></td>
	</tr>
	<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">62401/04</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">VENTA DE BIENES Y SERVICIOS</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['62401/04']['balance']*-1)}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['62401/04']['balance']*-1)}</font></td>
	</tr>
	<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">63801/04</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) COSTO DE VENTAS</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['63801/04']['balance']*-1)}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['63801/04']['balance']*-1)}</font></td>
	</tr>
	<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DE OPERACIÓN</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_operacion']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_operacion']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 621</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">IMPUESTOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['621']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['621']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 623</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">TASAS Y CONTRIBUCIONES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['623']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['623']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 631</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) GASTOS EN INVERSIONES PÚBLICAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['631']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['631']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 633</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) GASTOS EN REMUNERACIONES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['633']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['633']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 634</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) GASTOS BIENES Y SERVICIOS DE CONSUMO</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['634']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['634']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">63501-04</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) GASTOS FINANCIEROS Y OTROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['63501-04']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['63501-04']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">TRANSFERENCIAS NETAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['transferencias_netas']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['transferencias_netas']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 626</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">TRANSFERENCIAS RECIBIDAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['626']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['626']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 636</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) TRANSFERENCIAS ENTREGADAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['636']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['636']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO FINANCIERO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_financiero']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_financiero']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">62501/04</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">RENTAS DE INVERSIONES Y OTROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['62501/04']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['62501/04']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">63502/03-07</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) GASTOS FINANCIEROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['63502/03-07']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['63502/03-07']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">OTROS INGRESOS Y GASTOS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['otros_ingresos_gastos']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['otros_ingresos_gastos']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">62421/27</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">VENTA DE BIENES Y SERVICIOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['62421/27']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['62421/27']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">63821/27</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) COSTO DE VENTAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['63821/27']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['63821/27']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">62521/24</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">RENTAS DE INVERSIONES Y OTROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['62521/24']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['62521/24']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">63851/93</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) DEPRECIACIONES, AMORTIZACIONES Y OTROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['63851/93']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['63851/93']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 629</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">ACTUALIZACIONES Y AJUSTES DE INGRESOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['629']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['629']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 639</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) ACTUALIZACIONES Y AJUSTES DE GASTOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['639']['balance']*-1)}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['639']['balance']*-1)}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="30" align="left" valign=top bgcolor="#D6D6D6" sdval="61803" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">61803</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DEL EJERCICIO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_ejercicio']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_ejercicio']['balance'])}</font></b></td>
	</tr>
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:11px">
  </tr>
  <tr style="font-size:11px">
    <th width="33%">CONTADOR GENERAL</th>
    <th width="33%">DIRECTOR FINANCIERO</th>
    <th width="33%">${get_firmas('mx_a')}</th>
  </tr>  
  <tr>
  </tr>
  <tr style="height:11px">
    <th width="33%">_____________________</th>
    <th width="33%">_____________________</th>
    <th width="33%">_____________________</th>
  </tr>
  <tr style="font-size:11px">
    <th width="33%">${get_firmas('cg')}</th>
    <th width="33%">${get_firmas('df')}</th>
    <th width="33%">${get_firmas('ma')}</th>
  </tr>  
</table>
</footer>
</html>
