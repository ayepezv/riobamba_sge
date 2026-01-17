# Diccionario de Datos - Módulo Financiero

## Prefijo de Tablas: `fi_`

Este módulo gestiona la estructura presupuestaria y la ejecución financiera.

### 1. Fuente de Financiamiento
- **Tabla**: `fi_fuente`
- **Descripción**: Origen de los recursos (ej: Recursos Fiscales, Autogestión).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | AutoField | PK | Identificador interno. |
| codigo | CharField(3) | Unique | Código de la fuente (ej: '001'). |
| nombre | CharField(200) | | Nombre descriptivo. |

### 2. Estructura Programática
- **Tabla**: `fi_estructura_programatica`
- **Descripción**: Unidades administrativas o programas (ej: Gerencia de TICs).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | AutoField | PK | Identificador interno. |
| codigo | CharField(20) | Unique | Código programático (ej: '040303'). |
| nombre | CharField(200) | | Nombre de la unidad/programa. |
| nivel | Integer | Default: 1 | Nivel jerárquico. |

### 3. Clasificador Presupuestario
- **Tabla**: `fi_clasificador`
- **Descripción**: Catálogo de cuentas de ingresos y gastos.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | AutoField | PK | Identificador interno. |
| codigo | CharField(30) | Unique | Partida presupuestaria (ej: '61.01.05'). |
| nombre | CharField(300) | | Nombre de la cuenta. |
| tipo | CharField(3) | Choices | 'ING' (Ingreso) o 'GAS' (Gasto). |
| agrupador | Boolean | Default: False | True si es cuenta padre (no imputable). |

### 4. Presupuesto (Transaccional)
- **Tabla**: `fi_presupuesto`
- **Descripción**: Registro detallado de la asignación y ejecución presupuestaria.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | AutoField | PK | Identificador interno. |
| anio | Integer | Default: 2026 | Año fiscal. |
| partida_concatenada | CharField(100) | Unique | String completo llave (Estructura + Clasificador + Fuente). |
| fuente_id | FK | Nullable | Relación a `fi_fuente`. |
| estructura_id | FK | Nullable | Relación a `fi_estructura_programatica`. |
| clasificador_id | FK | Not Null | Relación a `fi_clasificador`. |
| asignacion_inicial | Decimal(20,2) | Default: 0.00 | Presupuesto inicial aprobado. |
| reformas | Decimal(20,2) | Default: 0.00 | Aumentos o disminuciones aprobadas. |
| codificado | Property | Calculado | `asignacion_inicial + reformas`. |
| devengado | Decimal(20,2) | Default: 0.00 | Valor ya comprometido/ejecutado. |
