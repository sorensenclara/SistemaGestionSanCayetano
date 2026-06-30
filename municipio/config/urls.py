from accounts.views import CustomLoginView, acceso_inicial
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from dashboard import views as dashboard_views
from tasks import views as tasks_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Pantalla inicial
    path("", acceso_inicial, name="acceso_inicial"),

    # Admin
    path("admin/", admin.site.urls),

    # Auth COM
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="acceso_inicial"), name="logout"),

    # Dashboard COM
    path("dashboard/", dashboard_views.dashboard_home, name="dashboard"),

    # Kanban
    path("kanban/", tasks_views.kanban_board, name="kanban"),

    # Tasks
    path("tasks/", tasks_views.TaskListView.as_view(), name="task_list"),
    path("tasks/<int:pk>/", tasks_views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/create/", tasks_views.task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", tasks_views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", tasks_views.TaskDeleteView.as_view(), name="task_delete"),
    path("tasks/update_status/", tasks_views.update_task_status, name="update_task_status"),

    # Artículos
    path("articles/", tasks_views.ArticleListView.as_view(), name="article_list"),
    path("articles/create/", tasks_views.ArticleCreateView.as_view(), name="article_create"),
    path("articles/<int:pk>/edit/", tasks_views.ArticleUpdateView.as_view(), name="article_update"),
    path("articles/<int:pk>/delete/", tasks_views.ArticleDeleteView.as_view(), name="article_delete"),

    # Mapa operativo
    path("mapa-operativo/", dashboard_views.mapa_operativo, name="mapa_operativo"),

    # Gestiones
    path("gestiones/", dashboard_views.gestion_list, name="gestion_list"),
    path("gestiones/<int:gestion_id>/", dashboard_views.gestion_detail, name="gestion_detail"),
    path("gestiones/<int:gestion_id>/cambiar-estado/", dashboard_views.gestion_cambiar_estado, name="gestion_cambiar_estado"),
    path("reclamos/", dashboard_views.reclamos_list, name="reclamos_list"),
    path("solicitudes/", dashboard_views.solicitudes_list, name="solicitudes_list"),

    # App Ciudadana
    path("ciudadano/", include("citizen.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
