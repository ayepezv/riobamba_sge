<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
      <%
      var=0
      %>
      %for lines in o.line_ids:
          <%
          f = time.strptime(lines.fecha_actual1, '%Y-%m-%d')
          cont=0
          cont2=0
          cont3=0 
          %>
          %for i in f:
             %if cont==2: 
                 <% dia=i %>
             %endif
             <% cont+=1 %>
          %endfor
          %for i in f:
             %if cont2==1: 
                 <% mes=i %>
             %endif
             <% cont2+=1 %> 
          %endfor
          %for i in f:
             %if cont3==0: 
                 <% anio=i %>
             %endif
             <% cont3+=1 %>
          %endfor
          %if mes==1:
            <% mes1="Enero" %>
          %elif mes==2:
            <% mes1="Febrero" %>
          %elif mes==3:
            <% mes1="Marzo" %>
          %elif mes==4:
            <% mes1="Abril" %>
          %elif mes==5:
            <% mes1="Mayo" %>
          %elif mes==6:
            <% mes1="Junio" %>
          %elif mes==7:
            <% mes1="Julio" %>
          %elif mes==8:
            <% mes1="Agosto" %>
          %elif mes==9:
            <% mes1="Septiembre" %>
          %elif mes==10:
            <% mes1="Octubre" %>
          %elif mes==11:
            <% mes1="Noviembre" %>
          %else:
            <% mes1="Diciembre" %>
          %endif

          <% fe = str(dia) + " de " + str(mes1) + " del " + str(anio)%>
          %if var==0:
              <h2 style="text-align:center;" align="center">GENERAL PLAZA, ${fe}</h2>
          %endif
          <% var=var+1 %>
      %endfor

   <h2 style="text-align:center;" align="center">BIENES DEL CUSTODIO: </h2>
   <h3 style="text-align:center;" align="center">${user.employee_id.complete_name or ''|entity}</h3>
   %if o.tipo=='Larga Duracion':
   <h4 style="text-align:center;" align="center">ACTIVOS FIJOS</h4>
   %elif o.tipo=='Sujeto a Control':
   <h4 style="text-align:center;" align="center">SUJETOS A CONTROL</h4>
   %else:
   <h4 style="text-align:center;" align="center">LISTADO DE BIENES</h4>
   %endif
  <table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
	 <thead style="display: table-header-group">
	   <tr>
	     <th width="13 style="text-align:left;">C&oacute;digo</th>
	     <th width="34%">Descripci&oacute;n del Activo</th>
             <th width="25%">Otros Componentes</th>
	     <th width="9%">Valor Compra</th>
	     <th width="9%">Valor Actual</th>
             <th width="10%">Condici&oacute;n</th>
	   </tr>
	 </thead>
      <%
      total_actual=total_compra=0
      %>
    %for line in o.line_ids:
      <%
	total_compra+=line.valor_compra
        total_actual+=line.valor_actual
      %>
       <tr style="page-break-inside:avoid">
	 <td width="13 style="font-size:11px;text-align:left">${ line.code }</td>
	 <td width="34%" style="font-size:11px;text-align:left">${ line.name }</td>
         <td width="25%" style="font-size:11px;text-align:left">${ line.otros }</td>
	 <td width="9%" style="font-size:11px;text-align:right">${ line.valor_compra }</td>
	 <td width="9%" style="font-size:11px;text-align:right">${ line.valor_actual }</td>
         <td width="10%" style="font-size:11px;text-align:right">${ line.condicion }</td>
       </tr>
     
    %endfor
 </table>

<table WIDTH="100%" border="1" cellpadding="2" bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
       <tr style="page-break-inside:avoid">
	 <td width="72%" style="font-size:11px;text-align:right"><b>TOTAL</b></td>
	 <td width="9%" style="font-size:11px;text-align:right"><b>${ total_compra }</b></td>
         <td width="9%" style="font-size:11px;text-align:right"><b>${ total_actual }</b></td>
         <td width="10%" style="font-size:11px;text-align:right"><b>${ line.cantidad} Bienes</b></td>
       </tr>
 </table>
<!-- td son columnas,   tr son filas-->


  
  
  %endfor
</html>
