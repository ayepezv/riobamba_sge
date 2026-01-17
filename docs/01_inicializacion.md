# Hito 1: Inicialización del Proyecto Riobamba SGE

Este documento resume el proceso de inicialización del proyecto, incluyendo el plan original y los resultados obtenidos.

---

## 1. Resumen de Ejecución (Walkthrough)

Se ha inicializado exitosamente el proyecto `riobamba_sge` utilizando Django 5.0. Se estableció una estructura modular robusta con una aplicación core encargada de la autenticación mediante un modelo de usuario personalizado.

### Logros
- **Control de Versiones**: Repositorio Git inicializado con un `.gitignore` completo.
- **Estructura del Proyecto**:
    - `config/`: Configuraciones del proyecto (settings, urls, etc.).
    - `apps/`: Directorio modular para aplicaciones.
    - `apps/core/`: Maneja la gestión de usuarios.
- **Dependencias**: Instaladas en el entorno virtual `.venv`. Librerías clave: `django`, `psycopg2-binary`, `django-environ`, `django-guardian`, `pillow`.
- **Base de Datos**: PostgreSQL configurada y migrada exitosamente.
- **Modelo de Usuario Personalizado**:
    - `CustomUser` implementado con campos adicionales: `cedula`, `cargo`, `departamento`.
- **Superusuario**: Creado programáticamente con campos personalizados.
  - **Username**: `admin`
  - **Email**: `ayepezv@gmail.com`
  - **Cédula**: `9999999999` (Dummy)
  - **Cargo**: Director de Desarrollo
  - **Departamento**: Tecnologías

### Verificación
#### Estado del Servidor
El servidor de desarrollo está en ejecución.
- **URL**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 2. Plan de Implementación Original

### Descripción del Objetivo
Inicializar el proyecto 'riobamba_sge' con una estructura robusta, control de versiones Git y un modelo de usuario personalizado. El proyecto utilizará Django 5.0, PostgreSQL y seguirá una arquitectura modular con un directorio `apps/`.

### Cambios Propuestos

#### Raíz del Proyecto
- **[.gitignore](file:///c:/Proyectos/riobamba_sge/.gitignore)**
    - Archivo de exclusión robusto incluyendo `.env`, `venv/`, `__pycache__/`, `.vscode/`, y otros artefactos de Python/Django.
- **[requirements.txt](file:///c:/Proyectos/riobamba_sge/requirements.txt)**
    - Dependencias: `django>=5.0`, `psycopg2-binary`, `django-environ`, `django-guardian`, `pillow`.

#### Estructura de Directorios y App Core
- **[apps/core/models.py](file:///c:/Proyectos/riobamba_sge/apps/core/models.py)**
    - Modelo `CustomUser` heredando de `AbstractUser`.
    - Campos: `cedula` (único, 10 caracteres), `cargo`, `departamento`.
- **[apps/core/apps.py](file:///c:/Proyectos/riobamba_sge/apps/core/apps.py)**
    - Configuración de la aplicación para `apps.core`.

#### Configuración (Post-Instalación)
Después de instalar Django, se ejecutó `django-admin startproject config .` para generar `manage.py` y el directorio `config`. Luego se modificó:

- **config/settings.py**
    - Estructura:
        - Configurar `BASE_DIR` para soportar la carpeta `apps/`.
        - Configurar `django-environ`.
        - Establecer `AUTH_USER_MODEL = 'core.CustomUser'`.
        - Agregar `apps.core` a `INSTALLED_APPS`.
        - Configuración de base de datos desde `DATABASE_URL`.
