import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('banco', models.CharField(max_length=100)),
                ('ultimos_digitos', models.CharField(max_length=4)),
                ('direccion', models.CharField(max_length=255)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='PedidoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad', models.PositiveIntegerField()),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='tienda.pedido')),
            ],
        ),
    ]
