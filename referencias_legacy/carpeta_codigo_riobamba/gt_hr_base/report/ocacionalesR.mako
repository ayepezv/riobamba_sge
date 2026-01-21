<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
  %for o in objects:
  <H2><center>CONTRATO DE SERVICIOS OCACIONALES</center></H2>
  <table WIDTH="100%">
    <tr style="height:35px">
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr>
      <td width="50%" style="font-size:22;text-align:left;"><b>CONTRATO Nro. :</b></td>	  	  
      <td width="50%" style="font-size:22;text-align:left;"><b>${o.name or ''|entity}</b></td>	  	  
    </tr>	
    <tr>
      <td width="50%" style="font-size:22;text-align:left;"><b>CONTRATO DE :</b></td>	  	  
      <td width="50%" style="font-size:22;text-align:left;"><b>Servicios Ocacionales</b></td>	  	  
    </tr>	
    <tr>
      <td width="50%" style="font-size:22;text-align:left;"><b>NOMBRES :</b></td>	  	  
      <td width="50%" style="font-size:22;text-align:left;"><b>${o.employee_id.employee_first_name or ''|entity}</b></td>	  	  
    </tr>	
    <tr>
      <td width="50%" style="font-size:22;text-align:left;"><b>APELLIDOS :</b></td>	  	  
      <td width="50%" style="font-size:22;text-align:left;"><b>${o.employee_id.employee_first_lastname or ''|entity}</b></td>	  	  
    </tr>	
    <tr>
      <td width="50%" style="font-size:22;text-align:left;"><b>Nro. DE CEDULA :</b></td>	  	  
      <td width="50%" style="font-size:22;text-align:left;"><b>${o.employee_id.name or ''|entity}</b></td>	  	  
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
      <td WIDTH=1000 >Comparecen a la celebración de este contrato, por una parte el Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba, legalmente representado por el ingeniero Napoleón Cadena Oleas, en calidad de Alcalde del Cantón Riobamba y por otra parte el/la  señor/a ${o.employee_id.complete_name}, portador (a) de la cédula de ciudadanía No. ${o.employee_id.name}, quienes convienen en celebrar el presente contrato al tenor de las siguientes cláusulas::
<P>
<b>PRIMERO: ANTECEDENTES.-</b> 
El Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba, requiere contratar los servicios  del señor/a ${o.employee_id.complete_name} en calidad de ${o.employee_id.job_id.name}.

1.1 Mediante informe No. 2016-0001-DGTH, de fecha  04 de enero de 2016, la Dirección de Gestión de Talento Humano  remite  a la Alcaldía el informe previo a la contratación de personal para el año 2016, conforme al requerimiento de personal justificado con los proyectos presentados por los servidores ordenadores de gasto, y se obtenga la correspondiente autorización del señor Alcalde, requisito indispensable para iniciar el proceso de contratación.  

1.2 En hoja de vida del señor/a {{o.employee_id.complete_name}}, consta la respectiva sumilla de autorización del Ingeniero Napoleón Cadena, Alcalde de Riobamba, razón por la cual la Dirección de Gestión de Talento Humano, inicia este proceso de contratación, en calidad de {{o.employee_id.job_id.name}}.

1.3  Mediante Memorando Nro.  GADMR-GTH-2016-……-M, suscrito por el Director de Gestión de Talento Humano, solicita a la Dirección de Gestión Financiera, que certifique partida presupuestaria y disponibilidad de fondos, requisito indispensable para elaborar los respectivos contratos de trabajo.

1.4 La Dirección de Gestión Financiera, certifica las partidas presupuestarias de Servicios Personales por Contrato en sus diferentes funciones, programas y proyectos, para suscribir los respectivos contratos de trabajo.
<P>
<b>SEGUNDA: OBJETO.-</b>
Por medio del presente contrato el señor/a ${o.employee_id.complete_name} se compromete a prestar sus servicios lícitos y personales en calidad de: ${o.employee_id.job_id.name} este contrato se lo efectúa sobre la base de lo dispuesto en el Art. 58 de la Ley Orgánica del Servicio Público, publicada en el Segundo Suplemento del Registro Oficial No. 294 de fecha 06 de Octubre del 2010 y Art. 143 de su Reglamento publicado en el Registro Oficial No. 418 de fecha 01 de abril del 2011, debiendo cumplir con las siguientes funciones o actividades:
<OL>
%for actividad in get_actividades(o):
<LI>${ actividad }
%endfor
</OL>
Y demás análogas que sean asignadas por la administración municipal de acuerdo a la naturaleza del trabajo y por necesidad de servicio

