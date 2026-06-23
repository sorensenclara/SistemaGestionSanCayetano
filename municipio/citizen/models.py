from django.conf import settings
from django.db import models


class Area(models.Model):
    nombre = models.CharField(max_length=120)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class CategoriaGestion(models.Model):
    TIPO_RECLAMO = "RECLAMO"
    TIPO_SOLICITUD = "SOLICITUD"
    TIPO_TRAMITE = "TRAMITE"

    TIPO_CHOICES = [
        (TIPO_RECLAMO, "Reclamo"),
        (TIPO_SOLICITUD, "Solicitud"),
        (TIPO_TRAMITE, "Trámite"),
    ]

    nombre = models.CharField(max_length=160)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="categorias")
    descripcion = models.TextField(blank=True)
    palabras_clave = models.TextField(
        blank=True,
        help_text="Separar palabras clave con comas. Ej: poda, árbol, ramas, cables"
    )
    activa = models.BooleanField(default=True)
    destacada = models.BooleanField(
        default=False,
        verbose_name="Mostrar en accesos rápidos"
    )

    usos = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de usos"
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Categoría de gestión"
        verbose_name_plural = "Categorías de gestión"
        ordering = ["tipo", "area__nombre", "orden", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()} / {self.area})"


class EstadoGestion(models.Model):
    nombre = models.CharField(max_length=80)
    codigo = models.SlugField(unique=True)
    descripcion_ciudadano = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Estado de gestión"
        verbose_name_plural = "Estados de gestión"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Gestion(models.Model):
    ciudadano = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gestiones_ciudadanas"
    )
    categoria = models.ForeignKey(CategoriaGestion, on_delete=models.PROTECT)
    area_responsable = models.ForeignKey(Area, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoGestion, on_delete=models.PROTECT)

    descripcion = models.TextField()
    direccion = models.CharField(max_length=200, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gestión ciudadana"
        verbose_name_plural = "Gestiones ciudadanas"
        ordering = ["-creada"]

    def __str__(self):
        return f"#{self.id} - {self.categoria.nombre}"
    

class AdjuntoGestion(models.Model):
    TIPO_IMAGEN = "imagen"
    TIPO_DOCUMENTO = "documento"

    TIPO_CHOICES = [
        (TIPO_IMAGEN, "Imagen"),
        (TIPO_DOCUMENTO, "Documento"),
    ]

    gestion = models.ForeignKey(
        Gestion,
        on_delete=models.CASCADE,
        related_name="adjuntos"
    )

    archivo = models.FileField(
        upload_to="gestiones/adjuntos/"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )

    nombre_original = models.CharField(
        max_length=255,
        blank=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Adjunto"
        verbose_name_plural = "Adjuntos"

    def __str__(self):
        return self.nombre_original or self.archivo.name