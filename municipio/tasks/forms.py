from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from django.forms.models import inlineformset_factory
from .models import Task, Article, TaskResource
from accounts.models import User

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['name', 'description', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar Artículo', css_class='btn-primary'))

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'due_date', 'status', 
            'assigned_to', 'involved_persons', 'planned_hours', 'executed_hours'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'involved_persons': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Important because we include a formset inside the same HTML form
        
        # Only assignable by admin or func
        qs = User.objects.filter(role__in=[User.Role.FUNCIONARIO, User.Role.OPERADOR])
        self.fields['assigned_to'].queryset = qs
        self.fields['involved_persons'].queryset = User.objects.all()

class TaskResourceForm(forms.ModelForm):
    class Meta:
        model = TaskResource
        fields = ['article', 'quantity']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

TaskResourceFormSet = inlineformset_factory(
    Task, 
    TaskResource, 
    form=TaskResourceForm,
    extra=1,
    can_delete=True
)
