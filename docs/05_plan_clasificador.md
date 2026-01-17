# Plan de UI: Tooltips del Clasificador Presupuestario

El modelo `ClasificadorPresupuestario` ahora incluye el campo `descripcion`, que contiene la definición legal extraída del PDF oficial.

## Objetivo
Mostrar esta definición legal como una ayuda contextual (tooltip) en las interfaces de creación de presupuestos y consultas.

## Implementación Futura

1.  **Backend (API)**:
    *   En los endpoints que sirven listas de clasificadores (Select2 / Autocomplete), incluir el campo `descripcion` en la respuesta JSON.

2.  **Frontend (HTML/JS)**:
    *   **Icono de Ayuda**: Junto al nombre del clasificador en el dropdown o tabla, agregar un ícono `(i)` o `?`.
    *   **Tooltip**: Al pasar el mouse (hover) sobre el ícono o el nombre, renderizar el contenido de `descripcion`.
    *   **Librería Sugerida**: Usar los Tooltips de **Flowbite** (ya integrado) o `tippy.js` para textos largos.

## Ejemplo de UX
> Al seleccionar la partida "51.01.05", el usuario ve un tooltip: *"Gastos para el pago de la remuneración mensual unificada..."*
