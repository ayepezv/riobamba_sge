from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
email = 'ayepezv@gmail.com'
password = 'andres1979'
cedula = '9999999999' # Cédula temporal, actualizar si es necesario

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        cedula=cedula,
        cargo='Director de Desarrollo',
        departamento='Tecnologías'
    )
    print(f"Superusuario '{username}' creado exitosamente.")
else:
    print(f"El usuario '{username}' ya existe.")
