def generar_redaccion_ia(objeto_contratacion):
    """
    Simula la respuesta de una IA para redactar antecedentes.
    En el futuro, esto conectará con la API de Gemini.
    """
    
    prompt_simulado = f"Redactar antecedentes para: {objeto_contratacion}"
    
    texto_sugerido = f"""
    ANTECEDENTES (Sugerdio por IA):
    
    El Art. 16 de la Constitución de la República del Ecuador establece que el Estado garantizará el derecho al acceso a bienes y servicios públicos de calidad.
    
    Considerando la necesidad institucional de "{objeto_contratacion}", se requiere iniciar el proceso de contratación para cumplir con los objetivos operativos y estratégicos de la Empresa Pública Municipal.
    
    Este servicio/bien permitirá mejorar la eficiencia en la gestión y asegurar la continuidad de los servicios brindados a la ciudadanía de Riobamba.
    """
    
    return texto_sugerido.strip()
