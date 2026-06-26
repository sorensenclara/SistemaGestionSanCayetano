"""
Script de usuarios de demostración — San Cayetano Sistema de Gestión
=====================================================================
Crea usuarios ficticios para cada rol del sistema, útiles para demos
con el cliente y para probar los distintos dashboards.

USO:
    python manage.py shell < create_demo_users.py
    — o —
    python manage.py runscript create_demo_users  (si usás django-extensions)

CREDENCIALES GENERADAS:
    Rol             DNI         Contraseña
    ─────────────────────────────────────────
    Administrador   99000001    demo1234
    Secretario*     99000002    demo1234
    Funcionario     99000003    demo1234
    Funcionario     99000004    demo1234
    Operador        99000005    demo1234
    Operador        99000006    demo1234
    Ciudadano       99000007    demo1234

    * Secretario usa role=FUNC hasta que se cree Role.SECRETARIO en el modelo.

NOTA: Este script es idempotente — si un usuario ya existe, lo actualiza.
"""

from accounts.models import User

DEMO_USERS = [
    {
        "dni":        "99000001",
        "password":   "demo1234",
        "first_name": "Admin",
        "last_name":  "Demo",
        "email":      "admin@sancayetano.demo",
        "role":       User.Role.ADMINISTRADOR,
        "is_staff":   True,
    },
    {
        "dni":        "99000002",
        "password":   "demo1234",
        "first_name": "Secretario",
        "last_name":  "Demo",
        "email":      "secretario@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,  # hasta que exista Role.SECRETARIO
        "is_staff":   False,
    },
    {
        "dni":        "99000003",
        "password":   "demo1234",
        "first_name": "Funcionario",
        "last_name":  "Servicios Públicos",
        "email":      "func.servicios@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
    },
    {
        "dni":        "99000004",
        "password":   "demo1234",
        "first_name": "Funcionario",
        "last_name":  "Obras Públicas",
        "email":      "func.obras@sancayetano.demo",
        "role":       User.Role.FUNCIONARIO,
        "is_staff":   False,
    },
    {
        "dni":        "99000005",
        "password":   "demo1234",
        "first_name": "Operador",
        "last_name":  "García",
        "email":      "operador.garcia@sancayetano.demo",
        "role":       User.Role.OPERADOR,
        "is_staff":   False,
    },
    {
        "dni":        "99000006",
        "password":   "demo1234",
        "first_name": "Inspector",
        "last_name":  "López",
        "email":      "inspector.lopez@sancayetano.demo",
        "role":       User.Role.OPERADOR,
        "is_staff":   False,
    },
    {
        "dni":        "99000007",
        "password":   "demo1234",
        "first_name": "Ciudadano",
        "last_name":  "Demo",
        "email":      "ciudadano@sancayetano.demo",
        "role":       User.Role.CIUDADANO,
        "is_staff":   False,
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

    status = "✓ Creado  " if is_new else "↺ Actualizado"
    print(f"  {status}  DNI: {dni}  |  {user.get_full_name() or dni}  |  {user.role}")

    if is_new:
        created += 1
    else:
        updated += 1

print(f"\n  {created} creados · {updated} actualizados")
print("\n━━━ Credenciales para demo ━━━")
print("  DNI        Contraseña   Rol")
print("  ─────────────────────────────────────────")
print("  99000001   demo1234     Administrador")
print("  99000002   demo1234     Secretario (dashboard funcionario)")
print("  99000003   demo1234     Funcionario — Servicios Públicos")
print("  99000004   demo1234     Funcionario — Obras Públicas")
print("  99000005   demo1234     Operador")
print("  99000006   demo1234     Inspector")
print("  99000007   demo1234     Ciudadano (App Ciudadana)")
print()
