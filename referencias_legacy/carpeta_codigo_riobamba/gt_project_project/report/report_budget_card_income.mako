<!DOCTYPE HTML>
<html>
  <head>
  </head>
  <body>
    %for o in objects:
    <% 
       vars = _vars(o)
       %> 
    <table cellspacing="0" cellpadding="0" WIDTH="100%">
      <tr>
	<th style="font-size:16px" WIDTH="100%">CEDULA DE INGRESOS</th>
      </tr>  
    </table>
    <p></p>
    <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
      <thead style="display: table-header-group" BGCOLOR="#D8D8D8">   
	<tr>
	  <td style="font-size:14px" WIDTH="15%">Fechas:</td>
	  <td style="font-size:14px" align="left" WIDTH="85%">Del: ${vars['date_from']} Al: ${vars['date_to']}</td>    
	  <td></td>
	  <td></td>
	  <td></td>
	  <td></td>
	  <td></td>
	  <td></td>
	</tr>
	<tr>
	  <td align="left" style="font-size:12px" WIDTH="7%">PARTIDA</td>
	  <td align="center" style="font-size:12px" WIDTH="29%">DENOMINACION</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">ASIGNACION INCIAL <br>(1)</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">REFORMAS <br> (2)</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">CODIFCADO <br>(3)=1+2</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">DEVENGADO <br>(4)</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">RECAUDADO <br>(5)</td>
	  <td align="center" style="font-size:12px" WIDTH="7%">SALDO POR DEVENGAR <br>(6)=3-4</td>
	</tr>
      </thead>
      <%res=_get_totales(o)%>
      <%result_dic=res.values()%>
      <%import operator%>
      <%dic_ord=sorted(result_dic, key=operator.itemgetter('code_aux'))%>
      %for values in dic_ord:
      %if values['code']!=0 and values['code']!='0' and (values['planned_amount']!=0 or values['reform_amount']!=0 or values['codif_amount']!=0 or values['devengado_amount']!=0 or values['paid_amount']!=0):
      %if vars['tipo_nivel']=='p':
      %if (values['nivel']<= vars['nivel']) or vars['nivel']==0:
			     <tr style="border: 1px solid black; page-break-inside: avoid;" BGCOLOR="#D8D8D8">
			       <td WIDTH="7%" align="left" >${ values['code']}</td>
			       <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
			       <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
			     </tr>
			     %endif
			     %elif vars['tipo_nivel']=='h':
			     %if (values['nivel']>= vars['nivel']) or vars['nivel']==0:
	<tr style="border: 1px solid black; page-break-inside: avoid;">
	  <td WIDTH="7%" align="left">${ values['code']}</td>
	  <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
	</tr>
	%endif
	%else:
	%if (vars['nivel'] > 0 and values['nivel']== vars['nivel']) or vars['nivel']==0:
	%if values['final']:
	<tr style="border: 1px solid black; page-break-inside: avoid;">
	  <td WIDTH="7%" align="left">${ values['code']}</td>
	  <td WIDTH="29%" align="left">${ values['general_budget_name']}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['planned_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['reform_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['codif_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['paid_amount'])}</td>
	  <td WIDTH="7%" align="right">${'{:,.2f}'.format(values['devengado_balance'])}</td>
	</tr>
	%else:
	<tr style="border: 1px solid black; page-break-inside: avoid;">
	  <td WIDTH="7%" align="left"><b>${ values['code']}</b></td>
	  <td WIDTH="29%" align="left"><b>${ values['general_budget_name']}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['planned_amount'])}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['reform_amount'])}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['codif_amount'])}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['devengado_amount'])}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['paid_amount'])}</b></td>
	  <td WIDTH="7%" align="right"><b>${'{:,.2f}'.format(values['devengado_balance'])}</b></td>
	</tr>
	%endif
    %endif
  %endif
  %endif
  %endfor
  <tfoot style="display: table-row-group">
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right"></td>  
    <td WIDTH="29%" style="font-weight: bold;font-size:12px" align="right">TOTALES</td>        
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['planned_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['reform_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['codif_amount'])}</td>    
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['devengado_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['paid_amount'])}</td>
    <td WIDTH="7%" style="font-weight: bold;font-size:12px" align="right">${'{:,.2f}'.format(res['total']['devengado_balance'])}</td>           
  <tfoot>
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
