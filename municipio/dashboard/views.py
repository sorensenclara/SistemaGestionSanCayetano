from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django import forms
import datetime

from tasks.models import Task
from citizen.models import Gestion, CategoriaGestion, AdjuntoGestion, EstadoGestion


@login_required
def dashboard_home(request):
    user = request.user

    # Ciudadanos no tienen acceso al Centro de Operaciones
    if user.role == user.Role.CIUDADANO:
        return redirect('citizen_home')

    start_date_str = request.GET.get("start_date")
    end_date_str   = request.GET.get("end_date")
    area           = request.GET.get("area")
    tipo           = request.GET.get("tipo")

    # ── Base querysets ──────────────────────────────────────────────────────
    gestiones = Gestion.objects.select_related(
        "ciudadano", "categoria", "area_responsable", "estado",
    ).all()

    tasks = Task.objects.all()

    # ── Filtros por ROL ─────────────────────────────────────────────────────
    # Operador: solo ve sus tareas asignadas, y las gestiones de su área
    if user.role == user.Role.OPERADOR:
        tasks = tasks.filter(assigned_to=user)
        if user.area:
            gestiones = gestiones.filter(area_responsable=user.area)

    # Funcionario: solo ve gestiones y tareas de su área
    elif user.role == user.Role.FUNCIONARIO:
        if user.area:
            gestiones = gestiones.filter(area_responsable=user.area)
            tasks     = tasks.filter(assigned_to__area=user.area)

    # Secretario: ve todo (supervisa todas las áreas)
    # Administrador: ve todo
    # → ambos no necesitan filtro adicional aquí

    # ── Filtros desde la UI (GET params) ────────────────────────────────────
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            gestiones  = gestiones.filter(creada__date__gte=start_date)
            tasks      = tasks.filter(created_at__date__gte=start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date  = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            gestiones = gestiones.filter(creada__date__lte=end_date)
            tasks     = tasks.filter(created_at__date__lte=end_date)
        except ValueError:
            pass

    if area:
        gestiones = gestiones.filter(area_responsable_id=area)

    if tipo:
        gestiones = gestiones.filter(categoria__tipo=tipo)

    # ── Subsets por tipo ────────────────────────────────────────────────────
    reclamos   = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_RECLAMO)
    solicitudes = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_SOLICITUD)

    def count_estado(codigo):
        return gestiones.filter(estado__codigo=codigo).count()

    today = timezone.now().date()

    # ── Stats ───────────────────────────────────────────────────────────────
    stats = {
        "total": gestiones.count() + tasks.count(),

        "gestiones_total":   gestiones.count(),
        "reclamos_total":    reclamos.count(),
        "solicitudes_total": solicitudes.count(),
        "tareas_total":      tasks.count(),

        "iniciadas": (
            count_estado("registrado")
            + count_estado("iniciada")
            + count_estado("iniciado")
        ),
        "analisis": (
            count_estado("analisis")
            + count_estado("en-analisis")
            + count_estado("en_analisis")
        ),
        "programadas": (
            count_estado("programada")
            + count_estado("programado")
        ),
        "ejecucion": (
            count_estado("ejecucion")
            + count_estado("en-ejecucion")
            + count_estado("en_ejecucion")
            + tasks.filter(status=Task.Status.IN_PROGRESS).count()
        ),
        "finalizadas": (
            count_estado("finalizada")
            + count_estado("finalizado")
            + count_estado("resuelto")
            + count_estado("resuelta")
            + tasks.filter(status=Task.Status.COMPLETED).count()
        ),
        "reabiertas": (
            count_estado("reabierta")
            + count_estado("reabierto")
        ),
        "rechazadas": (
            count_estado("rechazada")
            + count_estado("rechazado")
        ),
        "criticas": tasks.exclude(
            status=Task.Status.COMPLETED
        ).filter(due_date__lt=today).count(),
        "overdue": tasks.exclude(
            status=Task.Status.COMPLETED
        ).filter(due_date__lt=today).count(),

        # Compatibilidad con keys de Task.Status
        Task.Status.REGISTERED:  tasks.filter(status=Task.Status.REGISTERED).count(),
        Task.Status.PENDING:     tasks.filter(status=Task.Status.PENDING).count(),
        Task.Status.IN_PROGRESS: tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        Task.Status.COMPLETED:   tasks.filter(status=Task.Status.COMPLETED).count(),
    }

    # ── Listas recientes ─────────────────────────────────────────────────────
    reclamos_recientes  = reclamos.order_by("-creada")[:5]
    solicitudes_activas = solicitudes.exclude(
        estado__codigo__in=[
            "finalizada", "finalizado", "resuelta", "resuelto",
            "rechazada", "rechazado",
        ]
    ).order_by("-creada")[:5]

    tareas_pendientes = tasks.exclude(
        status=Task.Status.COMPLETED
    ).order_by("due_date", "-created_at")[:5]

    areas_stats = (
        gestiones
        .values("area_responsable__id", "area_responsable__nombre")
        .annotate(total=Count("id"))
        .order_by("area_responsable__nombre")
    )

    # ── Fecha en español ─────────────────────────────────────────────────────
    DIAS  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    MESES = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    hoy = timezone.now().date()
    current_date_str = f"{DIAS[hoy.weekday()]}, {hoy.day} de {MESES[hoy.month-1]} de {hoy.year}"

    context = {
        "stats":              stats,
        "current_date":       current_date_str,
        "start_date":         start_date_str,
        "end_date":           end_date_str,
        "selected_area":      area,
        "selected_tipo":      tipo,
        "reclamos_recientes":  reclamos_recientes,
        "solicitudes_activas": solicitudes_activas,
        "tareas_pendientes":   tareas_pendientes,
        "areas_stats":         areas_stats,
    }

    # ── Template único: dashboard.html decide internamente qué mostrar
    # a cada rol mediante bloques {% if %} ──────────────────────────────────
    template = "dashboard/dashboard.html"

    return render(request, template, context)


