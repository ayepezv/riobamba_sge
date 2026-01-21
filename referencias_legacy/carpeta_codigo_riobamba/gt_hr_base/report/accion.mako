<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <tr>
      <td width="33%" style="font-size:14;text-align:center;">ACCION DE PERSONAL</td>
      <td width="33%" style="font-size:14;text-align:center;">Nro. ${o.name or  ''}</td>
      <td width="33%" style="font-size:14;text-align:center;">Fecha. ${o.date or  ''}</td>
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">APELLIDOS</td>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">NOMBRES</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">${o.contract_id.employee_id.employee_first_lastname or ''}</td>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">${o.contract_id.employee_id.employee_first_name or ''}</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">CEDULA</td>
      <td style="font-weight: bold;font-size:11px;text-align:center;" width="50%">RIGE A PARTIR DE:</td>
    </tr>
    <tr>
      <td style="font-size:11px;text-align:center;" width="50%">${o.contract_id.employee_id.name or ''}</td>
      <td style="font-size:11px;text-align:center;" width="50%">${o.date_from or ''}</td>
    </tr>
  </table>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">Tipo:</td>
      <td style="font-size:11px" width="42%">${o.tipo or ''}</td>
    </tr>
  </table>
  <p></p>
  <table WIDTH="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000" >
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">ANTECEDENTES: ${o.desc or ''}</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px" width="12%">EXPLICACION: ${o.desc1 or ''}</td>
    </tr>
  </table>
  <p></p>
  <table WIDTH="100%" border="1" cellpadding="2" cellspacing="0"  bordercolor="#000000" style="border-collapse:collapse;font-size:12px">
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">SITUACION ACTUAL</td><td style="font-size:11px" width="12%"></td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">SITUACION PROPUESTA</td><td style="font-size:11px" width="12%"></td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Direccion</td><td style="font-size:11px" width="12%">${o.direccion_id.name or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Direccion</td><td style="font-size:11px" width="12%">${o.direccion_id2.name or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento</td><td style="font-size:11px" width="12%">${o.department_id.name or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Departamento</td><td style="font-size:11px" width="12%">${o.department_id2.name or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Cargo</td><td style="font-size:11px" width="12%">${o.cargo_id.name or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Cargo</td><td style="font-size:11px" width="12%">${o.cargo_id2.name or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Grupo ocupacional</td><td style="font-size:11px" width="12%">${o.nivel_id.name or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Grupo ocupacional</td><td style="font-size:11px" width="12%">${o.nivel_id2.name or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
          <td style="font-weight: bold;font-size:11px" width="12%">Nivel</td><td style="font-size:11px" width="12%">${o.nivel_contrato_id.name or ''}</td>
      %endif
      %if not o.si_nueva:
          <td style="font-weight: bold;font-size:11px" width="12%">Nivel</td><td style="font-size:11px" width="12%">${o.nivel_contrato_id2.name or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Lugar de trabajo</td><td style="font-size:11px" width="12%">${o.lugar or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Lugar de trabajo</td><td style="font-size:11px" width="12%">${o.lugar2 or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Remuneracion Unificada</td><td style="font-size:11px" width="12%">${o.rmu or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Remuneracion Unificada</td><td style="font-size:11px" width="12%">${o.rmu2 or ''}</td>
      %endif
    <tr>
    <tr>
      %if not o.si_actual:
      <td style="font-weight: bold;font-size:11px" width="12%">Partida Presupuestaria</td><td style="font-size:11px" width="12%">${o.budget_id or ''}</td>
      %endif
      %if not o.si_nueva:
      <td style="font-weight: bold;font-size:11px" width="12%">Partida Presupuestaria</td><td style="font-size:11px" width="12%">${o.budget_id2 or ''}</td>
      %endif
    <tr>
  </table>
  <table style="page-break-inside:avoid" width="100%" border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <br>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">f)....................................</th>
    </tr>
    %if o.tipo=='Vacaciones':
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR O JEFE DEPARTAMENTAL</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    %else:
    %if o.alcalde_e:
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">${o.alcalde_e.complete_name or ''}</th>
    </tr>
    <tr style="font-size:11px">
      %if o.subrog_alcalde:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION ADMINISTRATIVA (E)(S)</th>
      %else:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION ADMINISTRATIVA (E)</th>
      %endif
    </tr>
    %else:
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">Mgs. Marco Marcelo Tapia Arias</th>
    </tr>
    <tr style="font-size:11px">
      %if o.subrog_alcalde:
       <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION ADMINISTRATIVA(S)</th>
      %else:
       <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION ADMINISTRATIVA</th>
      %endif
    </tr>
    %endif
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    %endif
  </table>
  <table style="page-break-inside:avoid" width="100%"  border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
    <br>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:left;">GESTION DE TALENTO HUMANO</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr style="font-size:11px"  border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">f)....................................</th>
    </tr>
    %if o.talento_e:
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">${o.talento_e.complete_name}</th>
    </tr>
    <tr style="font-size:11px">
      %if o.subrog_talento:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION DE TALENTO HUMANO Y DESARROLLO INSTITUCIONAL(E)(S)</th>
      %else:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION DE TALENTO HUMANO Y DESARROLLO INSTITUCIONAL (E)</th>
      %endif
    </tr>
    %else:
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">Abg. María Fernanda Moreno Villacís</th>
    </tr>
    <tr style="font-size:11px">
      %if o.subrog_talento:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTOR DE GESTION DE TALENTO HUMANO Y DESARROLLO INSTITUCIONAL(S)</th>
      %else:
        <th width="100%" style="font-weight: bold;font-size:11px;text-align:center;">DIRECTORA DE GESTION DE TALENTO HUMANO Y DESARROLLO INSTITUCIONAL</th>
      %endif
    </tr>
    %endif
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%"  border='1' rules="cols" cellpadding="2" cellspacing="2"  bordercolor="#000000">
<br>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px;text-align:left;">Registrado</td>
    </tr>
    <tr>
      <td style="font-weight: bold;font-size:11px;text-align:left;">Nro:  ${o.name or  ''}    Fecha: ${o.date or  ''} 

	  Interesado f) ______________________</td>
    </tr>   
	<tr>
      <td style="font-weight: bold;font-size:11px;text-align:left;">
	  <p style="height:10px;"></p>
	  Elaborado y Revisado: f) ______________________ </td>
	<tr>
	  <td style="font-weight: bold;font-size:11px;text-align:left;" ></td>
	  
	  
	  </tr>
	  
    </tr>
    <tr style="font-size:11px">
      <th width="100%" style="font-weight: bold;font-color='white';font-size:11px;text-align:left;">.</th>
    </tr>
  </table>
  %endfor
</html>
