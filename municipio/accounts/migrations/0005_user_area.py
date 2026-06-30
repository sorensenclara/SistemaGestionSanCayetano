from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_add_role_secretario'),
        ('citizen', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='area',
            field=models.ForeignKey(
                blank=True,
                help_text='Área a la que pertenece este usuario (Funcionario, Operador o Secretario).',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='usuarios',
                to='citizen.area',
                verbose_name='Área',
            ),
        ),
    ]
