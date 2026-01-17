# Implementation Plan - Frontend Integration (Tailwind + Flowbite)

## Goal Description
Integrate Tailwind CSS and Flowbite via CDN to create a modern UI. Create the template structure (`base.html`, `home.html`, `login.html`), implement the `home` view protected by login, and configure URLs.

## User Review Required
> [!NOTE]
> **CDN Usage**: Using CDN for Tailwind and Flowbite as requested for rapid development. For production, a build process (npm/webpack) is recommended later.

## Proposed Changes

### Configuration
#### [MODIFY] config/settings.py
- Configure `TEMPLATES['DIRS']` to include `BASE_DIR / 'templates'`.
- Set `LOGIN_REDIRECT_URL = 'home'` and `LOGOUT_REDIRECT_URL = 'login'`.

### Templates
#### [NEW] templates/base.html
- HTML5 structure.
- Tailwind CSS CDN & Flowbite CDN.
- Layout:
    - Sidebar (Collapsible).
    - Header (Logo + User info).
    - Content block.

#### [NEW] templates/home.html
- Extends `base.html`.
- Dashboard content: "Usuarios Activos", "Módulos Disponibles" cards.

#### [NEW] templates/registration/login.html
- Extends `base.html` (or standalone with same styles).
- Modern centered login form.

### Apps/Core
#### [MODIFY] apps/core/views.py
- Add `home` view with `@login_required` decorator.

### URLs
#### [MODIFY] config/urls.py
- Add path for `home` view at root `/`.
- Ensure `django.contrib.auth.urls` is included (although `admin` handles some, we need standard auth views).

## Verification Plan

### Manual Verification
- **Login Page**: Navigate to `http://127.0.0.1:8000/`. Should redirect to login. Verify modern UI.
- **Login Flow**: Log in with `admin`.
- **Dashboard**: Verify redirect to `/` showing the Dashboard with Sidebar and Cards.
- **Responsive**: Check Sidebar behavior on smaller screens (Flowbite handles this).
