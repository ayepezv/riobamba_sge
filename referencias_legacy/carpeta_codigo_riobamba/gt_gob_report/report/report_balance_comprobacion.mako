<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
      .line {
      border-bottom:1pt solid black;
      }
      .title {
      font-size: 10px;
      }
      .lines {
      font-size: 12px;
      }
    </style>  
  </head>
<body>
%for o in objects:
<% 
     vars = _vars(o)
   %>
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <th style="font-size:20px" WIDTH="100%">BALANCE DE COMPROBACION</th>
  </tr>  
</table>
<!--table cellspacing="0" cellpadding="1" WIDTH="100%">
  <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
    <tr>
      <td style="font-size:18px" WIDTH="15%"><b>Fechas:</b></td>
      <td style="font-size:18px" align="left" WIDTH="85%"><b>Del: ${vars['date_from']} Al: ${vars['date_end']}</b></td>    
    </tr>   
  </thead>
</table-->	
<p></p>	
<table width="100%" cellspacing="0" border="0">
	<colgroup width="85"></colgroup>
	<colgroup width="300"></colgroup>
	<colgroup span="8" width="55"></colgroup>
	<thead style="display: table-header-group" BGCOLOR="#D8D8D8">
	  <tr>
	    <td style="font-size:18px" WIDTH="15%"><b>Fechas:</b></td>
	    <td style="font-size:18px" align="left" WIDTH="85%"><b>Del: ${vars['date_from']} Al: ${vars['date_end']}</b></td>    
	    <td></td>
	    <td></td>
	    <td></td>
	    <td></td>
	    <td></td>
	    <td></td>
	    <td></td>
	    <td></td>
	  </tr>
	  <p>
	  <tr style="font-size:16px">
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 height="34" align="center" valign=middle><b>Codigo</b></td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" rowspan=2 align="center" valign=middle><b>Descripcion</b></td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=middle><b>Saldo inicial</b></td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=middle><b>Flujos</b></td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=middle><b>Sumas</b></td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" colspan=2 align="center" valign=middle><b>Saldos Finales</b></td>
	  </tr>
	  <tr style="font-size:16px">
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Deudor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Acreedor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Deudor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Acreedor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Deudor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Acreedor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Deudor</td>
	    <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">Acreedor</td>
	  </tr>
	</thead>
	<%res=lineas(o)%>
	<%debe_inicial=0%>
	<%haber_inicial=0%>
	<%debe_flujo=0%>
	<%haber_flujo=0%>
	<%debe_suma=0%>
	<%haber_suma=0%>
	<%debe_final=0%>
	<%haber_final=0%>
	<%result_dic=res.values()%>
	<%import operator%>
	<%dic_ord=sorted(result_dic, key=operator.itemgetter('code'))%>
	%for values in dic_ord:
	<!-- %if (values['nivel'] == 1): -->
	%if (values['nivel'] == 1):    
	<%debe_inicial+=values['debe_inicial']%>
	<%haber_inicial+=values['haber_inicial']%>
	<%debe_flujo+=values['debe_flujo']%>
	<%haber_flujo+=values['haber_flujo']%>
	<%debe_suma+=values['debe_suma']%>
	<%haber_suma+=values['haber_suma']%>
	<%debe_final+=values['debe_final']%>
	<%haber_final+=values['haber_final']%>
	%endif
	%if (vars['all_accounts']==True) or (vars['all_accounts']==False and values['nivel']==vars['nivel']) or ((values['nivel'] < vars['nivel']) and values['final']==True):
	%if (values['debe_inicial']!=0 or values['haber_inicial']!=0 or values['debe_flujo']!=0 or values['haber_flujo']!=0 or values['debe_suma']!=0 or values['haber_suma']!=0 or values['debe_final']!=0 or values['haber_final']!=0) or (values['nivel']==1):
	<tr style="page-break-inside:avoid;font-size:16px">
		<td style="border-top: 1px solid #000000;font-size:16px; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left">${ values['code_aux']}</td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">${ values['desc']}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(values['debe_inicial'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['haber_inicial'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['debe_flujo'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['haber_flujo'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['debe_suma'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['haber_suma'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['debe_final'])}</td>
		<td align="right" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(values['haber_final'])}</td>
	</tr>
	%endif
	%endif
	%endfor
	<br/>
	<tr style="page-break-inside:avoid"  style="font-size:14px">
	  <td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" height="17" align="left"></td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" align="left">TOTALES:</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000">${'{:,.2f}'.format(debe_inicial)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(haber_inicial)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(debe_flujo)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(haber_flujo)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(debe_suma)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(haber_suma)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(debe_final)}</td>
		<td align="rigth" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000" >${'{:,.2f}'.format(haber_final)}</td>
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
    <th width="33%">______________________________</th>
    <th width="33%">______________________________</th>
    <th width="33%">______________________________</th>
  </tr>
  <tr style="font-size:13px">
    <th width="33%">CONTADOR GENERAL</th>
    <th width="33%">DIRECTOR FINANCIERO</th>
    <th width="33%">${get_firmas('mx_a')}</th>
  </tr>  
  <tr style="font-size:15px">
    <th width="33%">${get_firmas('cg')}</th>
    <th width="33%">${get_firmas('df')}</th>
    <th width="33%">${get_firmas('ma')}</th>
  </tr>  
</table>
</footer>
</html>
