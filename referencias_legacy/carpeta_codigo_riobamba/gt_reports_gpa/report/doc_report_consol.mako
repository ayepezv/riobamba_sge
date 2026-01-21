<html>
  <head>
  </head>
  <style>
caption {
   padding-bottom: 5px;
   text-align:center;
}
th {
   font-weight: bold;
}

.center {
   text-align: center;
}
.tborder {
border-spacing: 3;
border: 1px solid black;
}

  </style>
  <body>
    <table width="100%" class="tborder">
      <caption>
	<strong>REPORTE CONSOLIDADO DE EGRESOS</strong>
      </caption>
      <thead>
	<tr style="border: 1px solid black;">
	  <th>Ejercicio Fiscal</th>
	  <th>Documentos Consolidados</th>
	  <th>Fecha de Consulta</th>
	</tr>
      </thead>
      <tbody>
	<tr>
	  <td class="center">${ data['fiscalyear'] }</td>
	  <td class="center">Convenios, Contratos, Facturas Proveedor</td>
	  <td class="center">${ time.strftime('%Y-%m-%d') }</td>
	</tr>
      </tbody>
    </table>
    <br>
    <table width="100%" style="text-size: 10px;">
      <thead>
	<tr>
	  <th style="border-bottom: 2px solid gray;">Detalle</th>
	  <th style="border-bottom: 2px solid gray;">Fecha</th>
	  <th style="border-bottom: 2px solid gray;">Monto ($)</th>
	</tr>
      </thead>
      <tbody style="font-size: 10px;">
	% for item in process_data(data):
	<tr>
	  <td style="border-bottom: 1px solid gray;">${ item['partner'] }</td>
	  <td colspan="2" style="text-align:right;"><strong>${ formatLang(item['total'], digits=2) }</strong></td>
	</tr>
	% for li in item['docs']:
	<tr>
	  <td style="text-align:right;">${ li['name'] }: ${ li.origin }</td>
	  <td width="30%" style="text-align:center;">${ li.date_due }</td>
	  <td width="20%" style="text-align:right;">${ formatLang(li.residual, digits=2) }</td>
	</tr>
	% endfor

	% endfor
      </tbody>
    </table>
  </body>
</html>
