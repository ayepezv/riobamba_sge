<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
      .line {
      border-bottom:1pt solid black;
      }
      .title {
      font-size: 11px;
      }
      .lines {
      font-size: 12px;
      }
    </style>  
  </head>
<body>
%for o in objects:
<% vars = _vars(o)  %>
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:16px" WIDTH="100%">ESTADO DE SITUACION FINANCIERA</th>
  </tr>  
</table>
<%res=lineas(o)%>
<%res_act=res['act']%>
<%res_ant=res['ant']%>
<table cellspacing="0" border="0">
  <colgroup width="100"></colgroup>
  <colgroup width="500"></colgroup>
  <colgroup width="200"></colgroup>
  <colgroup span="2" width="200"></colgroup>
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <tr>
      <td style="font-size:11px" WIDTH="15%">Fechas:</td>
      <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_end']}</td>    
      <td></td>
      <td></td>
    </tr>	  
    <tr>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">CUENTAS</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">DENOMINACION</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">Año Vigente</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">Año Anterior</font></b></td>
    </tr>
    <thead>
    <tr style="page-break-inside:avoid;font-size:12px">
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="14" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">ACTIVO</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['activo']['balance'])}</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="rigth" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['activo']['balance'])}</font></b></td>
    </tr>
    <tr style="page-break-inside:avoid;font-size:12px">
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">CORRIENTE</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['corriente']['balance'])}</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['corriente']['balance'])}</font></b></td>
    </tr>
    %for account_id in get_saldo_situacion('111','11101','11199'):
    <tr style="page-break-inside:avoid;font-size:12px">
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
    </tr>
    %endfor
    %for account_id in get_saldo_situacion('112','11201','11299'):
    <tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('113','11301','11399'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('121','12101','12199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('129','12901','12999'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('131','13101','13199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('132','13201','13299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">INVERSIONES LARGO PLAZO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['largo_plazo']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['largo_plazo']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('122','12201','12299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('123','12301','12399'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('124','12401','12499'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('125','12501','12599'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('126','12601','12699'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('128','12801','12899'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">INVERSIONES EN BIENES DE LARGA DURACION ACTIVOS FIJOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['activos_fijos']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['activos_fijos']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('141','14101','14198'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14199','14199','14199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('142','14201','14298'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14299','14299','14299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('143','14301','14398'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14399','14399','14399'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('144','14401','14498'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14499','14499','14499'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('145','14501','14598'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14599','14599','14599'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('146','14601','14698'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14699','14699','14699'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('147','14701','14798'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14799','14799','14799'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('148','14801','14898'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14899','14899','14899'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('149','14901','14998'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('14999','14999','14999'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">INVERSIONES EN PROYECTOS Y PROGRAMAS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['inversiones']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['inversiones']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('133','13301','13399'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[2])}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[3])}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('135','13501','13599'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[2])}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[3])}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('151','15101','15197'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[2])}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[3])}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('15198','15198','15198'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('152','15201','15297'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('15298','15298','15298'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor

    <tr style="page-break-inside:avoid;font-size:12px">
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">ACTIVOS INTANGIBLES</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['otros']['balance'])}</font></b></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['otros']['balance'])}</font></b></td>
    </tr>
    %for account_id in get_saldo_situacion('191','19101','19199'):
    <tr style="page-break-inside:avoid;font-size:12px">
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[2])}</font></td>
      <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(account_id[3])}</font></td>
    </tr>
    %endfor
	
	
	<tr style="page-break-inside:avoid;font-size:12px">
<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">PASIVO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['pasivo']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="rigth" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['pasivo']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">CORRIENTE</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['pcorrientes']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['pcorrientes']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('212','21201','21299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('213','21301','21399'):
	%if account_id[2]>0.01 or account_id[2]<-0.01: 
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endif
	%endfor
	%for account_id in get_saldo_situacion('221','22101','22199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">LARGO PLAZO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['plargo_plazo']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['plargo_plazo']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('222','22201','22299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('223','22301','22399'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('224','22401','22499'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">OTROS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['potros']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['potros']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('225','22501','22599'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('226','22601','22699'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">PATRIMONIO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['patrimonio']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="rigth" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['patrimonio']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('611','61101','61199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('612','61201','61299'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('61803','61803','61803'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('619','61901','61999'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('618','61801','61899'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font color="#000000"><br></font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">TOTAL PASIVO PATRIMONIO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['pasivo_patrimonio']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="rigth" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['pasivo_patrimonio']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">CUENTAS DE ORDEN</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000"></font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000"></font></b></td>
	</tr>
	%for account_id in get_saldo_situacion('911','91101','91199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_situacion('921','92101','92199'):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
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
