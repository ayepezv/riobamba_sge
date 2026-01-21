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
<table cellspacing="0" cellpadding="3" WIDTH="120%">
	 <tr>
    <th colspan="2" style="font-size:19px" align="center">CERTIFICACION PRESUPUESTARIA No. ${ o.name }</th>
  </tr>
</table>
<table width="120%" rules="cols" cellspacing="0" cellpadding="5" border="1">  
  <tr>
    <th style="font-size:11px" align="right" width="20%">Fecha de Emisión:</th>
    <td style="font-size:11px" width="80%" align="left">${ formatLang(o.date, date_time=True) }</td>
  </tr>
  <tr>
    <th style="font-size:11px" align="right" width="20%">Unidad Operativa:</th>
    <td style="font-size:11px" width="80%" align="left">${ o.department_id.name }</td>
  </tr>
  <tr>
    <th style="font-size:11px" align="right" width="20%">Emitido por:</th>
    <td style="font-size:11px" width="80%" align="left">${ o.user_id.name }</td>
  </tr>
  <tr>
    <th style="font-size:11px" align="right" width="20%">Observaciones:</th>
    <td style="font-size:11px" with="80%">${ o.notes }</td>
  </tr>
  <tr>
    <th></th>
    <th></th>
  </tr>
  <tr>
    <th></th>
    <th></th>
  </tr>  
</table>
<p></p>
<table border="1" cellpadding="2" cellspacing="0"  width="120%" >
  <thead>    
    <tr>
      <th align="left" style="font-size:9px" width="30%">PROYECTO</th>
      <th align="left" style="font-size:9px" width="26%">PARTIDA PRESUPUESTARIA</th>
      <th align="center" style="font-size:9px" width="12%" style="text-align:right;">MONTO CERTIFICADO</th>
    </tr>
  </thead>
  <% 
     total = 0.0
     total_certificado = 0.0
  %> 
  %for line in o.line_ids:
  <tbody>
    <tr style="font-size:10px">
      <td style="text-align:left;font-size:10px">${line.project_id.name }</td>
      <td style="text-align:center;font-size:10px">${line.budget_id.code } ${ line.budget_id.name }</td>
      <td style="text-align:right;font-size:10px">$ ${ line.amount_certified }</td>
    </tr>
 </tbody>
  %endfor
  <tfoot>
    <tr style="font-size:10px">
      <td></td>
      <td style="text-align:right" colspan="3">TOTAL</td>
      <td align="right">${o.amount_certified}</td>
  </tr>
  </tfoot>
</table>
<br>
<br>
<table width="120%">
  <tr style="font-size:11px">
    <th width="50%">ELABORADO</th>
    <th width="50%">APROBADO</th>
  </tr>  
  <tr style="height:35px">
    <th></th>
    <th></th>
  </tr>    
  <tr style="font-size:11px">
    <td width="50%" align="center">${ o.user_id.employee_id.complete_name }</td>
    <td width="50%" align="center">DIRECTOR FINANCIERO</td>
  </tr>
</table>
%endfor
</body>
</html>
