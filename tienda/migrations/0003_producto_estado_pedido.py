import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0002_pedido_pedidoitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('entregado', 'Entregado')], default='pendiente', max_length=20),
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.TextField(blank=True)),
                ('imagen', models.FileField(blank=True, upload_to='productos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif'])])),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
