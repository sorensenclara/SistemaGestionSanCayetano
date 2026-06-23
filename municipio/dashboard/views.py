from django.shortcuts import render, get_object_or_404
from citizen.models import Gestion, CategoriaGestion, AdjuntoGestion
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
import datetime

from tasks.models import Task
from citizen.models import Gestion, CategoriaGestion


@login_required
def dashboard_home(request):
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    area = request.GET.get("area")
    tipo = request.GET.get("tipo")

    gestiones = Gestion.objects.select_related(
        "ciudadano",
        "categoria",
        "area_responsable",
        "estado",
    ).all()

    tasks = Task.objects.all()

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            gestiones = gestiones.filter(creada__date__gte=start_date)
            tasks = tasks.filter(created_at__date__gte=start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            gestiones = gestiones.filter(creada__date__lte=end_date)
            tasks = tasks.filter(created_at__date__lte=end_date)
        except ValueError:
            pass

    if area:
        gestiones = gestiones.filter(area_responsable_id=area)

    if tipo:
        gestiones = gestiones.filter(categoria__tipo=tipo)

    reclamos = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_RECLAMO)
    solicitudes = gestiones.filter(categoria__tipo=CategoriaGestion.TIPO_SOLICITUD)

    def count_estado(codigo):
        return gestiones.filter(estado__codigo=codigo).count()

    today = timezone.now().date()

    stats = {
        "total": gestiones.count() + tasks.count(),

        "gestiones_total": gestiones.count(),
        "reclamos_total": reclamos.count(),
        "solicitudes_total": solicitudes.count(),
        "tareas_total": tasks.count(),

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
        ).filter(
            due_date__lt=today
        ).count(),

        "overdue": tasks.exclude(
            status=Task.Status.COMPLETED
        ).filter(
            due_date__lt=today
        ).count(),

        # Compatibilidad con dashboard viejo
        Task.Status.REGISTERED: tasks.filter(status=Task.Status.REGISTERED).count(),
        Task.Status.PENDING: tasks.filter(status=Task.Status.PENDING).count(),
        Task.Status.IN_PROGRESS: tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        Task.Status.COMPLETED: tasks.filter(status=Task.Status.COMPLETED).count(),
    }

    reclamos_recientes = reclamos.order_by("-creada")[:5]
    solicitudes_activas = solicitudes.exclude(
        estado__codigo__in=["finalizada", "finalizado", "resuelta", "resuelto", "rechazada", "rechazado"]
    ).order_by("-creada")[:5]

    tareas_pendientes = tasks.exclude(
        status=Task.Status.COMPLETED
    ).order_by("due_date", "-created_at")[:5]

    areas_stats = (
        gestiones.values("area_responsable__id", "area_responsable__nombre")
        .annotate(total=Count("id"))
        .order_by("area_responsable__nombre")
    )

    context = {
        "stats": stats,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "selected_area": area,
        "selected_tipo": tipo,
        "reclamos_recientes": reclamos_recientes,
        "solicitudes_activas": solicitudes_activas,
        "tareas_pendientes": tareas_pendientes,
        "areas_stats": areas_stats,
    }

    return render(request, "dashboard/dashboard_admin.html", context)


@login_required
def mapa_operativo(request):
    gestiones = Gestion.objects.select_related(
        "categoria",
        "area_responsable",
        "estado",
        "ciudadano",
    ).filter(
        latitud__isnull=False,
        longitud__isnull=False,
    ).order_by("-creada")

    return render(request, "dashboard/mapa_operativo.html", {
        "gestiones": gestiones
    })

@login_required
def gestion_list(request):
    tipo = request.GET.get("tipo")
    estado = request.GET.get("estado")
    area = request.GET.get("area")

    gestiones = Gestion.objects.select_related(
        "ciudadano",
        "categoria",
        "area_responsable",
        "estado",
    ).order_by("-creada")

    if tipo:
        gestiones = gestiones.filter(categoria__tipo=tipo)

    if estado:
        gestiones = gestiones.filter(estado__codigo=estado)

    if area:
        gestiones = gestiones.filter(area_responsable_id=area)

    return render(request, "gestiones/gestion_list.html", {
        "gestiones": gestiones,
        "selected_tipo": tipo,
        "selected_estado": estado,
        "selected_area": area,
        "tipo_reclamo": CategoriaGestion.TIPO_RECLAMO,
        "tipo_solicitud": CategoriaGestion.TIPO_SOLICITUD,
    })


@login_required
def gestion_detail(request, gestion_id):
    gestion = get_object_or_404(
        Gestion.objects.select_related(
            "ciudadano",
            "categoria",
            "area_responsable",
            "estado",
        ),
        id=gestion_id,
    )

    adjuntos = AdjuntoGestion.objects.filter(
        gestion=gestion
    ).order_by("creado")

    return render(request, "gestiones/gestion_detail.html", {
        "gestion": gestion,
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