@login_required
def mapa_operativo(request):
    gestiones = Gestion.objects.select_related(
        "categoria", "area_responsable", "estado", "ciudadano",
    ).filter(
        latitud__isnull=False,
        longitud__isnull=False,
    ).order_by("-creada")

    return render(request, "dashboard/mapa_operativo.html", {"gestiones": gestiones})


@login_required
def gestion_list(request):
    tipo   = request.GET.get("tipo")
    estado = request.GET.get("estado")
    area   = request.GET.get("area")

    gestiones = Gestion.objects.select_related(
        "ciudadano", "categoria", "area_responsable", "estado",
    ).order_by("-creada")

    if tipo:
        gestiones = gestiones.filter(categoria__tipo=tipo)
    if estado:
        gestiones = gestiones.filter(estado__codigo=estado)
    if area:
        gestiones = gestiones.filter(area_responsable_id=area)

    return render(request, "gestiones/gestion_list.html", {
        "gestiones":      gestiones,
        "selected_tipo":  tipo,
        "selected_estado": estado,
        "selected_area":  area,
        "tipo_reclamo":   CategoriaGestion.TIPO_RECLAMO,
        "tipo_solicitud": CategoriaGestion.TIPO_SOLICITUD,
    })


@login_required
def gestion_detail(request, gestion_id):
    gestion = get_object_or_404(
        Gestion.objects.select_related(
            "ciudadano", "categoria", "area_responsable", "estado",
        ),
        id=gestion_id,
    )
    adjuntos = AdjuntoGestion.objects.filter(gestion=gestion).order_by("creado")

    return render(request, "gestiones/gestion_detail.html", {
        "gestion":  gestion,
        "adjuntos": adjuntos,
    })


@login_required
def reclamos_list(request):
    request.GET = request.GET.copy()
    request.GET["tipo"] = CategoriaGestion.TIPO_RECLAMO
    return gestion_list(request)


@login_required
def solicitudes_list(request):
    request.GET = request.GET.copy()
    request.GET["tipo"] = CategoriaGestion.TIPO_SOLICITUD
    return gestion_list(request)


# ════════════════════════════════════════════════════════════════════════════
# Cambiar estado de gestión
# ════════════════════════════════════════════════════════════════════════════

class CambiarEstadoForm(forms.Form):
    estado = forms.ModelChoiceField(
        queryset=EstadoGestion.objects.filter(activo=True).order_by("orden"),
        label="Nuevo estado",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    comentario = forms.CharField(
        label="Comentario (opcional)",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Agregá una nota sobre este cambio de estado...",
        }),
    )


@login_required
def gestion_cambiar_estado(request, gestion_id):
    gestion = get_object_or_404(Gestion, id=gestion_id)
    user = request.user

    # Permisos: ciudadanos no pueden cambiar estado.
    # Operador, Funcionario, Secretario y Administrador sí pueden.
    if user.role == user.Role.CIUDADANO:
        messages.error(request, "No tenés permisos para cambiar el estado de esta gestión.")
        return redirect('gestion_detail', gestion_id=gestion.id)

    if request.method == "POST":
        form = CambiarEstadoForm(request.POST)
        if form.is_valid():
            estado_anterior = gestion.estado
            gestion.estado = form.cleaned_data["estado"]
            gestion.save(update_fields=["estado", "actualizada"])

            messages.success(
                request,
                f"Estado actualizado: {estado_anterior.nombre} → {gestion.estado.nombre}"
            )
            return redirect('gestion_detail', gestion_id=gestion.id)
    else:
        form = CambiarEstadoForm(initial={"estado": gestion.estado_id})

    return render(request, "gestiones/gestion_cambiar_estado.html", {
        "gestion": gestion,
        "form": form,
    })
