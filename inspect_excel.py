import pandas as pd
import os

path = r"c:\Proyectos\riobamba_sge\docs\Informacion\PAC2026.xlsx"

if not os.path.exists(path):
    print(f"File not found: {path}")
else:
    try:
        df = pd.read_excel(path, dtype=str, header=None, nrows=20)
        print(df.fillna("").to_string())
    except Exception as e:
        print(f"Error reading excel: {e}")
