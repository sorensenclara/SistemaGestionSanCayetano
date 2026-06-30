from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, dni, password=None, **extra_fields):
        if not dni:
            raise ValueError("El DNI es obligatorio")

        user = self.model(dni=dni, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, dni, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.ADMINISTRADOR)

        return self.create_user(dni, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        SECRETARIO    = "SECR", "Secretario"
        FUNCIONARIO   = "FUNC", "Funcionario"
        OPERADOR      = "OPER", "Operador"
        CIUDADANO     = "CIUD", "Ciudadano"

    username = None

    dni = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="DNI",
    )

    role = models.CharField(
        max_length=5,
        choices=Role.choices,
        default=Role.CIUDADANO,
        verbose_name="Rol",
    )

    # Datos de contacto
    phone = models.CharField("Celular", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)

    # Datos complementarios
    birth_date = models.DateField("Fecha de nacimiento", null=True, blank=True)
    address    = models.CharField("Domicilio", max_length=255, blank=True)
    city       = models.CharField("Localidad", max_length=100, blank=True)

    # Foto perfil
    photo = models.ImageField("Foto de perfil", upload_to="profiles/", null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD  = "dni"
    REQUIRED_FIELDS = []

    def __str__(self):
        nombre = f"{self.first_name} {self.last_name}".strip()
        return nombre if nombre else self.dni

    def is_administrador(self):
        return self.role == self.Role.ADMINISTRADOR

    def is_secretario(self):
        return self.role == self.Role.SECRETARIO

    def is_funcionario(self):
        return self.role == self.Role.FUNCIONARIO

    def is_operador(self):
        return self.role == self.Role.OPERADOR

    def is_ciudadano(self):
        return self.role == self.Role.CIUDADANO
