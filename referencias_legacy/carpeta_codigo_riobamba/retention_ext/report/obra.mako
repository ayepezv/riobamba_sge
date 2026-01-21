<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr BGCOLOR="#A4A4A4">
      <td width="100%" style="font-size:14;text-align:center;">LIQUIDACION DE OBRA/CONTRATO Nro. ${o.num_contrato or  ''}</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Nombre Contrato:</td>
      <td style="font-size:11px" width="75%">${o.name or  ''}</td>
    </tr>	
    <tr BGCOLOR="#A4A4A4">
      <td style="font-weight: bold;font-size:11px" width="25%">Doc. Presupuestario:</td>
      <td style="font-size:11px" width="75%">${o.certificate_id.name or  ''} -  ${o.certificate_id.notes or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Financiamiento:</td>
      <td style="font-size:11px" width="75%">${o.financiamiento.name or  ''} -  ${o.financiamiento.desc or  ''}</td>
    </tr>	
    <tr BGCOLOR="#A4A4A4">
      <td style="font-weight: bold;font-size:11px" width="25%">Proveedor</td>
      <td style="font-size:11px" width="75%">${o.partner_id.ced_ruc or ''} - ${o.partner_id.name or ''}</td>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Administrador</td>
      <td style="font-size:11px" width="75%">${o.administrador_id.name or ''}</td>
    </tr> 
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >  
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Fecha Inicio:</td>
      <td style="font-size:11px" width="25%">${o.date_start or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">Fecha Fin:</td>
      <td style="font-size:11px" width="25%">${o.date_end or  ''}</td>
    </tr>	
    <tr BGCOLOR="#A4A4A4">
      <td style="font-weight: bold;font-size:11px" width="25%">Plazo:</td>
      <td style="font-size:11px" width="25%">${o.plazo or  ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">Fecha Anticipo:</td>
      <td style="font-size:11px" width="25%">${o.date_anticipo or  ''}</td>
    </tr>	
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Monto(Sin IVA)</td>
      <td style="font-size:11px" width="25%">${o.monto_sin_iva or ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">IVA</td>
      <td style="font-size:11px" width="25%">${o.iva or ''}</td>
    </tr>
    <tr BGCOLOR="#A4A4A4">
      <td style="font-weight: bold;font-size:11px" width="25%">IVA</td>
      <td style="font-size:11px" width="25%">${o.iva or ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">Reajustes</td>
      <td style="font-size:11px" width="25%">${o.total_reajuste or ''}</td>
    </tr> 
    <tr>
    </tr> 
    <tr>
      <td style="font-weight: bold;font-size:11px" width="25%">Anticipo Entregado(%)</td>
      <td style="font-size:11px" width="25%">${o.porcentaje_anticipo or ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">Monto Anticipo</td>
      <td style="font-size:11px" width="25%">${o.anticipo_entregado or ''}</td>
    </tr> 
    <tr BGCOLOR="#A4A4A4">
      <td style="font-weight: bold;font-size:11px" width="25%">Total Pagos</td>
      <td style="font-size:11px" width="25%">${o.total_pagado or ''}</td>
      <td style="font-weight: bold;font-size:11px" width="25%">Saldo</td>
      <td style="font-size:11px" width="25%">${o.saldo or ''}</td>
    </tr> 
  </table>
  <p></p>

  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr BGCOLOR="#A4A4A4">
      <td width="100%" style="font-size:14;text-align:center;">DETALLE REAJUSTES</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr BGCOLOR="#A4A4A4">
        <th style="font-size:11px" width="80%">DESCRIPCION</th>        
	<th style="font-size:11px" width="10%">FECHA</th>
        <th style="font-size:11px" width="10%">VALOR</th>
      </tr>
    </thead>
    <%
       ar=totalr=0
       %>
    %for line_r in o.reajuste_ids:
    <%
       ar+=1
       totalr+=line_r.valor
       %>
    <tr style="page-break-inside:avoid">
      <td width="80%" style="font-size:11px;text-align:center">${line_r.name}</td>
      <td width="10%" style="font-size:11px;text-align:center">${line_r.fecha}</td>
      <td width="10%" style="font-size:11px;text-align:right">${'{:,.2f}'.format(line_r.valor)}</td>
    </tr>
    %endfor      
  </table>
  <table width="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr style="page-break-inside:avoid" BGCOLOR="#A4A4A4">
      <td width="5%" style="font-size:11px;text-align:center"> </td>
      <td width="10%" style="font-size:11px;text-align:left"> </td>
      <td width="10%" style="font-size:11px;text-align:right"> </td>
      <td width="65%" style="font-size:11px;text-align:right"><b>Total Reajustes</b></td>
      <td width="10%" style="font-size:11px;text-align:right;border: medium solid black">${'{:,.2f}'.format(totalr)}</td>
    </tr>
  </table>
  
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr BGCOLOR="#A4A4A4">
      <td width="100%" style="font-size:14;text-align:center;">DETALLE PAGOS</td>	  	  
    </tr>	
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr BGCOLOR="#A4A4A4">
        <th style="font-size:11px" width="5%">Nro.</th>        
	<th style="font-size:11px" width="10%">Nro. Comprobante</th>
        <th style="font-size:11px" width="10%">FECHA</th>
        <th style="font-size:11px" width="65%">DETALLE</th>
        <th style="font-size:11px" width="10%">TOTAL</th>
      </tr>
    </thead>
    <%
       a=total=0
       %>
    %for line in o.pago_ids:
    <%
       a+=1
       total+=line.total_banco
       %>
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:11px;text-align:center">${a}</td>
      <td width="10%" style="font-size:11px;text-align:center">${line.name}</td>
      <td width="10%" style="font-size:11px;text-align:center">${line.date}</td>
      <td width="65%" style="font-size:11px;text-align:left">${line.narration}</td>
      <td width="10%" style="font-size:11px;text-align:right">${'{:,.2f}'.format(line.total_banco)}</td>
    </tr>
    %endfor      
  </table>
  <table width="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr style="page-break-inside:avoid" BGCOLOR="#A4A4A4">
      <td width="5%" style="font-size:11px;text-align:center"> </td>
      <td width="10%" style="font-size:11px;text-align:left"> </td>
      <td width="10%" style="font-size:11px;text-align:right"> </td>
      <td width="65%" style="font-size:11px;text-align:right"><b>Total Pagos</b></td>
      <td width="10%" style="font-size:11px;text-align:right;border: medium solid black">${'{:,.2f}'.format(total)}</td>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>__________________</th>
      <th>__________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="50%">ELABORADO POR</th>
      <th width="50%">REVISADO POR</th>
    </tr>  
    <tr style="height:35px">
      <th></th>
      <th></th>
    </tr>
  </table>
  %endfor
</html>
