from django.contrib import admin
from .models import Area, CategoriaGestion, EstadoGestion, Gestion


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre",)


@admin.register(CategoriaGestion)
class CategoriaGestionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "area", "activa", "destacada", "usos", "orden")
    list_filter = ("tipo", "area", "activa", "destacada")
    search_fields = ("nombre", "descripcion", "palabras_clave")
    list_editable = ("activa", "destacada", "orden")


@admin.register(EstadoGestion)
class EstadoGestionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "activo", "orden")
    list_filter = ("activo",)
    search_fields = ("nombre", "codigo", "descripcion_ciudadano")
    list_editable = ("activo", "orden")


@admin.register(Gestion)
class GestionAdmin(admin.ModelAdmin):
    list_display = ("id", "ciudadano", "categoria", "area_responsable", "estado", "creada")
    list_filter = ("categoria__tipo", "area_responsable", "estado")
    search_fields = ("descripcion", "direccion", "ciudadano__username")
    readonly_fields = ("creada", "actualizada")