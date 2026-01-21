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
    <th style="font-size:16px" WIDTH="100%">${ user.company_id.name }</th>
  </tr>
  <tr>
    <th style="font-size:16px" WIDTH="100%">ESTADO DE SITUACION FINANCIERA</th>
  </tr>  
</table>
<%res=lineas(o)%>
<%res_act=res['act']%>
<%res_ant=res['ant']%>
<table cellspacing="0" cellpadding="1" WIDTH="100%">
  <tr>
    <td style="font-size:11px" WIDTH="15%">Fechas:</td>
    <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_end']}</td>    
  </tr>   
<table cellspacing="0" border="0">
	<colgroup width="117"></colgroup>
	<colgroup width="167"></colgroup>
	<colgroup width="469"></colgroup>
	<colgroup width="140"></colgroup>
	<colgroup width="143"></colgroup>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><b><font face="Arial" color="#000000">Guia *</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">CUENTAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center" valign=top><b><font face="Arial" color="#000000">DENOMINACION</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Vigente</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Anterior</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">ACTIVO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" color="#000000">${'{:,.2f}'.format(res_act['activo']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="rigth" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">${'{:,.2f}'.format(res_ant['activo']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">CORRIENTE</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['corriente']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['corriente']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG111</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=10 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">DISPONIBILIDADES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['111']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['111']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG112</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">ANTICIPOS DE FONDOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['112']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['112']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG113</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">CUENTAS POR COBRAR</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['113']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['113']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG121</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES TEMPORALES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['121']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['121']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG122</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES PERMANENTES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['122']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['122']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG123</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES EN PRESTAMOS Y ANTICIPOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['123']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['123']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG124</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">DEUDORES FINANCIEROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['124']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['124']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG132</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">EXISTENCIA PARA PRODUCCION Y VENTAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['132']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['132']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG134</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">EXISTENCIA PARA INVERSION</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['134']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['134']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG135</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">EXISTENCIA PARA LA VENTA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['135']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['135']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">LARGO PLAZO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['largo_plazo']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['largo_plazo']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG122</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=3 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES PERMANENTES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['122']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['122']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG123</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES EN PRESTAMOS Y ANTICIPOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['123']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['123']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG124</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">DEUDORES FINANCIEROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['124']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['124']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">ACTIVOS FIJOS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['activos_fijos']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['activos_fijos']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG141</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=8 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">BIENES DE ADMINISTRACION</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['141']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['141']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="14199" sdnum="3082;"><font face="Arial" size=1 color="#000000">14199</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) DEPRECIACIÓN  ACUMULADA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['14199']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['14199']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG142</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">BIENES DE PRODUCCION</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['142']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['142']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="14299" sdnum="3082;"><font face="Arial" size=1 color="#000000">14299</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) DEPRECIACIÓN  ACUMULADA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['14299']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['14299']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG144</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">BIENES DE PROYECTOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['144']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['144']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG14499</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) DEPRECIACIÓN  ACUMULADA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['14499']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['14499']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG145</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">BIENES DE PROGRAMAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['145']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['145']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG14599</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) DEPRECIACIÓN  ACUMULADA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['14599']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['14599']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">INVERSIONES EN PROYECTOS Y PROGRAMAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['inversiones']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['inversiones']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG151</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=4 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES EN OBRAS EN PROCESO</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['151']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['151']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="15198" sdnum="3082;"><font face="Arial" size=1 color="#000000">15198</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) APLICACIÓN DE GASTO DE GESTIÓN</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['15198']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['15198']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG152</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES EN PROGRAMAS EN EJECUCION</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['152']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['152']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="15298" sdnum="3082;"><font face="Arial" size=1 color="#000000">15298</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) APLICACIÓN DE GASTO DE GESTIÓN</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['15298']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['15298']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">OTROS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['otros']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['otros']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG125</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=6 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">CARGOS DIFERIDOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['125']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['125']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="12599" sdnum="3082;"><font face="Arial" size=1 color="#000000">12599</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) AMORTIZACIÓN ACUMULADA</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['12599']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['12599']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG126</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES NO RECUPERABLES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['126']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['126']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="12699" sdnum="3082;"><font face="Arial" size=1 color="#000000">12699</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">( - ) PROVISIÓN PARA INCOBRABLES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['12699']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['12699']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG131</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">EXISTENCIAS PARA CONSUMO</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['131']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['131']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG133</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">INVERSIONES EN PRODUCTOS EN PROCESO</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['133']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['133']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">PASIVO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" color="#000000"> ${'{:,.2f}'.format(res_act['pasivo']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">${'{:,.2f}'.format(res_ant['pasivo']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">CORRIENTES</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['pcorrientes']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['pcorrientes']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG212</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=2 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">DEPOSITOS Y FONDOS DE TERCEROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['212']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['212']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG213</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">CUENTAS POR PAGAR</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['213']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['213']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">LARGO PLAZO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['plargo_plazo']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['plargo_plazo']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG222</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=3 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">TÍTULOS Y VALORES PERMANENTES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['222']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['222']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG223</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">EMPRÉSTITOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['223']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['223']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG224</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">FINANCIEROS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['224']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['224']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">OTROS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['potros']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['potros']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG225</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">CRÉDITOS DIFERIDOS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['225']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['225']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">PATRIMONIO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['patrimonio']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['patrimonio']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG611</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">PATRIMONIO PÚBLICO</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['611']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['611']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG612</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000" rowspan=4 align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">RESERVAS</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['612']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['612']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6" sdval="61801" sdnum="3082;"><font face="Arial" size=1 color="#000000">61801</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">RESULTADOS DE EJERCICIOS  ANTERIORES</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['61801']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['61801']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG619</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">DISMINUCIÓN PATRIMONIAL</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['619']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['619']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG618</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">Resultado del ejercicio vigente</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['618']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['618']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="24" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">TOTAL PASIVO Y PATRIMONIO</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" color="#000000">${'{:,.2f}'.format(res_act['pasivo_patrimonio']['balance'])}</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">${'{:,.2f}'.format(res_ant['pasivo_patrimonio']['balance'])}</font></b></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" color="#000000">CUENTAS DE ORDEN</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">CUENTAS DE ORDEN DEUDORAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">VAL CUENTAS DE ORDEN</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">0</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 911</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">Cuentas de Orden Deudoras</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['911']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['911']['balance'])}</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top><b><font face="Arial" size=1 color="#000000">CUENTAS DE ORDEN ACREEDORAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">VAL CUENTAS ACREEDORAS</font></b></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">0</font></td>
	</tr>
	<tr>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">SG 921</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font color="#000000"><br></font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">Cuentas de Orden Acreedoras</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['921']['balance'])}</font></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['921']['balance'])}</font></td>
	</tr>
</table>
%endfor
</body>
<footer>
  <table style="page-break-inside:avoid" width="100%">
  <tr style="height:35px">
  </tr>
  <tr style="height:35px">
  </tr>
  <tr style="font-size:15px">
    <th width="40%">CONTADOR GENERAL</th>
    <th width="20%"></th>
    <th width="40%">DIRECTOR FINANCIERO</th>
  </tr>  
  <tr>
  </tr>
  <tr>
  </tr>
  <tr style="height:35px">
    <th width="40%">_____________________</th>
    <th width="20%"></th>
    <th width="40%">_____________________</th>
  </tr>
  <tr style="font-size:15px">
    <th width="40%">${user.employee_id.complete_name or ''}</th>
    <th width="20%"></th>
    <th width="40%">${user.context_department_id.manager_id.complete_name or ''}</th>
  </tr>  
</table>
</footer>
</html>
