<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    %if o.rf=='ingreso':
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">REFORMAS PRESUPUESTARIAS DE: INGRESOS</td>	  	  
    </tr>	
    %else:
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">REFORMAS PRESUPUESTARIAS DE: EGRESOS</td>	  	  
    </tr>
    %endif
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">DESDE: ${o.date_start or ''}</td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:14;text-align:center;">HASTA:${o.date or ''}</td>	  	  
    </tr>	
  </table>
    <%
       inicialt=reformt=totalt=0
       %>
  %for program_id in all_programas(o):
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:7px">
    <tr>
      <h5 style="font-weight: bold;font-size:14px" width="8%">PROGRAMA : ${program_id.sequence or ''} - ${program_id.name or ''}</h5>
    </tr> 
  </table>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:7px">
    <thead style="display: table-header-group" BGCOLOR="#D8D8D8">
      <tr>
        <th style="font-size:8px" width="25%">PARTIDA</th>
        <th style="font-size:8px" width="45%">DESCRIPCION</th>
        <th style="font-size:8px" width="10%">ASIGNACION INICIAL</th>
        <th style="font-size:8px" width="10%">REFORMA</th>
        <th style="font-size:8px" width="10%">TOTAL</th>
      </tr>
    </thead>
    <%
       a=inicial=reform=total=0
       %>
    %for line in generate_dict(o,program_id):
    <%
       a+=1
       inicial += line.inicial
       reform += line.reform
       total += line.total
       inicialt += line.inicial
       reformt += line.reform
       totalt += line.total
       %>
    <tr style="border: 1px solid black;page-break-inside:avoid">
      <td width="25%" style="font-size:8px;text-align:lef">${line.budget_id.code}</td>
      <td width="45%" style="font-size:8px;text-align:left">${line.post_id.name}</td>
      <td width="10%" style="font-size:8px;text-align:right">${line.inicial}</td>
      <td width="10%" style="font-size:8px;text-align:right">${line.reform}</td>
      <td width="10%" style="font-size:8px;text-align:right">${line.total}</td>
    </tr>
    %endfor      
  </table>
  <table WIDTH="100%" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:7px">
    <tr>
      <td style="font-weight: bold;font-size:9px" width="25%">SUBTOTAL</td>
      <td style="font-weight: bold;font-size:9px" width="45%">${a}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${inicial}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${reform}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${total}</td>
    </tr> 
  </table>
    %endfor
  <table WIDTH="100%" cellpadding="2" cellspacing="0" style="border-collapse:collapse;font-size:7px">
    <tr>
      <td style="font-weight: bold;font-size:9px" width="25%">TOTAL</td>
      <td style="font-weight: bold;font-size:9px" width="45%">${a}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${inicialt}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${reformt}</td>
      <td style="font-weight: bold;font-size:9px;text-align:right" width="10%">${totalt}</td>
    </tr> 
  </table>
  %endfor
</html>
