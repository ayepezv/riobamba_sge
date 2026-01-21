<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  <H2><center>REPORTE DE NOTIFICACIONES</center></H2>
  <p></p>

  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <thead style="display: table-header-group">
      <tr>
	<th style="font-size:9px" width="5%">NUM</th>
        <th style="font-size:9px" width="9%">FECHA</th>
        <th style="font-size:9px" width="8%">CLIENTE</th>
        <th style="font-size:9px" width="20%">ORDENANZA</th>
	<th style="font-size:9px" width="30%">MULTA</th>
	<th style="font-size:9px" width="10%">NOT 1</th>
	<th style="font-size:9px" width="10%">NOT 2</th>
	<th style="font-size:9px" width="10%">NOT 3</th>
	<th style="font-size:9px" width="10%">DIRECCION</th>
	<th style="font-size:9px" width="10%">OBSERVACIONES</th>
      </tr>
    </thead>
	<%
	   a=0
           ntotal = 0 
	   %>
    %for line in objects:
	<%
           n1 = line.notificacion1
	   n2 = line.notificacion2
	   n3 = line.notificacion3
	   a+=1
           ntotal +=1 
           x='X'
           y='X'
           z='X' 		
	   %>

    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:9px;text-align:left">${line.name}</td>
      <td width="9%" style="font-size:9px;text-align:left">${line.fecha}</td>
      <td width="8%" style="font-size:9px;text-align:right">${line.cliente_id.name}</td>
      <td width="20%" style="font-size:9px;text-align:right">${line.ordenanza_id.name}</td>
      <td width="30%" style="font-size:9px;text-align:right">${line.multa_id.name}</td>
%if n1 == True :
      <td width="10%" style="font-size:9px;text-align:right">${x}</td>
%endif
%if n1 == False :
      <td width="10%" style="font-size:9px;text-align:right"></td>
%endif
%if n2 == True :
      <td width="10%" style="font-size:9px;text-align:right">${x}</td>
%endif
%if n2 == False :
      <td width="10%" style="font-size:9px;text-align:right"></td>
%endif
%if n3 == True :
      <td width="10%" style="font-size:9px;text-align:right">${x}</td>
%endif
%if n3 == False :
      <td width="10%" style="font-size:9px;text-align:right"></td>
%endif

      <td width="10%" style="font-size:9px;text-align:right">${line.direccion}</td>
      <td width="10%" style="font-size:9px;text-align:right">${line.observaciones}</td>
	
    </tr>
    %endfor
    <tr style="page-break-inside:avoid">
      <td width="5%" style="font-size:9px;text-align:left"></td>
      <td width="9%" style="font-size:9px;text-align:left"></td>
      <td width="8%" style="font-size:9px;text-align:right"></td>
      <td width="20%" style="font-size:9px;text-align:right"></td>
      <td width="30%" style="font-size:9px;text-align:right"></td>
      <td width="10%" style="font-size:9px;text-align:right"></td>
      <td width="10%" style="font-size:9px;text-align:right"></td>
      <td width="10%" style="font-size:9px;text-align:right"></td>
      <td width="10%" style="font-size:9px;text-align:right"><b>TOTAL</b></td>
      <td width="50%" style="font-size:9px;text-align:right"><b>${ntotal}</b></td>
    </tr>
  </table>

  
  <table style="page-break-inside:avoid" width="100%">
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
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr style="height:35px">
      <th>__________________________</th>
    </tr>
    <tr style="font-size:9px">
      <th width="100%"></th>
    </tr>  
    <tr style="font-size:9px">
      <th width="50%">SUPERVISOR DE COMISARIA</th>
    </tr>  

  </table>
</html>