Actividades las cuales desempeñará con honestidad, eficiencia y sujetándose en todo momento a las normas legales vigentes y cuidando siempre los intereses institucionales.
<P>
<b>TERCERA: PARTIDA PRESUPUESTARIA Y DISPONIBILIDAD DE FONDOS.-</b>
La Dirección  Financiera  informa que la disponibilidad económica y la partida presupuestaria que será utilizada para el presente contrato es la No. ${o.budget_ind}, PROYECTO: ${o.program_id.name}; debidamente financiado con ………………..

<P>
<BR>
<b>CUARTA: REMUNERACIÓN.-</b>
La remuneración  mensual unificada que recibirá el señor/a ${o.employee_id.complete_name}, por concepto de este contrato es la cantidad de ($ ${o.wage}) ………….. DÓLARES AMERICANOS CON 00/100 previo a la presentación del informe de actividades mensuales, avaladas por su Jefe inmediato. 
<P>
<b>QUINTA: PLAZO.-</b>
El presente contrato rige desde el ${o.date_start} al ${o.date_end} y su vigencia estará sujeta a la existencia de recursos económicos.
<P>
<b>SEXTA:.-</b>
el señor/a ${o.employee_id.complete_name} laborará en el Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba, realizando las tareas especificadas en la cláusula segunda del presente contrato, en una jornada de ocho horas diarias efectivas, de  lunes a viernes de 8h00 am a 12h30 y de 14h30 a 18h00 o en el  horario que estableciere posteriormente la Institución contratante.
<P>
<b>SÉPTIMA: EXCEPCIONES.-</b>
el/la contratado/a no ingresará a la carrera del servicio público mientras dure su contrato de servicios ocasionales, modalidad de contratación que no le otorga estabilidad ni permanencia en la institución. No se le concederá licencia sin remuneración y comisión de servicios con remuneración para efectuar estudios regulares de postgrado determinadas en los artículos 28 letra b); y 30 inciso final de la Ley Orgánica del Servicio Público. Tampoco podrá prestar sus servicios en otra institución del sector público mediante comisiones de servicio con o sin remuneración conforme lo establecen los artículos 30 y 31 de la mencionada Ley.
No se le otorgará permiso para estudios regulares según lo determinado en el inciso primero del artículo 33 de la citada norma.
<P>
<BR><BR>
<b>OCTAVA: TERMINACIÓN DEL CONTRATO.-</b>
Acorde a lo determinado en el artículo 58, inciso sexto de la Ley Orgánica del Servicio Público y el Art. 146 del Reglamento de la LOSEP, el contrato podrá darse por terminado en cualquier momento. 

El contrato así mismo podrá concluir por las siguientes causas:

a) Cumplimiento del plazo; 
b) Mutuo acuerdo de las partes; 
c) Renuncia voluntaria presentada; 
d) Incapacidad absoluta y permanente de la o el contratado para prestar  servicios; 
e) Pérdida de los derechos de ciudadanía declarada judicialmente en  providencia ejecutoriada; 
f) Por terminación unilateral del contrato por parte de la autoridad  nominadora, sin que fuere necesario otro requisito previo; 
g) Por obtener una calificación regular o insuficiente establecida  mediante el proceso de la evaluación del desempeño;
h) Destitución; 
i) Muerte.
j) Por incumplimiento del Objeto del contrato.
<P>
<b>NOVENA: SEGURO SOCIAL.-</b>
Conforme con lo que dispone la Ley de Seguro Social Obligatorio, el Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba afiliará al contratado/a la sección correspondiente.
<P>
<b>DÉCIMA: SUBROGACIÓN O ENCARGO.-</b>
Según lo contemplado en el Párrafo Sexto del Art 143 del Reglamento a la Ley Orgánica del Servicio Público el personal contratado podrá subrogar o encargarse de un puesto de aquellos comprendidos dentro de la escala del nivel jerárquico superior o de la escala nacional de remuneraciones mensuales unificadas de los servidores públicos, para lo cual deberá cumplir con los requisitos y perfiles para el puesto a subrogar o encargarse. La UATH en el informe previo a la contratación deberá incorporar dicha posibilidad, la cual constará de manera expresa como cláusula en el contrato a suscribirse.
<P>
<b>DECIMA PRIMERA: DECLARACIÓN.-</b>
el/la contratado/a, declara que no se encuentra incursa en inhabilidad ni prohibición establecida por la Ley para suscribir este contrato, declara expresamente que no presta servicios en ninguna otra Institución del Estado, a ningún título y que no ha sido compensada, ni indemnizada  por renuncia voluntaria o supresión de puestos en el Sector Público, además que no tiene ningún parentesco con la Máxima Autoridad o su Delegado.
<P>
<b>DÉCIMA SEGUNDA: CONFIDENCIALIDAD.-</b>
el/la contratado/a se obliga a mantener la más estricta confidencialidad relacionada a las actividades y funciones que desempeña en la prestación de sus servicios para la institución, así mismo, se obliga a no utilizar directa o indirectamente, difundir o revelar información que perjudique al Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba;  El contravenir esta disposición dará lugar a la terminación de la relación laboral, previo al derecho a la defensa conforme a la ley, sin perjuicio de las acciones civiles o penales que le asiste a la institución, por lo que deberá mantener la confidencialidad aún después de terminada la relación laboral.
<P>
<b>DÉCIMA TERCERA: .-</b>
Para los efectos legales del presente contrato el señor/a ${o.employee_id.complete_name}, señala como domicilio ${o.employee_id.address} Telef: ${o.employee_id.house_phone} y el Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba, las calles 5 de junio y Veloz, en el despacho del señor Alcalde.
<P>
<b>DÉCIMA CUARTA: JURISDICCIÓN Y COMPETENCIA.-</b>
El Gobierno Autónomo Descentralizado Municipal del Cantón Riobamba y el/ la contratado/a, en caso de controversias derivadas de la aplicación de los términos establecidos en el presente contrato, se someterán a los jueces competentes de la ciudad de Riobamba renunciando fuero y domicilio.
<P>
<b>DÉCIMA QUINTA:.-</b>
El presente contrato deberá registrarse en la Unidad de Administración de Talento Humano o Departamento de Recursos Humanos para los efectos de Ley, de conformidad a lo estipulado en el artículo 18 de la Ley Orgánica de Servicio Público. 
<P>
Para constancia y aceptación de todo lo estipulado en el presente contrato los comparecientes enterados de todas y cada una de las cláusulas que anteceden, se afirman y ratifican en todo su contenido y firman de buena fe en original, en la ciudad de Riobamba  él: 
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
	</tr>
	<tr style="height:35px">
	  <th>_____________________________</th>
	  <th>_____________________________</th>
	</tr>
	<tr style="font-size:20px">
	  <th width="50%">Ing. Napoleón Cadena </th>
	  <th width="50%">${o.employee_id.complete_name or ''}</th>
	</tr>  
	<tr style="font-size:20px">
	  <th width="50%">ALCALDE DE RIOBAMBA</th>
	  <th width="50%">CC. Nro. ${o.employee_id.name or ''}</th>
	</tr>  
  </table>
<p>
<b>RAZÓN:</b> El presente contrato ha sido elaborado en la Dirección de Talento Humano por el Ab. Diego Castillo, Abogado de Talento Humano y revisado por  el Ab. Jorge Luis Zambrano, Director de Gestión de Talento Humano, de acuerdo a los oficios e informes constantes en el mismo. 
</p>
  <table style="page-break-inside:avoid" width="100%">
    </tr>
	<tr style="height:35px">
	  <th></th>
	  <th></th>
	</tr>
	<tr style="height:35px">
	  <th>_____________________________</th>
	  <th>_____________________________</th>
	</tr>
	<tr style="font-size:20px">
	  <th width="50%">Ab. Diego Castillo E.</th>
	  <th width="50%">ABOGADO DE TALENTO HUMANO</th>
	</tr>  
	<tr style="font-size:20px">
	  <th width="50%">Ab. Jorge Luis Zambrano  S.</th>
	  <th width="50%">DIRECTOR DE TALENTO HUMANO</th>
	</tr>  
  </table>
  %endfor
</html>
