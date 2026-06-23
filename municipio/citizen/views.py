from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.forms import DniAuthenticationForm
from .models import CategoriaGestion, EstadoGestion, Gestion, AdjuntoGestion


class CitizenLoginView(LoginView):
    template_name = "citizen/login.html"
    authentication_form = DniAuthenticationForm

    def get_success_url(self):
        return "/ciudadano/"


citizen_login = CitizenLoginView.as_view()


@login_required(login_url="citizen_login")
def home(request):
    gestiones = Gestion.objects.filter(ciudadano=request.user)

    reclamos_count = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_RECLAMO).count()
    solicitudes_count = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_SOLICITUD).count()

    return render(request, "citizen/home.html", {
        "reclamos_count": reclamos_count,
        "solicitudes_count": solicitudes_count,
        "turnos_count": 1,
        "notificaciones_count": 3,
    })


@login_required(login_url="citizen_login")
def nueva_gestion(request):
    categorias_destacadas = CategoriaGestion.objects.filter(
        activa=True,
        destacada=True
    ).order_by("orden")[:5]

    if not categorias_destacadas.exists():
        categorias_destacadas = CategoriaGestion.objects.filter(
            activa=True
        ).order_by("-usos", "orden")[:5]

    return render(request, "citizen/nueva_gestion.html", {
        "categorias_destacadas": categorias_destacadas
    })


@login_required(login_url="citizen_login")
def mis_gestiones(request):
    gestiones = Gestion.objects.filter(
        ciudadano=request.user
    ).select_related(
        "categoria",
        "area_responsable",
        "estado"
    ).order_by("-creada")

    return render(request, "citizen/mis_gestiones.html", {
        "gestiones": gestiones
    })


@login_required(login_url="citizen_login")
def mis_reclamos(request):
    gestiones = Gestion.objects.filter(
        ciudadano=request.user,
        categoria__tipo=CategoriaGestion.TIPO_RECLAMO
    ).select_related("categoria", "area_responsable", "estado").order_by("-creada")

    return render(request, "citizen/mis_reclamos.html", {
        "gestiones": gestiones
    })


@login_required(login_url="citizen_login")
def mis_solicitudes(request):
    gestiones = Gestion.objects.filter(
        ciudadano=request.user,
        categoria__tipo=CategoriaGestion.TIPO_SOLICITUD
    ).select_related("categoria", "area_responsable", "estado").order_by("-creada")

    return render(request, "citizen/mis_solicitudes.html", {
        "gestiones": gestiones
    })


@login_required(login_url="citizen_login")
def mis_turnos(request):
    return render(request, "citizen/mis_turnos.html")


@login_required(login_url="citizen_login")
def notificaciones(request):
    return render(request, "citizen/notificaciones.html")



@login_required(login_url="citizen_login")
def estado_servicios(request):
    return render(request, "citizen/estado_servicios.html")


@login_required(login_url="citizen_login")
def mapa_ciudadano(request):
    gestiones = Gestion.objects.filter(
        ciudadano=request.user
    ).select_related(
        "categoria",
        "area_responsable",
        "estado"
    ).order_by("-creada")

    return render(request, "citizen/mapa_ciudadano.html", {
        "gestiones": gestiones
    })


@login_required(login_url="citizen_login")
def buscar_categorias(request):
    q = request.GET.get("q", "").strip()

    categorias = CategoriaGestion.objects.filter(activa=True)

    if q:
        categorias = categorias.filter(nombre__icontains=q) | categorias.filter(
            palabras_clave__icontains=q
        )

    categorias = categorias.select_related("area").order_by(
        "tipo", "area__nombre", "nombre"
    )[:12]

    data = [
        {
            "id": c.id,
            "nombre": c.nombre,
            "tipo": c.get_tipo_display(),
            "tipo_codigo": c.tipo,
            "area": c.area.nombre,
            "url": (
                f"/ciudadano/reclamos/detalle/{c.id}/"
                if c.tipo == CategoriaGestion.TIPO_RECLAMO
                else f"/ciudadano/solicitudes/detalle/{c.id}/"
                if c.tipo == CategoriaGestion.TIPO_SOLICITUD
                else "#"
            ),
        }
        for c in categorias
    ]

    return JsonResponse({"results": data})


@login_required(login_url="citizen_login")
def reclamo_tipo(request):
    categorias = CategoriaGestion.objects.filter(
        activa=True,
        tipo=CategoriaGestion.TIPO_RECLAMO
    ).select_related("area").order_by("area__nombre", "nombre")

    return render(request, "citizen/reclamo_tipo.html", {
        "categorias": categorias
    })


