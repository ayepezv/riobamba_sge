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
    <th style="font-size:16px" WIDTH="100%">ESTADO DE FLUJO DE EFECTIVO</th>
  </tr>  
</table>
<%res=lineas(o)%>
<%res_act=res['act']%>
<%res_ant=res['ant']%>

<table cellspacing="0" border="0">
  <colgroup width="100"></colgroup>
  <colgroup width="600"></colgroup>
  <colgroup width="150"></colgroup>
  <colgroup span="2" width="150"></colgroup>
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <tr>
      <td style="font-size:11px" WIDTH="15%">Fechas:</td>
      <td style="font-size:11px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_end']}</td>    
      <td></td>
      <td></td>
    </tr>   
  </thead>
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">CUENTAS</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">DENOMINACION</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">Año Vigente</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><b><font face="Arial" size=1 color="#000000">Año Anterior</font></b></td>
  </tr>
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FUENTES CORRIENTES</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['fuentes_corrientes']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['fuentes_corrientes']['balance'])}</font></b></td>
  </tr>
  %for account_id in get_saldo_flujo('11311','11311','11311','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11313','11313','11313','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11314','11314','11314','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11317','11317','11317','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11318','11318','11318','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11319','11319','11319','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">USOS CORRIENTES</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['usos_corrientes']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['usos_corrientes']['balance'])}</font></b></td>
  </tr>
  %for account_id in get_saldo_flujo('21351','21351','21351','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21352','21352','21352','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21353','21353','21353','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21356','21356','21356','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21357','21357','21357','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21358','21358','21358','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">SUPERAVIT/DEFICIT CORRIENTE</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['sd_corriente']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['sd_corriente']['balance'])}</font></b></td>
  </tr>
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FUENTES DE CAPITAL</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['fuentes_capital']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['fuentes_capital']['balance'])}</font></b></td>
  </tr>
  %for account_id in get_saldo_flujo('11324','11324','11324','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11328','11328','11328','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">USOS DE PRODUCCION, INVERSION Y CAPITAL</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['usos_produccion']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['usos_produccion']['balance'])}</font></b></td>
  </tr>
  %for account_id in get_saldo_flujo('21371','21371','21371','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21373','21373','21373','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21375','21375','21375','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21377','21377','21377','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21378','21378','21378','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21384','21384','21384','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('21387','21387','21387','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  %for account_id in get_saldo_flujo('11327','11327','11327','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">(-) ${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">SUPERAVIT/DEFICIT DE CAPITAL</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['sd_capital']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['sd_capital']['balance'])}</font></b></td>
  </tr>
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">SUPERAVIT/DEFICIT BRUTO</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['sd_bruto']['balance'])}</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['sd_bruto']['balance'])}</font></b></td>
  </tr>
  
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FINANCIAMIENTO DEL DEFICIT</font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000"></font></b></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000"></font></b></td>
  </tr>
  %for account_id in get_saldo_flujo('11336','11336','11336','credit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11397','11397','11397','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11398','11398','11398','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FUENTES DE FINANCIAMIENTO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['fuentes_financiamiento']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['fuentes_financiamiento']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_flujo('21394','21394','21394','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21396','21396','21396','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21397','21397','21397','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21398','21398','21398','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21399','21399','21399','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">USOS DE FINANCIAMIENTO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['usos_financiamiento']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['usos_financiamiento']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">SUPERAVIT/DEFICIT DE FINANCIAMIENTO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['sd_financiamiento']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['sd_financiamiento']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FLUJOS NO PRESUPUESTARIOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000"></font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000"></font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FLUJOS NO PRESUPUESTARIOS FUENTES CREDITOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['flujos_no_presupuestariosc']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['flujos_no_presupuestariosc']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_flujo('11340','11340','11340','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11341','11341','11341','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11351','11351','11351','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11377','11377','11377','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11381','11381','11381','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11382','11382','11382','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11383','11383','11383','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11385','11385','11385','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('11393','11393','11393','credit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
  	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FLUJOS NO PRESUPUESTARIOS USOS CREDITOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['flujos_no_presupuestariosd']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['flujos_no_presupuestariosd']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_flujo('21315','21315','21315','debit'):
  <tr style="page-break-inside:avoid;font-size:14px">
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
  </tr>
  %endfor
  	%for account_id in get_saldo_flujo('21381','21381','21381','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
  	%for account_id in get_saldo_flujo('21382','21382','21382','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21383','21383','21383','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21385','21385','21385','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21386','21386','21386','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21393','21393','21393','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_flujo('21395','21395','21395','debit'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FLUJOS NO PRESUPUESTARIOS DEBITOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['flujos_no_presupuestariosd']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['flujos_no_presupuestariosd']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">FLUJOS NETOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['flujos_netos']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['flujos_netos']['balance'])}</font></b></td>
	</tr>
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">VARIACIONES NO PRESUPUESTARIAS CREDITOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['111']['balance']+res_act['112']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['flujos_netos']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_resta('111','111','111',['inicial','final']):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resta('112','112','112',['inicial','final']):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">VARIACIONES NO PRESUPUESTARIAS DEBITOS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['212']['balance']+res_act['61991']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['212']['balance']+res_ant['61991']['balance'])}</font></b></td>
	</tr>
	%for account_id in get_saldo_flujo('61991','61991','61991','balance'):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor
	%for account_id in get_saldo_resta('212','212','212',['final','inicial']):
	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="18" align="left" valign=top bgcolor="#D6D6D6"><font face="Arial" size=1 color="#000000">${account_id[0]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left" valign=top><font face="Arial" size=1 color="#000000">${account_id[1]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top sdval="0" sdnum="3082;"><font face="Arial" size=1 color="#000000">${account_id[2]}</font></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top><font face="Arial" size=1 color="#000000">${account_id[3]}</font></td>
	</tr>
	%endfor

	<tr style="page-break-inside:avoid;font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">VARIACIONES NETAS</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['variaciones_netas']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['variaciones_netas']['balance'])}</font></b></td>
	</tr>
<tr>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="left" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">SUPERAVIT O DEFICIT BRUTO</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6" sdval="0" sdnum="3082;"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_act['sd_bruto2']['balance'])}</font></b></td>
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="right" valign=top bgcolor="#D6D6D6"><b><font face="Arial" size=1 color="#000000">${'{:,.2f}'.format(res_ant['sd_bruto2']['balance'])}</font></b></td>
	</tr>
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
