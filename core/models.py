from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    cedula_ruc = models.CharField(max_length=13, unique=True, verbose_name='Cédula/RUC')
    cargo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cargo')
    unidad_administrativa = models.CharField(max_length=100, blank=True, null=True, verbose_name='Unidad Administrativa')

    def __str__(self):
        return f"{self.username} - {self.cedula_ruc}"
