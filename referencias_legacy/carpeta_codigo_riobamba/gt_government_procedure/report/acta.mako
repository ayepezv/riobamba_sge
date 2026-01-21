<!DOCTYPE HTML>
<html>
<head>
  <style type="text/css">
    .line {
    border-bottom:1pt solid black;
    }
  </style>
</head>
<body>
%for o in objects:
<table width="100%" style="border:thin solid;">
  <thead>
    <h3 colspan="2" style="text-align:center">ACTA DE ENTREGA - RECEPCION</h3>
  </thead>
  <tbody>
  <%import time%>
  <p style="text-align:justify">En el canton de ${user.company_id.city or ''|entity}, Provincia de/del ${user.company_id.state_id.name or ''|entity}, el ${o.date_acta or ''|entity}, comparecen: por una parte el ${user.company_id.partner_id.name or ''|entity} representado por la C.P.A. SHEILA PATIÑO, en calidad de GUARDALMACEN, y por otra parte como proveedor, ${o.partner_id.name or ''|entity} - ${o.partner_id.ced_ruc or ''|entity}, con la finalidad de suscribir la presente ACTA DE ENTEGA - RECEPCION de los siguientes bienes</p>
    <table width="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000">
      <tr>
        <tr>
	  <th width="5%" style="text-align:center;font-size:14px">#</th>
          <th width="55%" style="text-align:center;font-size:14px">PRODUCTO</th>
          <th width="10%" style="text-align:center;font-size:14px">UNIDAD</th>
          <th width="10%" style="text-align:center;font-size:14px">CANTIDAD</th>
          <th width="10%" style="text-align:center;font-size:14px">P.UNITARIO</th>
	  <th width="10%" style="text-align:center;font-size:14px">SUBTOTAL</th>
        </tr>
      </tr>
      <%a=total=0%>
      %for line in o.order_line:
      <%
	 a+=1
	 total += line.price_subtotal_s
	 %>
      <tbody>
        <tr>
	  <td style="text-align:center;font-size:12px">${a}</td>
          <td style="text-align:left;font-size:12px">${line.name or '' }</td>
          <td style="text-align:center;font-size:12px">${ line.product_uom.name or line.uom_desc or ''}</td>
          <td style="text-align:center;font-size:12px">${line.product_qty }</td>
	  <td style="text-align:right;font-size:12px">${line.price_unit }</td>
	  <td style="text-align:right;font-size:12px">${line.price_subtotal_s }</td>
        </tr>
      </tbody>
      %endfor
    </table>
<table WIDTH=1000 style="font-size:14px" >	
  <tr WIDTH=1000 style="page-break-inside:avoid"> <b>		
      <td  width="15%" ></td>
      <td  width="35%" ></b></td>
<td  width="10%" ></td>
<td  width="35%" >Total</td>
<td  width="10%" align="right">${total}</td>
</tr>
</table>
<br>
  <p style="text-align:justify">Se deja constancia que los bienes que se reciben cumplen con las caracteristicas tecnicas especificadas en los pliegos y se recibe en perfectas condiciones</p>
  </tbody>
  <tfoot>
    <br>
    <br>
    <br>
    <br>
    <table width="100%">
      <tr>
	<td width="50%" style="text-align:center;font-size:12px">_______________________________</td>
	<td width="50%" style="text-align:center;font-size:12px">_______________________________</td>
      </tr>
      <tr>
	<td width="50%" style="text-align:center;font-size:12px">C.P.A. SHEILA PATIÑO</td>
	<td width="50%" style="text-align:center;font-size:12px">${ o.partner_id.name }</td>
      </tr>
      <tr>
	<th width="50%" style="text-align:center;font-size:12px">GUARDALMACEN(E)</th>
	<th width="50%" style="text-align:center;font-size:12px">PROVEEDOR</th>
      </tr>
      <tr>
	<th width="50%" style="text-align:center;font-size:12px">Recibi Conforme</th>
	<th width="50%" style="text-align:center;font-size:12px">Entregue Conforme</th>
      </tr>
    </table>
    <br>
    <br>
  </tfoot>
</table>  
%endfor
</body>
</html>
