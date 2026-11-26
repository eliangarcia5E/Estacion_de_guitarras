import shutil
from pathlib import Path

from django.conf import settings
from django.db import migrations


# Los productos que antes estaban escritos a mano en productos.html.
# Sus imágenes se copian a MEDIA_ROOT/productos/ para que se administren igual que las nuevas.
PRODUCTOS_INICIALES = [
    ('Guitarra Stratocaster Tagima Tw530 Woodstock Tw-530 Strato Cor Black', 6499, 'Cuerpo de Basswood, mástil de arce y diapasón con 22 trastes. Pastillas single coil que ofrecen ese tono clásico y brillante de las strato.', 'tagima.jpg'),
    ('Guitarra Fender Stratocaster Solid Body Electric Guitar', 18500, 'Cuerpo de aliso con acabado brillante, mástil de arce con perfil en C y diapasón de arce de radio 9.5 pulgadas.', 'fender_strato.jpg'),
    ('Guitarra Gibson Custom Shop CS9 Les Paul Standard BB VOS', 78000, 'Construcción Custom Shop con tapa de arce figurado, cuerpo de caoba de una pieza y diapasón de palo de rosa indio.', 'gibson_lespaul.jpg'),
    ('Guitarra Fender Vintera III Jaguar', 27500, 'Cuerpo de aliso, mástil de arce con perfil vintage en C y diapasón de palo de rosa. Sistema de trémolo flotante y switches de circuito característicos de la Jaguar.', 'fender_jaguar.jpg'),
    ('Guitarra Gibson Explorer Vintage', 52000, 'Cuerpo de caoba con la icónica forma angular Explorer, mástil de caoba pegado y pastillas humbucker de alta ganancia para un tono potente y agresivo.', 'gibson_explorer.jpg'),
    ('Guitarra Gibson Acústica Vintage', 38900, 'Tapa de abeto macizo y aros y fondo de caoba, construcción tradicional Gibson que entrega un tono cálido y proyección excepcional.', 'gibson_acustica.jpg'),
    ('Pedal de Efectos Boss DS-1 Distortion', 1850, 'El pedal de distorsión más vendido de la historia. Controles sencillos de Gain, Tone y Level con la legendaria construcción indestructible de BOSS.', 'ds1.jpg'),
    ('Pedal de Efectos Boss SD-1 Super Overdrive', 1950, 'Overdrive clásico de BOSS que agrega calidez y saturación suave, ideal para empujar el amplificador con un tono cálido tipo tubo.', 'sd1.jpg'),
    ('Pedal de Efectos Boss CH-1 Super Chorus', 2100, 'Chorus estéreo de alta calidad con controles de Rate, Depth, Effect Level y EQ para un sonido amplio y brillante.', 'ch1.jpg'),
    ('Pedal Digitech Whammy', 6800, 'Pedal de cambio de tono en tiempo real controlado por pedal expresivo, capaz de efectos de armonía, octavas y el clásico whammy ascendente/descendente.', 'whammy.jpg'),
]


def cargar_productos_iniciales(apps, schema_editor):
    Producto = apps.get_model('tienda', 'Producto')
    if Producto.objects.exists():
        return

    origen_imagenes = Path(settings.BASE_DIR) / 'tienda' / 'static' / 'tienda'
    destino_imagenes = Path(settings.MEDIA_ROOT) / 'productos'
    destino_imagenes.mkdir(parents=True, exist_ok=True)

    for nombre, precio, descripcion, archivo in PRODUCTOS_INICIALES:
        ruta_imagen = ''
        origen = origen_imagenes / archivo
        if origen.exists():
            shutil.copy2(origen, destino_imagenes / archivo)
            ruta_imagen = f'productos/{archivo}'

        Producto.objects.create(
            nombre=nombre,
            precio=precio,
            descripcion=descripcion,
            imagen=ruta_imagen,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0003_producto_estado_pedido'),
    ]

    operations = [
        migrations.RunPython(cargar_productos_iniciales, migrations.RunPython.noop),
    ]
