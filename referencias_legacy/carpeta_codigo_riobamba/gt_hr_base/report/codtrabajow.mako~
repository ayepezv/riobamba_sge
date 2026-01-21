<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <table WIDTH="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr>
      <td width="100%" style="font-size:22;text-align:center;"><b>${o.name or ''|entity}</b></td>	  	  
    </tr>	
    <tr>
      <td width="100%" style="font-size:22;text-align:center;"><b>CONTRATO INDIVIDUAL DE TRABAJO A PLAZO FIJO</b></td>	  	  
    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </table>
  <table WIDTH=1000 style="font-size:20px;text-align: justify;">
    <tr WIDTH=1000>
      <td WIDTH=1000 >En la ciudad de ${user.company_id.city or ''|entity}, cabecera cantonal del mismo nombre, provincia de/del ${user.company_id.state_id.name or ''|entity}, el ${o.date_start or ''|entity} , se suscribe el presente contrato individual de trabajo a plazo indefinido el mismo que se estipula al tenor de las siguientes cláusulas:
<P>
<b>PRIMERA: COMPARECIENTES.-</b> 
Comparecen a la celebración del presente contrato, por una parte el <b>${user.company_id.name or ''|entity}</b>, representado legalmente por sus personeros: Ingeniero Marcos Alberto Chica Cárdenas; y, Abogado Felipe Dau Ochoa, en sus calidades de ALCALDE Y PROCURADOR SÍNDICO MUNICIPAL, respectivamente en su orden, a quien para efecto y resultado del presente instrumento se lo denominará como <b>“EL CONTRATANTE”</b> o <b>“EL EMPLEADOR”</b>; y por otra parte comparece el señor <b>${o.employee_id.complete_name}</b>, portador de la cédula de ciudadanía Nº. <b>${o.employee_id.name}</b>, por sus propios derechos,  sin nombramiento en la Administración Pública, ni prestando servicios en ella capaz ante la Ley, a quien en adelante para los mismos efectos se llamará como <b>“EL CONTRATADO”</b>. Los comparecientes son mayores de edad, hábiles para obligarse, contratar y ejercer esta clase de actos, con capacidad civil amplia y suficiente cual en derecho se requiere.
<P>
<b>SEGUNDA: ANTECEDENTES.-</b>
El ${user.company_id.name} para el cumplimiento de sus actividades y desarrollo de las tareas propias de su actividad; y, del análisis realizado por la Unidad de Administración del Talento Humano al desempeño de las funciones del personal que se encuentra laborando en esta municipalidad, se infiere la necesidad indispensable de contratar a un ${o.job_id.name}. ${o.employee_id.complete_name} declara tener los conocimientos y capacidades necesarios para el desempeño del cargo indicado, por lo que en base a las consideraciones anteriores y por lo expresado en los numerales siguientes, el EMPLEADOR y el TRABAJADOR proceden a celebrar el presente contrato individual de trabajo a plazo fijo.
<P>
<b>TERCERA: OBJETO DEL CONTRATO.-</b>
${o.employee_id.complete_name} se compromete con el empleador a prestar sus servicios lícitos y personales en la clase de trabajo que le ha determinado la Unidad de Administración del Talento Humano en calidad de ${o.employee_id.job_id.name}, para lo cual declara tener los conocimientos y capacidades necesarias, sus acciones serán supervisadas por el (Jefe Administrativo); y, cumplirá con las determinaciones descritas en el Art.80 referida en la Ordenanza de Clasificación y Valoración de Puestos, Reglamento Orgánico Funcional, Organigrama Estructural y Manual de Funciones, publicada en el Edición Especial del Registro Oficial Nº.99 de martes 10 de Febrero del 2009 y su reforma.
<P>
<BR>
<b>CUARTA: OBLIGACIONES DEL EMPLEADOR Y TRABAJADOR.-</b>
En lo que respecta a las obligaciones, derechos y prohibiciones del empleador y trabajador, estos se sujetan estrictamente a lo dispuesto en el Código del Trabajo en su Capítulo IV del Título I de las obligaciones del empleador y trabajador, a más de las estipuladas en este contrato, se consideran como faltas graves del trabajador, y por tanto suficientes para dar por terminada la relación laboral.

