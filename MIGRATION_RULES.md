# REGLAS DE MIGRACIÓN - RIOBAMBA SGE

## 1. Fuente de la Verdad
- Toda lógica de negocio debe basarse en el código encontrado en la carpeta `referencias_legacy/`.
- No inventar reglas de negocio. Si el código legacy valida "Saldo < 0", nosotros también.

## 2. Nomenclatura de Base de Datos (Estricto)
- Tablas Financieras: Prefijo `fi_` (Ej: `fi_partida_presupuestaria`)
- Tablas Administrativas: Prefijo `ad_` (Ej: `ad_proveedores`)
- Tablas Talento Humano: Prefijo `th_`
- Tablas Generales: Prefijo `ge_`
- Idioma: Español.

## 3. Stack Tecnológico
- Backend: Python (FastAPI o el stack que estés usando).
- Base de Datos: PostgreSQL.

## 4. Flujo de Trabajo
1. Analizar archivo legacy correspondiente (ej: `budget.py`).
2. Identificar campos críticos.
3. Crear tabla nueva con prefijos correctos.
4. Implementar endpoint con la misma lógica de validación.