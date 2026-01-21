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
	<colgroup width="100"></colgroup>
	<colgroup width="660"></colgroup>
	<colgroup width="120"></colgroup>
	<colgroup span="2" width="120"></colgroup>
	<thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	  <tr>
	    <td style="font-size:14px" WIDTH="15%"><b>Fechas:</b></td>
	    <td style="font-size:14px" align="left" WIDTH="85%"><b>Del: ${vars['date_from']} Al: ${vars['date_end']}</b></td>    
	    <td></td>
	    <td></td>
	  </tr>   
	</thead>
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">CUENTAS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">DENOMINACION</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Vigente</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" color="#000000">Año Anterior</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DE EXPLOTACIÓN</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_explotacion']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_explotacion']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resultados('624','62401','62404',['62401','62402','62403','62404']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DE OPERACIÓN</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_operacion']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_operacion']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resultados('621','62101','62199',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('623','62301','62399',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('631','63101','63199',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('633','63301','63399',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('634','63401','63499',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('635','63501','63504',['63501','63504','63505']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">TRANSFERENCIAS NETAS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['transferencias_netas']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['transferencias_netas']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resultados('626','62601','62699',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('636','63601','63699',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO FINANCIERO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_financiero']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_financiero']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resultados('625','62501','62504',['62501','62502','62503','62504']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('635','63502','63507',['63502','63503','63507','63508']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">OTROS INGRESOS Y GASTOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['otros_ingresos_gastos']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['otros_ingresos_gastos']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resultados('624','62421','62427',['62407','62421','62422','62423','62424','62425','62426','62427']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('638','63821','63827',['63808','63821','63822','63823','63824','63825','63826','63827','63837']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('625','62521','62524',['62521','62522','62523','62524']):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('638','63851','63893',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('629','62901','62999',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resultados('639','63901','63999',[]):
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:12px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">RESULTADO DEL EJERCICIO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['resultado_ejercicio']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['resultado_ejercicio']['balance'])}</font></b></td>
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