@login_required(login_url="citizen_login")
def reclamos_categorias(request):
    categorias = CategoriaGestion.objects.filter(
        activa=True,
        tipo=CategoriaGestion.TIPO_RECLAMO
    ).select_related("area").order_by("area__nombre", "orden", "nombre")

    return render(request, "citizen/reclamos_categorias.html", {
        "categorias": categorias
    })


@login_required(login_url="citizen_login")
def reclamo_detalle(request, categoria_id):
    categoria = get_object_or_404(
        CategoriaGestion.objects.select_related("area"),
        id=categoria_id,
        tipo=CategoriaGestion.TIPO_RECLAMO
    )

    if request.method == "POST":
        reclamo = request.session.get("reclamo", {})

        reclamo["categoria_id"] = categoria.id
        reclamo["categoria_nombre"] = categoria.nombre
        reclamo["categoria_tipo"] = categoria.get_tipo_display()
        reclamo["area_nombre"] = categoria.area.nombre
        reclamo["descripcion"] = request.POST.get("descripcion", "")
        reclamo["urgencia"] = request.POST.get("urgencia", "")
        reclamo["desde_cuando"] = request.POST.get("desde_cuando", "")
        reclamo["solucionar_antes_de"] = request.POST.get("solucionar_antes_de", "")

        request.session["reclamo"] = reclamo
        request.session.modified = True

        return redirect("citizen_reclamo_ubicacion")

    return render(request, "citizen/reclamo_detalle.html", {
        "categoria": categoria
    })


@login_required(login_url="citizen_login")
def reclamo_ubicacion(request):
    reclamo = request.session.get("reclamo")

    if not reclamo:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        direccion = request.POST.get("direccion", "")
        latitud = request.POST.get("latitud", "")
        longitud = request.POST.get("longitud", "")

        if not direccion and not latitud and not longitud:
            return render(request, "citizen/reclamo_ubicacion.html", {
                "reclamo": reclamo,
                "error": "Indicá una dirección o utilizá tu ubicación actual."
            })

        reclamo["direccion"] = direccion
        reclamo["latitud"] = latitud
        reclamo["longitud"] = longitud
        reclamo["referencia_ubicacion"] = request.POST.get("referencia_ubicacion", "")

        request.session["reclamo"] = reclamo
        request.session.modified = True

        return redirect("citizen_reclamo_evidencia")

    return render(request, "citizen/reclamo_ubicacion.html", {
        "reclamo": reclamo
    })


@login_required(login_url="citizen_login")
def reclamo_evidencia(request):
    reclamo = request.session.get("reclamo")

    if not reclamo:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        adjuntos_guardados = []

        for foto in request.FILES.getlist("fotos"):
            path = default_storage.save(f"temp/reclamos/{foto.name}", foto)
            adjuntos_guardados.append({
                "path": path,
                "url": default_storage.url(path),
                "nombre": foto.name,
                "tipo": AdjuntoGestion.TIPO_IMAGEN,
            })

        documento = request.FILES.get("documento")
        if documento:
            path = default_storage.save(f"temp/reclamos/{documento.name}", documento)
            adjuntos_guardados.append({
                "path": path,
                "url": default_storage.url(path),
                "nombre": documento.name,
                "tipo": AdjuntoGestion.TIPO_DOCUMENTO,
            })

        reclamo["adjuntos"] = adjuntos_guardados
        reclamo["fotos_cargadas"] = len([a for a in adjuntos_guardados if a["tipo"] == AdjuntoGestion.TIPO_IMAGEN])
        reclamo["documentos_cargados"] = len([a for a in adjuntos_guardados if a["tipo"] == AdjuntoGestion.TIPO_DOCUMENTO])

        request.session["reclamo"] = reclamo
        request.session.modified = True

        return redirect("citizen_reclamo_resumen")

    return render(request, "citizen/reclamo_evidencia.html", {
        "reclamo": reclamo
    })


@login_required(login_url="citizen_login")
def reclamo_resumen(request):
    reclamo = request.session.get("reclamo")

    if not reclamo:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        categoria = get_object_or_404(
            CategoriaGestion.objects.select_related("area"),
            id=reclamo["categoria_id"]
        )

        estado, _ = EstadoGestion.objects.get_or_create(
            codigo="registrado",
            defaults={
                "nombre": "Registrado",
                "descripcion_ciudadano": "Tu reclamo fue recibido.",
                "orden": 1,
            }
        )

        gestion = Gestion.objects.create(
            ciudadano=request.user,
            categoria=categoria,
            area_responsable=categoria.area,
            estado=estado,
            descripcion=reclamo.get("descripcion", ""),
            direccion=reclamo.get("direccion", ""),
            latitud=reclamo.get("latitud") or None,
            longitud=reclamo.get("longitud") or None,
        )

        for adjunto in reclamo.get("adjuntos", []):
            AdjuntoGestion.objects.create(
                gestion=gestion,
                archivo=adjunto["path"],
                tipo=adjunto["tipo"],
                nombre_original=adjunto["nombre"],
            )

        categoria.usos += 1
        categoria.save(update_fields=["usos"])

        request.session.pop("reclamo", None)

        return redirect("citizen_reclamo_iniciado", gestion_id=gestion.id)

    return render(request, "citizen/reclamo_resumen.html", {
        "reclamo": reclamo
    })


