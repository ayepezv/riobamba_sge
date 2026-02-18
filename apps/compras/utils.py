from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from .models import InformeNecesidad

def generar_pdf_necesidad(informe_id):
    """
    Genera el PDF del Informe de Necesidad usando xhtml2pdf.
    """
    informe = get_object_or_404(InformeNecesidad, pk=informe_id)
    
    template_path = 'compras/pdf_informe_necesidad.html'
    context = {'informe': informe}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Informe_Necesidad_{informe.numero_informe}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Tuvimos algunos errores <pre>' + html + '</pre>')
        
    return response