El trabajador se compromete para con el Municipio, a cumplir las cláusulas contenidas en este contrato, así como las disposiciones que para efecto determine la Jefatura de la Unidad de Administración del Talento Humano; además se obliga durante la vigencia del contrato a no adquirir ninguna nueva obligación que limite el cumplimiento de sus obligaciones para con el Municipio y observar confidencialidad sobre la información que le corresponda conocer durante la ejecución del contrato, así como luego de fenecido el plazo del mismo.
<P>
<b>QUINTA: LUGAR DE PRESTACIÓN DE SERVICIOS.-</b>
El lugar principal de trabajo del contratado se establece en la Biblioteca Municipal en Palacio Municipal.</b>
<P>
<b>SEXTA: HORARIO DE TRABAJO.-</b>
El horario establecido será como jornada especial de ocho horas diarias observando el principio de continuidad, equidad y optimización del servicio, para lo cual se determinarán horarios de trabajos rotativos; además el trabajador asistirá a los actos solemnes, culturales, deportivos, sociales que realiza el Municipio.
<P>
<b>SÉPTIMA: REMUNERACIÓN Y FORMA DE PAGO.-</b>
El ${user.company_id.name or ''|entity} se compromete pagar a el/la CONTRATADA previa presentación de informes mensuales aprobados por el Jefe de Área, el valor de (${o.wage}), como remuneración mensual unificada, con cargo a la partida presupuestaria Nº. ${o.budget_id.code} denominada ${o.budget_id.name}.
<P>
<b>OCTAVA: PLAZO DE CONTRATO.-</b>
El presente contrato estará vigente a partir del ${o.date_start} hasta el ${o.date_end}.
<P>
<b>NOVENA: DOMICILIO Y NOTIFICACIONES.-</b>
Las partes de mutuo acuerdo señalan los siguientes domicilios para futuras notificaciones en las siguientes direcciones:

${user.company_id.name or ''|entity}: ${user.company_id.street or ''|entity}
Dirección del Trabajador: ${o.employee_id.address}
<P>
<b>DÉCIMA: TERMINACIÓN DEL CONTRATO.-</b>
El Contrato terminará por las siguientes causales:
<OL type =A>
<LI>Cumplimiento del plazo;
<LI>Mutuo acuerdo de la partes;
<LI>Renuncia voluntaria presentada;
<LI>Incapacidad absoluta y permanente de la contratada para prestar servicios;
<LI>Pérdida de los derechos de ciudadanía declarada judicialmente en providencia ejecutoriada;
<LI>Por terminación unilateral del contrato por parte de la autoridad nominadora, sin que fuere necesario otro requisito previo;
<LI>Por obtener una calificación regular o insuficiente establecida mediante el proceso de la evaluación del desempeño;
<LI>Destitución; y,
<LI>Muerte.
</OL>
<P>
<b>DÉCIMA PRIMERA: NATURALEZA.-</b>
Este tipo de contratos por su naturaleza, de ninguna manera representará estabilidad laboral en el mismo, ni derecho adquirido para la emisión de un nombramiento permanente, pudiendo darse por terminación unilateral por parte de la autoridad nominadora, sin que fuere necesario otro requisito previo.
<P>
<b>DÉCIMA SEGUNDA: LEGISLACIÓN APLICABLE.-</b>
En todo lo no previsto en este Contrato, cuyas modalidades especiales las reconocen y aceptan las partes, éstas se sujetan al Código del Trabajo.
<P>
<b>DÉCIMA TERCERA: JURISDICCIÓN Y COMPETENCIA.-</b>
En caso de suscitarse discrepancias en la interpretación, cumplimiento y ejecución del presente contrato y cuando fuere posible llegar a un acuerdo amistoso éntrelas partes, estas se someterán a los jueces competentes del lugar en que este contrato ha sido celebrado, así como a los procedimientos laborales determinados por la Ley.

Para constancia de su aceptación, las partes suscriben el presente contrato en original y copia de igual tenor y efecto legal.

    </tr>
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  <table style="page-break-inside:avoid" width="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </table>
  </table>
  <table style="page-break-inside:avoid" width="100%">
    </tr>
	<tr style="height:35px">
	  <th></th>
	  <th></th>
	  <th></th>
	</tr>
	<tr style="height:35px">
	  <th>_____________________________</th>
	  <th>_____________________________</th>
	  <th>_____________________________</th>
	</tr>
	<tr style="font-size:20px">
	  <th width="33%">ING. Marcos Chica Cardenas</th>
	  <th width="33%">${o.employee_id.complete_name or ''}</th>
	  <th width="33%">Ab. Felipe Dau Ochoa</th>
	</tr>  
	<tr style="font-size:20px">
	  <th width="33%">ALCALDE</th>
	  <th width="33%">CC. Nro. ${o.employee_id.name or ''}</th>
	  <th width="33%">PROCURADOR SINDICO</th>
	</tr>  
  </table>
<p>
C.C:  Alcaldía,
Unidad de Talento Humano,
Dirección Financiera,
Asesoría Jurídica
</p>
  %endfor
</html>
