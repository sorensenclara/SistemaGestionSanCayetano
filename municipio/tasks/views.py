from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import transaction

from .models import Task, Article, TaskResource
from accounts.models import User
from .forms import TaskForm, TaskResourceFormSet, ArticleForm
import json

# =======================
# KANBAN BOARD
# =======================
@login_required
def kanban_board(request):
    tasks = Task.objects.all()
    if request.user.is_operador():
        tasks = tasks.filter(assigned_to=request.user)

    context = {
        'tasks_registered': tasks.filter(status=Task.Status.REGISTERED),
        'tasks_pending': tasks.filter(status=Task.Status.PENDING),
        'tasks_in_progress': tasks.filter(status=Task.Status.IN_PROGRESS),
        'tasks_completed': tasks.filter(status=Task.Status.COMPLETED),
    }
    return render(request, 'tasks/kanban.html', context)

@login_required
@require_POST
def update_task_status(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')
        
        task = get_object_or_404(Task, id=task_id)
        
        if request.user.is_operador() and task.assigned_to != request.user:
             return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
             
        if new_status in dict(Task.Status.choices):
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Estado inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# =======================
# TASK CRUD (EXTENDED)
# =======================
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_operador():
            qs = qs.filter(assigned_to=self.request.user)
        return qs

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

@login_required
def task_create(request):
    if request.user.is_operador():
        return redirect('kanban')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        formset = TaskResourceFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                task = form.save(commit=False)
                task.created_by = request.user
                task.save()
                form.save_m2m() # For involved_persons ManyToMany
                
                formset.instance = task
                formset.save()
            return redirect('task_list')
    else:
        form = TaskForm()
        formset = TaskResourceFormSet()
        
    return render(request, 'tasks/task_form.html', {'form': form, 'formset': formset, 'title': 'Crear Tarea'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.is_operador() and task.assigned_to != request.user:
         return redirect('kanban')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        formset = TaskResourceFormSet(request.POST, instance=task)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
        formset = TaskResourceFormSet(instance=task)
        
    return render(request, 'tasks/task_form.html', {'form': form, 'formset': formset, 'title': f'Editar Tarea: {task.title}'})

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        return not self.request.user.is_operador()

# =======================
# ARTICLE CRUD
# =======================
class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'tasks/article_list.html'
    context_object_name = 'articles'

class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'tasks/article_form.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        return not self.request.user.is_operador()

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'tasks/article_form.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        return not self.request.user.is_operador()

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'tasks/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        return not self.request.user.is_operador()
