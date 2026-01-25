---
trigger: always_on
---

REGLAS DEL PROYECTO RIOBAMBA SGE:

Modelos y Base de Datos: Todos los modelos del módulo financiero DEBEN usar el prefijo fi_ en la propiedad db_table. Usa siempre help_text en los campos para guiar al usuario.

Diseño Frontend: Usa estrictamente Tailwind CSS y componentes de Flowbite. Prohibido usar Bootstrap.

Código Legacy: Antes de crear una lógica de negocio (ej. Certificaciones), DEBES consultar el archivo MEGA_CODIGO_LEGACY.txt para replicar el comportamiento original de OpenERP.

Idioma: Responde siempre en español, con un tono profesional apto para el sector público de Ecuador.

¡Guarda ese Workflow y úsalo de aquí en adelante para todos los chats!
# REGLAS DEL PROYECTO RIOBAMBA SGE

## Arquitectura Modular (13+ Módulos)
El sistema se divide estrictamente en los siguientes módulos funcionales ubicados en `apps/`. Respetar esta estructura para cualquier nueva funcionalidad.

1.  **apps/planificacion**: Planificación Institucional (PAC, POA, Estructura Orgánica: Direcciones, Unidades, Procesos).
2.  **apps/compras**: Compras Públicas.
3.  **apps/presupuestos**: Partidas Presupuestarias y Reformas.
4.  **apps/financiero**: Gestión Financiera (Certificaciones).
5.  **apps/tesoreria**: Tesorería y Pagos.
6.  **apps/contabilidad**: Contabilidad.
7.  **apps/talento_humano**: Talento Humano.
8.  **apps/inventario**: Gestión de Inventario.
9.  **apps/activos**: Activos Fijos.
10. **apps/proyectos**: Gestión de Proyectos.
11. **apps/permisos**: Permisos y Trámites.
12. **apps/agua_potable**: Agua Potable - Comercial.
13. **apps/juridico**: Gestión Jurídica.
14. **apps/auditoria**: Auditoría Interna.
15. **apps/servicios**: Servicios Generales.

## Frontend y UI
- **Framework**: Django Jazzmin con tema "Cerulean" (Celeste/Blanco).
- **Iconografía**: Usar FontAwesome (`fas fa-*`) para todos los módulos.
- **CSS**: Tailwind CSS y Flowbite para vistas personalizadas. Prohibido Bootstrap.

## Base de Datos
- Modelos del módulo financiero: Prefijo `fi_` en `db_table`.
- Otros módulos: Usar prefijos cortos consistentes (e.g., `pl_` para planificación).

## Código Legacy
- Consultar `MEGA_CODIGO_LEGACY.txt` antes de implementar lógica de negocio crítica.

## Auditoría y Trazabilidad (Regla Global)
- **Trazabilidad Obligatoria**: Todas las acciones de los usuarios (Creación, Edición, Eliminación, Vistas Clave) deben quedar registradas.
- **Medición de Tiempo**: Se debe registrar el tiempo de procesamiento/operación para análisis de eficiencia.
- **Implementación**: Todo el sistema debe pasar por el Middleware de Auditoría (`apps.auditoria.middleware.AuditMiddleware`).

## Documentación y Preservación de Conocimiento
- **Walkthroughs**: Cada vez que se generen mejoras significativas o se creen nuevos módulos, se debe generar un archivo `walkthrough.md` explicativo y guardarlo en `docs/walkthroughs/[YYYY-MM-DD]_[nombre_descriptivo].md`. Esto asegura que las decisiones técnicas y explicaciones queden en el repositorio.
