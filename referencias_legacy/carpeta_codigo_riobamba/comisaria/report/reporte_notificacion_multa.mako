<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
	<%
           n1 = o.notificacion1		
	   %>
<!-- td son columnas,   tr son filas-->
<table width="100%" >
    <tr>
      <td style="font-size:17px" width="12%">PARA: Sr. Luis Peñaranda G.</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:17px" width="12%">
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;COMISARIO MUNICIPAL</td>
    </tr>
     <tr>
      <td style="font-weight: bold;font-size:14px" width="12%"></td>
    </tr>  
<!-- pasamos de o.fecha_actual que es el campo fecha actual a f1 que es un campo string y luego mandamos a una funcion get_mes-->
             <%
               sex=o.cliente_id.sexo
               tipo=get_genero(sex)
               sex1=o.empleado_id.gender
               tipo1=get_genero_emp(sex1)
               sex2=o.empleado_id2.gender
               tipo2=get_genero_emp(sex2)
               sex3=o.empleado_id3.gender
               tipo3=get_genero_emp(sex3)
               f = time.strptime(o.fecha_actual, '%Y-%m-%d')
               fe=get_mes(f)
               f1 = time.strptime(o.fecha, '%Y-%m-%d')
               fe1=get_mes(f1)
               f2 = time.strptime(o.fecha2, '%Y-%m-%d')
               fe2=get_mes(f2)
               f3 = time.strptime(o.fecha3, '%Y-%m-%d')
               fe3=get_mes(f3)

             %>
    <tr>
      <td style="font-size:17px" width="12%">FECHA: General Leonidas Plaza Gutierrez, ${ fe} </td>
    </tr>
 
</table>
  <table WIDTH="100%">
     <tr>
      <td style="font-weight: bold;font-size:10px" width="12%">&nbsp</td>
    </tr>
	<tr>
	  <td width="100%" style="font-weight: bold;font-size:20;text-align:center;">INFORME DE NOTIFICACIONES </td>	  	  
    </tr>	
  </table>
  
  <p style="font-size:17;text-align:justify">
   El presente tiene la finalidad de informar a usted señor Comisario que por reiteradas 
   ocasiones se ha echo conocer ${tipo} ${o.cliente_id.name or ''}, 
   con cédula de identidad Nro. ${o.cliente_id.cedula or ''}, residente de la parroquia General Plaza, 
   ubicado en la ${o.cliente_id.direccion or ''}, y, que pese a haberse socializado la 
   ${o.ordenanza_id.name or ''} en su ${o.multa_id.name or ''}
   <br>
   A pesar de haberse socializado en forma verbal al antes citado señor, haciendo caso omiso ha infringido la antes
   citada ordenanza municipal, razón por la que se le ha notificado en forma escrita conforme describo a continuación:
   <br>
   <b>Primera Notificación</b>, otorgada por ${tipo1} policia municipal ${o.empleado_id.complete_name or ''}, con fecha ${fe1}.
   <br>
   <b>Segunda Notificación</b>, otorgada por ${tipo2} policia municipal ${o.empleado_id2.complete_name or ''}, con fecha ${fe2}.
   <br>                
   <b>Tercera Notificación</b>, otorgada por ${tipo3} policia municipal ${o.empleado_id3.complete_name or ''}, con fecha ${fe3}.
   <br>
   Con éstos antecedentes procedo a informar a usted señor Comisario para que de ser el caso proceda conforme dictamine
   la Ordenanza Municipal, citada en líneas anteriores en lo relativo a Multas y Sanciones.
   <br><br>
   Es todo cuanto informo a usted para fines legales pertinentes.


   </p>
  
  
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:15px">
      <th></th>
    </tr>

    <tr style="height:35px">
      <th>__________________________</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%"></th>
    </tr>  
    <tr style="font-size:17px">
      <th width="50%">${o.empleado_id3.complete_name}</th>
    </tr>  
    <tr style="font-weight: bold;font-size:20px">
      <th width="50%">POLICIA MUNICIPAL</th>
    </tr> 

  </table>
  %endfor
</html>
