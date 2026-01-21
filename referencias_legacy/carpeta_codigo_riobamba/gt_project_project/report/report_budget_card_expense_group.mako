<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
%for o in objects:
<% 
     vars = _months(o)
%> 
<table cellspacing="0" cellpadding="0" WIDTH="100%">  
  <tr>
    <th style="font-size:16px" WIDTH="100%">GOBIERNO PROVINCIAL DEL AZUAY</th>
  </tr>
  <tr>
    <th style="font-size:16px" WIDTH="100%">CÉDULA PRESUPUESTARIA DE GASTOS</th>
  </tr>  
</table>	
<table cellspacing="0" cellpadding="0" WIDTH="100%">
  <tr>
    <td style="font-size:11px" >Institución:</td>
    <td style="font-size:11px" >0001</td>
    <td style="font-size:11px">GOBIERNO PROVINCIAL DEL AZUAY</td>
  </tr>
  <tr>
    <td style="font-size:11px" WIDTH="17%" >Unidad Ejecutora:</td>
    <td style="font-size:11px" WIDTH="10%">${o.department_id.sequence}</td>
    <td style="font-size:11px" WIDTH="73%">${o.department_id.name}</td>
    <td></td>
  </tr>
  </table>
  <table cellspacing="0" cellpadding="0" WIDTH="100%"> 
  <tr>
    <td style="font-size:11px" WIDTH="17%">Programa:</td>
    <td style="font-size:11px" WIDTH="83%">${vars['program']}</td>    
  </tr> 
  <tr>
    <td style="font-size:11px" WIDTH="17%">Proyecto:</td>   
    <td style="font-size:11px" WIDTH="83%">${vars['project']}</td> 
  </tr>
  <tr>
    <td style="font-size:11px" WIDTH="17%">Período:</td>
    <td style="font-size:11px" align="left" WIDTH="83%">Desde ${vars['begin']} a ${vars['end']}</td>    
  </tr>    
</table>
<p></p>		
<table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:10px">
  <thead>   
    <tr>
      <th align="center" style="font-size:9px" WIDTH="13%">CÓDIGO</th>
      <th align="center" style="font-size:9px" WIDTH="57%">PARTIDA</th>
      <th align="center" style="font-size:9px" WIDTH="10%">PAGO ACUMULADO</th>
      <th align="center" style="font-size:9px" WIDTH="10%">PAGO COMPROMISO</th>
      <th align="center" style="font-size:9px" WIDTH="10%">SALDO POR DEVENGAR</th>
            
    </tr>
  </thead>
<%res=_get_totales(o)%> 
  %for values in res:
  	%if values['code']!=0:  		  
	  <tr>
	 	%if values['nivel']==1: 
	    	<td WIDTH="13%" style="font-weight: bold" align="center">${ values['code'].split(".")[1]}</td>
	    	<td WIDTH="57%" style="font-weight: bold" align="left">${ values['general_budget_name']}</td>
		    <td WIDTH="10%" style="font-weight: bold" align="right">${ formatLang(float(values['planned_amount']), digits=2)}</td>
		    <td WIDTH="10%" style="font-weight: bold" align="right">${ formatLang(float(values['commited_amount']), digits=2)}</td>
		    <td WIDTH="10%" style="font-weight: bold" align="right">${ formatLang(float(values['balance_acurred_amount']), digits=2)}</td>		    		    		       
	    %else:
	    	<td WIDTH="13%"  align="center">${ values['code'][:-2]}</td>	    
		    <td WIDTH="57%" align="left">${ values['general_budget_name']}</td>
		    <td WIDTH="10%"  align="right">${ formatLang(float(values['planned_amount']), digits=2)}</td>
		    <td WIDTH="10%"  align="right">${ formatLang(float(values['commited_amount']), digits=2)}</td>
		    <td WIDTH="10%"  align="right">${ formatLang(float(values['balance_acurred_amount']), digits=2)}</td>
	    %endif	       
	  </tr>
  %else:
  <tfoot>
    <tr>
    <td WIDTH="13%"></td>
    <td WIDTH="57%" style="font-weight: bold;font-size:11px" align="right">TOTALES</td>
    <td WIDTH="10%" style="font-weight: bold;font-size:11px" align="right">${ formatLang(float(values['planned_amount']), digits=2)}</td>
    <td WIDTH="10%" style="font-weight: bold;font-size:11px" align="right">${ formatLang(float(values['commited_amount']), digits=2)}</td>
    <td WIDTH="10%" style="font-weight: bold;font-size:11px" align="right">${ formatLang(float(values['balance_acurred_amount']), digits=2)}</td>    
    </tr>
  </tfoot>
  %endif  	
  %endfor 
</table> 
%endfor
</body>
</html>
