<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table cellspacing="3" cellpadding="3" WIDTH="100%">
	  <tr>
	    
	  </tr>  
	</table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-size:12px" width="12%">FECHA:</td>
      <td style="font-size:12px" width="58%">${o.date_invoice or ''}</td>
      <td style="font-size:12px" width="12%">RUC:</td>
      <td style="font-size:12px" width="18%">${o.partner_id.ced_ruc or '##########'}</td>
    </tr>
    <tr>
      <td style="font-size:12px" width="12%">CLIENTE:</td>
      <td style="font-size:12px" width="58%">${o.partner_id.name or  ''}</td>
      <td style="font-size:12px" width="12%">TELEFONO:</td>
      <td style="font-size:12px" width="18%">${o.address_invoice_id.phone or ''}</td>
    </tr>
    <tr>
      <td style="font-size:12px" width="12%">DIRECCIÓN:</td>
      <td style="font-size:12px" width="58%">${o.address_invoice_id.street or ''} ${o.address_invoice_id.street2 or ''}</td>
      <td width="12%"></td>
      <td width="18%"></td>
    </tr>       
  </table>
  <p></p>		
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
  <thead>   
    <tr>
      <th align="center" style="font-size:12px" WIDTH="12%">CANTIDAD</th>
      <th align="center" style="font-size:12px" WIDTH="58%">CONCEPTO</th>
      <th align="center" style="font-size:12px" WIDTH="15%">V.UNITARIO</th>
      <th align="center" style="font-size:12px" WIDTH="15%">V. TOTAL</th>                
    </tr>
  </thead>
    %for line in o.invoice_line :
    <tr>
      <td width="12%" style="text-align:center">${line.quantity or ''}</td>
      <td width="58%" style="text-align:left">${line.name or ''}</td>
      <td width="15%" style="text-align:right">${formatLang(line.price_unit, digits=2) }</td>
      <td width="15%" style="text-align:right">${formatLang(line.price_subtotal, digits=2) }</td>
    </tr>
    %endfor     
  <tr height="100">
    <td width="12%" style="text-align:center"></td>
    <td width="58%" style="text-align:left"></td>
    <td width="15%" style="text-align:right"></td>
    <td width="15%" style="text-align:right"></td>
  </tr>
    <tfoot> 
    <tr>    	
		<td style="border:0px" WIDTH="12%"></td>
    	<td style="border:0px" WIDTH="58%"></td>
    	<td style="font-weight: bold;font-size:13px" WIDTH="15%">SUBTOTAL</td>
		<td width="15%" style="text-align:right;font-weight: bold;font-size:13px">${formatLang(o.amount_untaxed or 0.00, digits=2)}</td>
    </tr>
    <tr>
    	<td style="border:0px" WIDTH="12%"></td>
    	<td style="border:0px" WIDTH="58%"></td>
    	<td style="font-weight: bold;font-size:13px" WIDTH="15%">BASE 0%</td>
    	<td width="15%" style="text-align:right;font-weight: bold;font-size:13px">${formatLang(o.amount_vat_cero or 0.00, digits=2)}</td>
    </tr>
    <tr>
    	<td style="border:0px" WIDTH="12%"></td>
    	<td style="border:0px" WIDTH="58%"></td>
    	<td style="font-weight: bold;font-size:13px" WIDTH="15%">BASE 12%</td>
    	<td width="15%" style="text-align:right;font-weight: bold;font-size:13px">${formatLang(o.amount_vat, digits=2)}</td>
    </tr>
    <tr>
    	<td style="border:0px" WIDTH="12%"></td>
    	<td style="border:0px" WIDTH="58%"></td>
    	<td style="font-weight: bold;font-size:13px" WIDTH="15%">IVA 12%</td>
    	<td width="15%" style="text-align:right;font-weight: bold;font-size:13px">${formatLang(o.amount_tax, digits=2)}</td>
    </tr>
    <tr>
    	<td style="border:0px" WIDTH="12%"></td>
    	<td style="border:0px" WIDTH="58%"></td>
    	<td style="font-weight: bold;font-size:13px" WIDTH="15%">TOTAL</td>
    	<td width="15%" style="text-align:right;font-weight: bold;font-size:13px">${formatLang(o.amount_pay, digits=2)}</td>
    </tr>
    </tfoot>
  </table>
   <div style="page-break-before: always"></div>    
  %endfor
</html>
