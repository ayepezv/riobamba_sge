import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import AuditLog

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if not hasattr(request, 'start_time'):
            return response

        # 1. Calculate Duration
        duration = time.time() - request.start_time
        
        # 2. Filter exclusions (static files, favicon, admin js requests usually ignored)
        path = request.path
        if any(prefix in path for prefix in ['/static/', '/media/', '/favicon.ico', 'jsi18n']):
            return response
            
        # 3. Determine Action
        method = request.method
        action = 'VIEW'
        if method == 'POST':
            if 'login' in path: action = 'LOGIN'
            elif 'logout' in path: action = 'LOGOUT'
            else: action = 'UPDATE' # Default POST is update/create
            
        # Refine action if necessary (e.g. check status code)
        if response.status_code >= 400:
            # Maybe log error? For now we treat as View/Attempt
            pass

        # 4. Capture User
        user = request.user if request.user.is_authenticated else None

        # 5. Capture IP
        ip = self.get_client_ip(request)

        # 6. Save Log
        # Note: Saving full body/changes is complex in middleware for generic cases.
        # We start with basic tracking.
        try:
            # Avoid logging OPTIONS or HEAD
            if method not in ['OPTIONS', 'HEAD']:
                AuditLog.objects.create(
                    usuario=user,
                    accion=action,
                    ruta=path,
                    metodo=method,
                    ip_address=ip,
                    duracion=round(duration, 4)
                )
        except Exception as e:
            # Fail silently to not impact user experience
            print(f"Audit Log Error: {e}")

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
