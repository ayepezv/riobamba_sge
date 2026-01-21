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
	  <td width="100%" style="font-size:14;text-align:center;">MAYOR DE CUENTA</td>	  	  
	</tr>	
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">DESDE: ${o.date_start or ''}</td>	  	  
	</tr>	
	<tr>
	  <td width="100%" style="font-size:14;text-align:center;">HASTA:${o.date_end or ''}</td>	  	  
	</tr>	
  </table>
  %for line_acc in o.line_ids:
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:9px" width="12%">CUENTA:</td>
      <td style="font-size:11px" width="42%">${line_acc.account_id.code or ''} - ${line_acc.account_id.name or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:7px">
    <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
      <tr>
        <th style="font-size:11px" width="8%">FECHA</th>
        <th style="font-size:11px" width="8%">COMP.</th>
        <th style="font-size:11px" width="50%">REFERENCIA</th>
        <th style="font-size:11px" width="16%">EMPRESA/BENEFICIARIO</th>
        <th style="font-size:11px" width="7%">DEBE</th>
        <th style="font-size:11px" width="7%">HABER</th>
        <th style="font-size:11px" width="7%">SALDO</th>
      </tr>
    </thead>
	<%
	   a=0
	   %>
    <tr>
      <td width="8%" style="font-size:11px;text-align:left">${}</td>
      <td width="8%" style="font-size:11px;text-align:left">${}</td>
      <td width="50%" style="font-size:11px;text-align:left">"SALDO ANTERIOR"</td>
      <td width="16%" style="font-size:11px;text-align:left">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line_acc.saldo_anterior}</td>
    </tr>
    %for line in line_acc.line_line_ids:
	<%
	   a+=1
	   %>
    <tr style="border: 1px solid black;page-break-inside:avoid">
      <td width="8%" style="font-size:11px;text-align:left">${line.date}</td>
      <td width="8%" style="font-size:11px;text-align:left">${line.doc}</td>
      <td width="50%" style="font-size:11px;text-align:left">${line.name}</td>
      <td width="16%" style="font-size:11px;text-align:left">${line.partner_id.ced_ruc} - ${line.partner_id.name}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line.debit}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line.credit}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line.saldo}</td>
    </tr>
    %endfor      
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:8px">
    <tr>
      <td width="79%" style="font-size:11px;text-align:left">SON ${a} COMPROBANTES SUMAN TOTAL: </td>
      <td width="7%" style="font-size:11px;text-align:left">${line_acc.debe}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line_acc.haber}</td>
      <td width="7%" style="font-size:11px;text-align:right">${line_acc.saldo_final}</td>
    </tr>
  </table>
    %endfor      
  <table width="100%">
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="font-size:8px">
      <th width="50%">Creado por</th>
 	</tr>  
	<tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
	</tr>
	<tr style="height:35px">
      <th>__________________</th>
	</tr>
	<tr style="font-size:8px">
      <th width="33%">${user.employee_id.complete_name or ''}</th>
  	</tr>  
  </table>
  %endfor
</html>
