"""
Script de usuarios de demostración — San Cayetano Sistema de Gestión
=====================================================================
Crea usuarios ficticios para cada rol del sistema, con asignación real
de área para Funcionarios, Operadores y Secretario, útiles para probar
el flujo completo: ciudadano carga reclamo → funcionario del área lo ve
→ asigna tarea a operador del área → operador la ejecuta.

USO:
    python manage.py shell < create_demo_users.py

REQUISITO: correr antes seed_citizen_data (para tener las Áreas creadas).

NOTA: Este script es idempotente — si un usuario ya existe, lo actualiza.
"""

from accounts.models import User
from citizen.models import Area

print("\n━━━ Creando usuarios de demostración ━━━\n")

# ── Áreas (deben existir ya por seed_citizen_data) ──────────────────────────
try:
    area_servicios = Area.objects.get(nombre="Servicios Públicos")
    area_obras     = Area.objects.get(nombre="Obras Públicas")
    area_vial      = Area.objects.get(nombre="Dirección Vial")
    area_catastro  = Area.objects.get(nombre="Catastro")
except Area.DoesNotExist:
    print("  ⚠️  Faltan áreas. Corré primero: python manage.py seed_citizen_data")
    raise SystemExit(1)

DEMO_USERS = [
    # ── Administrador ────────────────────────────────────────────────────
    {
        "dni":        "99000001",
        "password":   "demo1234",
        "first_name": "Admin",
        "last_name":  "Demo",
        "email":      "admin@sancayetano.demo",
        "role":       User.Role.ADMINISTRADOR,
        "is_staff":   True,
        "area":       None,
    },
    # ── Secretario ───────────────────────────────────────────────────────
    {
        "dni":        "99000002",
        "password":   "demo1234",
        "first_name": "Secretario",
        "last_name":  "Demo",
        "email":      "secretario@sancayetano.demo",
        "role":       User.Role.SECRETARIO,
        "is_staff":   False,
        "area":       None,  # supervisa todas las áreas, sin una propia
    },
    # ── Funcionarios por área ────────────────────────────────────────────
    {
        "dni":        "99000003",
        "password":   "demo1234",
        "first_name": "Juan",
        "last_name":  "Pérez",
        "email":      "func.servicios@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
        "area":       area_servicios,
    },
    {
        "dni":        "99000004",
        "password":   "demo1234",
        "first_name": "María",
        "last_name":  "Gómez",
        "email":      "func.obras@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
        "area":       area_obras,
    },
    {
        "dni":        "99000008",
        "password":   "demo1234",
        "first_name": "Carlos",
        "last_name":  "Ruiz",
        "email":      "func.vial@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
        "area":       area_vial,
    },
    {
        "dni":        "99000009",
        "password":   "demo1234",
        "first_name": "Laura",
        "last_name":  "Fernández",
        "email":      "func.catastro@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
        "area":       area_catastro,
    },
    # ── Operadores por área ──────────────────────────────────────────────
    {
        "dni":        "99000005",
        "password":   "demo1234",
        "first_name": "Operador",
        "last_name":  "García",
        "email":      "operador.garcia@sancayetano.demo",
        "role":       User.Role.OPERADOR,
        "is_staff":   False,
        "area":       area_servicios,
    },
    {
        "dni":        "99000006",
        "password":   "demo1234",
        "first_name": "Inspector",
        "last_name":  "López",
        "email":      "inspector.lopez@sancayetano.demo",
        "role":       User.Role.OPERADOR,
        "is_staff":   False,
        "area":       area_obras,
    },
    {
        "dni":        "99000010",
        "password":   "demo1234",
        "first_name": "Roberto",
        "last_name":  "Sosa",
        "email":      "operador.sosa@sancayetano.demo",
        "role":       User.Role.OPERADOR,
        "is_staff":   False,
        "area":       area_vial,
    },
    # ── Ciudadano ────────────────────────────────────────────────────────
    {
        "dni":        "99000007",
        "password":   "demo1234",
        "first_name": "Ciudadano",
        "last_name":  "Demo",
        "email":      "ciudadano@sancayetano.demo",
        "role":       User.Role.CIUDADANO,
        "is_staff":   False,
        "area":       None,
    },
]

print("\n━━━ Creando usuarios de demostración ━━━\n")

created = 0
updated = 0

for data in DEMO_USERS:
    password = data.pop("password")
    dni = data["dni"]

    user, is_new = User.objects.update_or_create(
        dni=dni,
        defaults=data,
    )
    user.set_password(password)
    user.save()

    area_label = f" | Área: {user.area}" if user.area else ""
    status = "✓ Creado  " if is_new else "↺ Actualizado"
    print(f"  {status}  DNI: {dni}  |  {user.get_full_name() or dni}  |  {user.get_role_display()}{area_label}")

    if is_new:
        created += 1
    else:
        updated += 1

print(f"\n  {created} creados · {updated} actualizados")
print("\n━━━ Credenciales para demo ━━━")
print("  DNI        Contraseña   Rol                          Área")
print("  ───────────────────────────────────────────────────────────────────────")
print("  99000001   demo1234     Administrador                —")
print("  99000002   demo1234     Secretario                   — (supervisa todas)")
print("  99000003   demo1234     Funcionario (Juan Pérez)      Servicios Públicos")
print("  99000004   demo1234     Funcionario (María Gómez)     Obras Públicas")
print("  99000008   demo1234     Funcionario (Carlos Ruiz)     Dirección Vial")
print("  99000009   demo1234     Funcionario (Laura Fernández) Catastro")
print("  99000005   demo1234     Operador (García)             Servicios Públicos")
print("  99000006   demo1234     Operador (López)              Obras Públicas")
print("  99000010   demo1234     Operador (Sosa)               Dirección Vial")
print("  99000007   demo1234     Ciudadano                     —")
print()
