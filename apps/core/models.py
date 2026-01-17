from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    cedula = models.CharField(max_length=10, unique=True, verbose_name='Cédula')
    cargo = models.CharField(max_length=100, verbose_name='Cargo', blank=True, null=True)
    departamento = models.CharField(max_length=100, verbose_name='Departamento', blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'cedula']

    def __str__(self):
        return f"{self.username} - {self.cedula}"
