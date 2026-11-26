from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.templatetags.static import static

EXTENSIONES_IMAGEN = ['jpg', 'jpeg', 'png', 'webp', 'gif']

# Create your models here.
class Empleado(models.Model):
    PUESTOS = [
        ('Vendedor', 'Vendedor / Asesor'),
        ('Tecnico', 'Técnico / Luthier'),
        ('Cajero', 'Cajero'),
        ('Gerente', 'Gerente de Tienda'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    puesto = models.CharField(max_length=50, choices=PUESTOS)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_contratacion = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.puesto}"


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    telefono = models.CharField(max_length=10)

    def __str__(self):
        return f"Perfil de {self.usuario}"


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen = models.FileField(
        upload_to='productos/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONES_IMAGEN)],
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nombre

    @property
    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        return static('tienda/image_028521.jpg')

    @property
    def precio_texto(self):
        return f"${int(self.precio):,} MXN"


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    banco = models.CharField(max_length=100)
    ultimos_digitos = models.CharField(max_length=4)
    direccion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Pedido {self.pk} de {self.usuario}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items',
    )
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nombre} x{self.cantidad}"
