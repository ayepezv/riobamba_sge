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
	  <td width="100%" style="font-size:12;text-align:right;">Nro. ${o.number or  ''}</td>	  	  
    </tr>	
    </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">SR.(ES):</td>
      <td style="font-size:11px" width="42%">${o.partner_id.name or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">FECHA EMISIÓN:</td>
	  <td style="font-size:11px" width="15%">${o.date or ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">RUC:</td>
      <td style="font-size:11px" width="42%">${o.partner_id.ced_ruc or '##########'}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">TIPO DOCUMENTO:</td>
	  <td style="font-size:11px" width="15%">${(o.type == 'in_invoice') and 'Factura' or ''}</td>	   
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">DIRECCIÓN:</td>
      <td style="font-size:11px" width="42%">${o.address_id.street or ''} ${o.address_id.street2 or ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">EJERCICIO FISCAL:</td>
	  <td style="font-size:11px" width="15%">${o.invoice_id.period_id.fiscalyear_id.name or ''}</td>
    </tr> 
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead>
      <tr>
        <th style="font-size:11px" width="17%">NUM. DOCUMENTO</th>
        <th style="font-size:11px" width="29%">BASE IMPONIBLE DE RETENCION</th>
        <th style="font-size:11px" width="18%">IMP. RETENCION</th>
        <th style="font-size:11px" width="18%">PORCENTAJE</th>
        <th style="font-size:11px" width="18%">VALOR RETENIDO</th>        
      </tr>
    </thead>
    %for line in o.tax_ids:
    <tr>
      <td width="17%" style="font-size:11px;text-align:center">${line.num_document}</td>
      <td width="29%" style="font-size:11px;text-align:center">${formatLang(line.base, digits=2) or ''}</td>
      <td width="18%" style="font-size:11px;text-align:left">${line.tax_group in ['ret_vat_b','ret_vat_srv'] and 'RET. IVA' or 'RET. RENTA'}</td>
      <td width="18%" style="font-size:11px;text-align:center">${line.percent or '0.00'}%</td>
      <td width="18%" style="font-size:11px;text-align:right">${formatLang(abs(line.amount), digits=2) or ''}</td>
    </tr>
    %endfor      
      <tr>
	    <td></td><td></td><td></td>
        <td style="font-weight: bold;font-size:12px;text-align:left">TOTAL RETENIDO:</td>
        <td style="font-weight: bold;font-size:12px;text-align:right">${formatLang(o.amount_total, digits=2)}</td>
      </tr>
  </table>
  %endfor
</html>
