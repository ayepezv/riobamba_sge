import pdfplumber

path = r"c:\Proyectos\riobamba_sge\docs\Informacion\PAC2026.pdf"

with pdfplumber.open(path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    print(f"Number of chars: {len(page.chars)}")
    print(f"Number of images: {len(page.images)}")
    text_layout = page.extract_text(layout=True)
    print("--- LAYOUT TEXT ---")
    print(text_layout[:2000] if text_layout else "No layout text")
