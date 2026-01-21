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
    <h3 colspan="2" style="text-align:center">SOLICITUD DE COMPRA No. ${ o.name }</h3>
    <tr>
      <th style="text-align:left;font-size:14px">Fecha de Emision : ${ formatLang(o.date_start, date=True) }</th>
    </tr>
    <tr>
      <th style="text-align:left;font-size:14px">Solicitado por : ${o.solicitant_id.complete_name}</th>
    </tr>
    <tr>
      <th style="text-align:left;font-size:14px">Unidad Operativa/Departamento : ${o.department_id.name}</th>
    </tr>
    <tr>
      <th style="text-align:left;font-size:14px">Ref. Docmto : ${o.referencia_bodega or ''}</th>
    </tr>
   
  </thead>
  <tbody>
        <table width="100%">
        <thead>
              <tr>
             </tr> 
            <tr style="text-align:left;font-size:9px">
                <th><b></b></th>
            </tr>
      
        </thead>
    </table>

    <table width="100%" style="border:thin solid;">
        <thead>
              <tr>
             </tr> 
            <tr style="text-align:left;font-size:15px">
                <th><b>CERTIFICACION PRESUPUESTARIA</b></th>
            </tr>
      
            <tr style="text-align:left;font-size:11px">
               <th> <b>PARTIDA : </b>${ o.partida_aux or "" }</th>

            </tr>

            <tr style="text-align:left;font-size:11px">
               
               <th> <b>DISPONIBILIDAD PRESUPUESTARIA :</b></th>
            </tr>

            <tr><th> </th> </tr>
	    <tr><th> </th> </tr>
            <tr><th> </th> </tr>
            <tr><th> </th> </tr>
            <tr><th> </th> </tr>
            <tr><th> </th> </tr>
            <tr><th> </th> </tr>
            <tr><th> </th> </tr>

            <tr style="text-align:center;font-size:10px">
               
               <th> ECO. OSWALDO JÁCOME B.</th>
            </tr>

           <tr style="text-align:center;font-size:10px">
               
               
               <td> <b>DIRECTOR FINANCIERO</b></td>
            </tr>

        </thead>
    </table>

    <table width="100%">
      <tr style="text-align:left;font-size:9px">
        
      </tr>
      %if o.asunto:
      <tr style="text-align:left;font-size:9px">
        <b>ASUNTO : </b>${ o.asunto or "" }
      </tr>
      %endif
      <tr>
	<td><b>JUSTIFICATIVO : </b>${ o.justificativo or "" }</td>
      </tr>
      <tr>
	<td><b>OBSERVACIONES/ANTECEDENTES</b> ${ o.description or "" } </td>
      </tr>
    </table>
    <table width="100%" style="border:thin solid;">
      <tr>
        <tr>
          <th width="90%">PRODUCTO</th>
          <th width="10%">CANTIDAD</th>
        </tr>
      </tr>
      %for line in o.line_ids:
      <tbody>
        <tr>
          <td style="text-align:left;font-size:10px">${line.product_id.default_code or '' } - ${line.product_id.name or ''}: ${line.desc or ""}</td>
          <td style="text-align:center;font-size:10px">${line.product_qty }</td>
        </tr>
      </tbody>
      %endfor
    </table>
  </tbody>
  <tfoot>
    <br>
    <br>
    <br>
    <br>
    <table width="100%">
      <tr>
	<th width="50%" style="text-align:center;font-size:12px">ELABORADO</th>
	<th width="50%" style="text-align:center;font-size:12px">AUTORIZADO POR</th>
      </tr>
    </table>
    <br>
    <br>
    <table width="100%">
      <tr>
	<td width="50%" style="text-align:center;font-size:12px">${ o.user_id.employee_id.complete_name }</td>
	%if o.aprueba_aux:
	<td width="50%" style="text-align:center;font-size:12px">${ o.aprueba_aux.complete_name }</td>
	%else:
	<td width="50%" style="text-align:center;font-size:12px">${ o.user_id.context_department_id.coordinador_id.complete_name }</td>
	%endif
      </tr>

    </table>
  </tfoot>
</table>  
%endfor
</body>
</html>
