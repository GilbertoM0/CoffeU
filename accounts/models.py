

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

import datetime
import random
import string


# Manager para Usuario
class GestorUsuarioPersonalizado(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Verificar que no este vacio el email
        if not email:
            raise ValueError('El Correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El Superusuario debe tener el atributo is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El Superusuario debe tener el atributo is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        return user


# Modelo  de Usuario extender AbstractBaseUser
class Usuario(AbstractBaseUser, PermissionsMixin):
    # Constante para administrar los generos
    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('N', 'No Especificado'),
        ('O', 'Otro')
    ]

    # Campos de registro inicial
    email = models.EmailField(unique=True, null=False, blank=False, max_length=255)
    nombre_usuario = models.CharField(max_length=255, null=False, blank=False)
    telefono_celular = models.CharField(max_length=20, null=False, blank=False, unique=True)

    # Campos adicionales
    bio = models.TextField(max_length=255, null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENEROS)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    intereses = models.JSONField(default=list, null=True, blank=True)
    avatar = models.ImageField(upload_to= 'avatars/', null=True, blank=True)


    # Campos de estado de la cuenta
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Campos para la verificación de códigos OTP
    otp_codigo = models.CharField(max_length=6, null=True, blank=True)
    otp_creado_en = models.DateTimeField(null=True, blank=True)

    # Especificar el Manager
    objects = GestorUsuarioPersonalizado()

    # Especificar el campo de USERNAME
    USERNAME_FIELD = 'telefono_celular'
    REQUIRED_FIELDS = ['email', 'nombre_usuario']

    # Codigo para evitar conflictos con el modelo de Django
    groups = models.ManyToManyField('auth.Group',
                                    related_name='usuarios',
                                    blank=True,
                                    help_text=('Para evitar conflictos con el modelo de Django'),
                                    related_query_name='usuario')

    user_permissions = models.ManyToManyField('auth.Permission',
                                              related_name='usuarios',
                                              blank=True,
                                              help_text=('Para evitar conflictos con el modelo de Django'),
                                              related_query_name='usuario'
                                              )

    @staticmethod
    def generar_otp():
        caracteres = string.digits
        # for _ in range(6):
        #     ''.join (random.choice(caracteres))
        return ''.join (random.choice(caracteres) for _ in range(6))

    def es_valido_otp(self, codigo_otp):
        if not codigo_otp:
            return False
        tiempo_expiracion = self.otp_creado_en + datetime.timedelta(minutes=10)

        if self.otp_codigo == codigo_otp and timezone.now() < tiempo_expiracion:
            return True
        return False
