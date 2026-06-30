from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_address_user_birth_date_user_city_user_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Administrador'),
                    ('SECR', 'Secretario'),
                    ('FUNC', 'Funcionario'),
                    ('OPER', 'Operador'),
                    ('CIUD', 'Ciudadano'),
                ],
                default='CIUD',
                max_length=5,
                verbose_name='Rol',
            ),
        ),
    ]