@login_required(login_url="citizen_login")
def reclamo_iniciado(request, gestion_id):
    gestion = get_object_or_404(
        Gestion.objects.select_related("categoria", "estado", "area_responsable"),
        id=gestion_id,
        ciudadano=request.user
    )

    return render(request, "citizen/reclamo_iniciado.html", {
        "gestion": gestion
    })


@login_required(login_url="citizen_login")
def solicitudes_categorias(request):
    categorias = CategoriaGestion.objects.filter(
        activa=True,
        tipo=CategoriaGestion.TIPO_SOLICITUD
    ).select_related("area").order_by("area__nombre", "orden", "nombre")

    return render(request, "citizen/solicitudes_categorias.html", {
        "categorias": categorias
    })


@login_required(login_url="citizen_login")
def solicitud_detalle(request, categoria_id):
    categoria = get_object_or_404(
        CategoriaGestion.objects.select_related("area"),
        id=categoria_id,
        tipo=CategoriaGestion.TIPO_SOLICITUD
    )

    if request.method == "POST":
        solicitud = request.session.get("solicitud", {})

        solicitud["categoria_id"] = categoria.id
        solicitud["categoria_nombre"] = categoria.nombre
        solicitud["categoria_tipo"] = categoria.get_tipo_display()
        solicitud["area_nombre"] = categoria.area.nombre
        solicitud["descripcion"] = request.POST.get("descripcion", "")
        solicitud["urgencia"] = request.POST.get("urgencia", "")
        solicitud["desde_cuando"] = request.POST.get("desde_cuando", "")
        solicitud["fecha_requerida"] = request.POST.get("fecha_requerida", "")

        request.session["solicitud"] = solicitud
        request.session.modified = True

        return redirect("citizen_solicitud_ubicacion")

    return render(request, "citizen/solicitud_detalle.html", {
        "categoria": categoria
    })


@login_required(login_url="citizen_login")
def solicitud_ubicacion(request):
    solicitud = request.session.get("solicitud")

    if not solicitud:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        solicitud["direccion"] = request.POST.get("direccion", "")
        solicitud["latitud"] = request.POST.get("latitud", "")
        solicitud["longitud"] = request.POST.get("longitud", "")
        solicitud["referencia_ubicacion"] = request.POST.get("referencia_ubicacion", "")

        request.session["solicitud"] = solicitud
        request.session.modified = True

        return redirect("citizen_solicitud_evidencia")

    return render(request, "citizen/solicitud_ubicacion.html", {
        "solicitud": solicitud
    })


@login_required(login_url="citizen_login")
def solicitud_evidencia(request):
    solicitud = request.session.get("solicitud")

    if not solicitud:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        adjuntos_guardados = []

        for foto in request.FILES.getlist("fotos"):
            path = default_storage.save(f"temp/solicitudes/{foto.name}", foto)
            adjuntos_guardados.append({
                "path": path,
                "url": default_storage.url(path),
                "nombre": foto.name,
                "tipo": AdjuntoGestion.TIPO_IMAGEN,
            })

        for documento in request.FILES.getlist("documentos"):
            path = default_storage.save(f"temp/solicitudes/{documento.name}", documento)
            adjuntos_guardados.append({
                "path": path,
                "url": default_storage.url(path),
                "nombre": documento.name,
                "tipo": AdjuntoGestion.TIPO_DOCUMENTO,
            })

        solicitud["adjuntos"] = adjuntos_guardados
        solicitud["fotos_cargadas"] = len([a for a in adjuntos_guardados if a["tipo"] == AdjuntoGestion.TIPO_IMAGEN])
        solicitud["documentos_cargados"] = len([a for a in adjuntos_guardados if a["tipo"] == AdjuntoGestion.TIPO_DOCUMENTO])

        request.session["solicitud"] = solicitud
        request.session.modified = True

        return redirect("citizen_solicitud_resumen")

    return render(request, "citizen/solicitud_evidencia.html", {
        "solicitud": solicitud
    })


