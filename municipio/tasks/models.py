from django.db import models
from django.conf import settings
from django.utils import timezone

class Article(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    unit = models.CharField(max_length=50, verbose_name='Unidad de medida', default='Unidad')

    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

class Task(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REG', 'Registrada'
        PENDING = 'PEN', 'Pendiente de Asignar'
        IN_PROGRESS = 'INP', 'En Curso'
        COMPLETED = 'COM', 'Finalizada'

    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    due_date = models.DateField(verbose_name='Fecha de Vencimiento')
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.REGISTERED,
        verbose_name='Estado'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Asignado a'
    )
    involved_persons = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='involved_tasks',
        blank=True,
        verbose_name='Personas Involucradas'
    )
    planned_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, verbose_name='Horas Planificadas'
    )
    executed_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, verbose_name='Horas Ejecutadas'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Creado por'
    )

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.status != self.Status.COMPLETED and self.due_date:
            return self.due_date < timezone.now().date()
        return False

class TaskResource(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='resources', verbose_name='Tarea')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='task_resources', verbose_name='Artículo')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Cantidad')

    class Meta:
        verbose_name = 'Recurso de Tarea'
        verbose_name_plural = 'Recursos de Tarea'

    def __str__(self):
        return f"{self.quantity} x {self.article.name} para {self.task.title}"
