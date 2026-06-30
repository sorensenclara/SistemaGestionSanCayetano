"""
Script de carga de gestiones de prueba — San Cayetano
========================================================
Crea 2 reclamos y 2 solicitudes de ejemplo, asignados al ciudadano demo,
para poder probar dashboards, mapa operativo y cambio de estado.

USO:
    python manage.py shell < seed_gestiones_demo.py

NOTA: Es idempotente respecto al ciudadano + categoría (no duplica si ya
existe una gestión igual para ese ciudadano y categoría).
"""

from accounts.models import User
from citizen.models import Area, CategoriaGestion, EstadoGestion, Gestion

print("\n━━━ Creando gestiones de prueba ━━━\n")

# ── Ciudadano autor ──────────────────────────────────────────────────────────
ciudadano = User.objects.get(dni="99000007")

# ── Estado inicial ───────────────────────────────────────────────────────────
estado_inicial = EstadoGestion.objects.get(codigo="registrado")

# ── Definición de gestiones de prueba ────────────────────────────────────────
GESTIONES_DEMO = [
    {
        "tipo": CategoriaGestion.TIPO_RECLAMO,
        "categoria_nombre": "Poda que afecta cables o viviendas",
        "area_nombre": "Servicios Públicos",
        "descripcion": "Hay una rama grande que está tocando el cableado eléctrico frente a mi casa, es peligroso.",
        "direccion": "Av. San Martín 1234",
    },
    {
        "tipo": CategoriaGestion.TIPO_RECLAMO,
        "categoria_nombre": "Calles con baches o elevaciones",
        "area_nombre": "Obras Públicas",
        "descripcion": "En la esquina de Belgrano y Rivadavia hay un pozo grande que dificulta el paso de autos.",
        "direccion": "Belgrano y Rivadavia",
    },
    {
        "tipo": CategoriaGestion.TIPO_SOLICITUD,
        "categoria_nombre": "Corte de pasto",
        "area_nombre": "Servicios Públicos",
        "descripcion": "Solicito el corte de pasto en el terreno baldío lindero a mi domicilio.",
        "direccion": "Calle Mitre 567",
    },
    {
        "tipo": CategoriaGestion.TIPO_SOLICITUD,
        "categoria_nombre": "Certificado de altura domiciliaria",
        "area_nombre": "Catastro",
        "descripcion": "Necesito el certificado de altura domiciliaria para una gestión bancaria.",
        "direccion": "Calle Sarmiento 890",
    },
]

creadas = 0
existentes = 0

for data in GESTIONES_DEMO:
    area = Area.objects.get(nombre=data["area_nombre"])
    categoria = CategoriaGestion.objects.get(
        nombre=data["categoria_nombre"],
        tipo=data["tipo"],
        area=area,
    )

    gestion, is_new = Gestion.objects.get_or_create(
        ciudadano=ciudadano,
        categoria=categoria,
        defaults={
            "area_responsable": area,
            "estado": estado_inicial,
            "descripcion": data["descripcion"],
            "direccion": data["direccion"],
        },
    )

    status = "✓ Creada" if is_new else "↺ Ya existía"
    print(f"  {status}  [{categoria.get_tipo_display()}] {categoria.nombre} (#{gestion.id})")

    if is_new:
        creadas += 1
    else:
        existentes += 1

print(f"\n  {creadas} creadas · {existentes} ya existían")
print(f"\n  Total gestiones en sistema: {Gestion.objects.count()}")
print()