@login_required(login_url="citizen_login")
def solicitud_resumen(request):
    solicitud = request.session.get("solicitud")

    if not solicitud:
        return redirect("citizen_nueva_gestion")

    if request.method == "POST":
        categoria = get_object_or_404(
            CategoriaGestion.objects.select_related("area"),
            id=solicitud["categoria_id"]
        )

        estado, _ = EstadoGestion.objects.get_or_create(
            codigo="registrado",
            defaults={
                "nombre": "Registrado",
                "descripcion_ciudadano": "Tu solicitud fue recibida.",
                "orden": 1,
            }
        )

        gestion = Gestion.objects.create(
            ciudadano=request.user,
            categoria=categoria,
            area_responsable=categoria.area,
            estado=estado,
            descripcion=solicitud.get("descripcion", ""),
            direccion=solicitud.get("direccion", ""),
            latitud=solicitud.get("latitud") or None,
            longitud=solicitud.get("longitud") or None,
        )

        for adjunto in solicitud.get("adjuntos", []):
            AdjuntoGestion.objects.create(
                gestion=gestion,
                archivo=adjunto["path"],
                tipo=adjunto["tipo"],
                nombre_original=adjunto["nombre"],
            )

        categoria.usos += 1
        categoria.save(update_fields=["usos"])

        request.session.pop("solicitud", None)

        return redirect("citizen_solicitud_iniciada", gestion_id=gestion.id)

    return render(request, "citizen/solicitud_resumen.html", {
        "solicitud": solicitud
    })


@login_required(login_url="citizen_login")
def solicitud_iniciada(request, gestion_id):
    gestion = get_object_or_404(
        Gestion.objects.select_related("categoria", "estado", "area_responsable"),
        id=gestion_id,
        ciudadano=request.user
    )

    return render(request, "citizen/solicitud_iniciada.html", {
        "gestion": gestion
    })


@login_required(login_url="citizen_login")
def gestion_detalle(request, gestion_id):
    gestion = get_object_or_404(
        Gestion.objects.select_related(
            "categoria",
            "area_responsable",
            "estado",
            "ciudadano",
        ),
        id=gestion_id,
        ciudadano=request.user,
    )

    adjuntos = AdjuntoGestion.objects.filter(gestion=gestion).order_by("id")

    historial_demo = [
        {
            "fecha": gestion.creada,
            "titulo": "Gestión iniciada",
            "descripcion": "La gestión fue recibida correctamente por el Municipio.",
            "estado": "Iniciada",
            "actor": "Ciudadano",
            "adjunto": None,
        },
        {
            "fecha": gestion.creada,
            "titulo": "Evaluación inicial",
            "descripcion": "El área responsable revisará la información enviada.",
            "estado": "En análisis",
            "actor": "Mesa de entrada",
            "adjunto": None,
        },
        {
            "fecha": gestion.creada,
            "titulo": "Pendiente de intervención",
            "descripcion": "La gestión queda disponible para que el operador cargue novedades, visitas, fotos o cambios de estado.",
            "estado": gestion.estado.nombre,
            "actor": "Centro de Operaciones",
            "adjunto": None,
        },
    ]

    return render(request, "citizen/gestion_detalle.html", {
        "gestion": gestion,
        "adjuntos": adjuntos,
        "historial_demo": historial_demo,
    })


@login_required(login_url="citizen_login")
def turno_detalle(request, turno_id):
    turno = {
        "id": turno_id,
        "titulo": "Licencia de conducir",
        "estado": "Confirmado",
        "area": "Tránsito",
        "fecha": "25/06/2026",
        "hora": "09:30",
        "ubicacion": "Palacio Municipal",
    }

    return render(request, "citizen/turno_detalle.html", {
        "turno": turno
    })

@login_required
def obtener_turno(request):
    return render(request, "citizen/obtener_turno.html")

@login_required
def mis_datos_turnero(request):
    return render(request, "citizen/mis_datos_turnero.html")

@login_required
def confirmacion_turno(request):
    return render(request, "citizen/confirmacion_turno.html")


@login_required(login_url="citizen_login")
def mi_perfil(request):
    user = request.user

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile":
            if hasattr(user, "email") and not getattr(user, "email", None):
                user.email = request.POST.get("email", "").strip()

            user.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("citizen_mi_perfil")

    context = {
        "profile": user,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "document_number": user.dni,
        "phone": getattr(user, "phone", "") or getattr(user, "celular", "") or getattr(user, "telefono", ""),
        "birth_date": getattr(user, "birth_date", None),
        "email": user.email,
        "address": getattr(user, "address", "") or getattr(user, "domicilio", ""),
        "city": getattr(user, "city", "") or getattr(user, "localidad", ""),
        "properties": [],
        "family_links": [],
    }

    return render(request, "citizen/mi_perfil.html", context)