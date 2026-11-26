import json
from decimal import Decimal, InvalidOperation
from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Empleado, Pedido, PedidoItem, PerfilUsuario, Producto
from .forms import EmpleadoForm, PagoForm, ProductoForm, RegistroForm



def index(request):
    return render(request, 'tienda/index.html')

def nosotros(request):
    return render(request, 'tienda/nosotros.html')

def productos(request):
    return render(request, 'tienda/productos.html', {
        'productos': Producto.objects.all(),
    })

def servicios(request):
    return render(request, 'tienda/servicios.html')

def contacto(request):
    return render(request, 'tienda/contacto.html')



def _siguiente_seguro(request):
    """Devuelve la URL de 'next' solo si es un destino interno del sitio."""
    siguiente = request.POST.get('next') or request.GET.get('next', '')
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente,
        allowed_hosts={request.get_host()},
    ):
        return siguiente
    return ''


def login_view(request):
    siguiente = _siguiente_seguro(request)
    error = None

    if request.user.is_authenticated:
        return redirect(siguiente or 'index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect(siguiente or 'index')

        error = 'Usuario o contraseña incorrectos.'

    return render(request, 'tienda/login.html', {
        'error': error,
        'next': siguiente,
    })


def registro_view(request):
    siguiente = _siguiente_seguro(request)

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
            )
            PerfilUsuario.objects.create(
                usuario=usuario,
                telefono=form.cleaned_data['telefono'],
            )
            messages.success(request, '¡Cuenta creada! Ya puedes iniciar sesión.')
            url_login = reverse('login')
            if siguiente:
                url_login += '?next=' + siguiente
            return redirect(url_login)
    else:
        form = RegistroForm()

    return render(request, 'tienda/registro.html', {
        'form': form,
        'next': siguiente,
    })


def logout_view(request):
    logout(request)
    return redirect('index')


def solo_administradores(vista):
    """Solo entran administradores (staff o superusuario).

    Si no hay sesión, manda al login. Si hay sesión pero no es administrador,
    manda al inicio.
    """
    @wraps(vista)
    def envuelta(request, *args, **kwargs):
        if not request.user.is_authenticated:
            url_login = reverse('login') + '?' + urlencode({'next': request.get_full_path()})
            return redirect(url_login)
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('index')
        return vista(request, *args, **kwargs)
    return envuelta


def requiere_sesion(vista):
    """Solo entran usuarios con sesión iniciada; el resto va al login."""
    @wraps(vista)
    def envuelta(request, *args, **kwargs):
        if not request.user.is_authenticated:
            url_login = reverse('login') + '?' + urlencode({'next': request.get_full_path()})
            return redirect(url_login)
        return vista(request, *args, **kwargs)
    return envuelta



@solo_administradores
def empleados(request):
    lista = Empleado.objects.order_by('apellido', 'nombre')
    return render(request, 'tienda/empleados.html', {'empleados': lista})


@solo_administradores
def guardar_empleado(request, empleado_id=None):
    empleado = get_object_or_404(Empleado, pk=empleado_id) if empleado_id else None
    form = EmpleadoForm(request.POST or None, instance=empleado)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Empleado guardado correctamente.')
        return redirect('empleados')

    return render(request, 'tienda/empleado_form.html', {'form': form, 'empleado': empleado})


@solo_administradores
def eliminar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)

    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado.')
        return redirect('empleados')

    return render(request, 'tienda/eliminar_empleado.html', {'empleado': empleado})



@requiere_sesion
def iniciar_pago(request):
    """Recibe el carrito de la página de productos y lo guarda en la sesión."""
    if request.method != 'POST':
        return redirect('productos')

    try:
        items = json.loads(request.POST.get('carrito', '[]'))
    except json.JSONDecodeError:
        items = []
    if not isinstance(items, list):
        items = []

    carrito = []
    for item in items:
        try:
            nombre = str(item['titulo'])[:255]
            precio = Decimal(str(item['precio']))
            cantidad = int(item['cantidad'])
        except (KeyError, TypeError, ValueError, InvalidOperation):
            continue
        if precio.is_finite() and precio >= 0 and cantidad >= 1:
            carrito.append({'nombre': nombre, 'precio': str(precio), 'cantidad': cantidad})

    if not carrito:
        return redirect('productos')

    request.session['carrito_pago'] = carrito
    return redirect('pago')


NUMERO_TIENDA_WHATSAPP = '528312897837'


def _enlace_whatsapp_tienda(pedido, total):
    """Enlace de WhatsApp con el resumen del pedido, listo para mandarse a la tienda."""
    lineas = [
        'Hola, acabo de realizar una compra en Estación de Guitarras.',
        f'Pedido: #{pedido.pk}',
        f'Usuario: {pedido.usuario.username}',
        f'Correo: {pedido.usuario.email or "sin correo"}',
        f'Celular: {_telefono_de(pedido.usuario) or "sin número"}',
        f'Tarjeta: **** **** **** {pedido.ultimos_digitos} ({pedido.banco})',
        'Productos:',
    ]
    lineas += [f'- {item.nombre} x{item.cantidad}' for item in pedido.items.all()]
    lineas.append(f'Total: ${total} MXN')
    return f"https://wa.me/{NUMERO_TIENDA_WHATSAPP}?" + urlencode({'text': '\n'.join(lineas)})


def _telefono_de(usuario):
    try:
        return usuario.perfil.telefono
    except PerfilUsuario.DoesNotExist:
        return ''


def _resumen(carrito):
    lineas = []
    total = Decimal('0')
    for item in carrito:
        subtotal = Decimal(item['precio']) * item['cantidad']
        total += subtotal
        lineas.append({
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'subtotal': subtotal,
        })
    return lineas, total


@requiere_sesion
def pago(request):
    # Después de confirmar, la compra se muestra una sola vez.
    pedido_id = request.session.pop('pedido_confirmado', None)
    if pedido_id:
        pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
        total = sum((item.precio * item.cantidad for item in pedido.items.all()), Decimal('0'))
        return render(request, 'tienda/pago.html', {
            'confirmado': True,
            'pedido': pedido,
            'total': total,
            'telefono': _telefono_de(request.user),
            'enlace_whatsapp': _enlace_whatsapp_tienda(pedido, total),
        })

    carrito = request.session.get('carrito_pago')
    if not carrito:
        return redirect('productos')

    lineas, total = _resumen(carrito)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero_tarjeta']
            # Solo se guardan los últimos 4 dígitos; el número completo y el banco no se almacenan.
            pedido = Pedido.objects.create(
                usuario=request.user,
                banco=form.cleaned_data['banco'],
                ultimos_digitos=numero[-4:],
                direccion=form.cleaned_data['direccion'],
            )
            for item in carrito:
                PedidoItem.objects.create(
                    pedido=pedido,
                    nombre=item['nombre'],
                    precio=Decimal(item['precio']),
                    cantidad=item['cantidad'],
                )
            del request.session['carrito_pago']
            request.session['pedido_confirmado'] = pedido.pk
            return redirect('pago')
    else:
        form = PagoForm()

    return render(request, 'tienda/pago.html', {
        'confirmado': False,
        'form': form,
        'lineas': lineas,
        'total': total,
        'telefono': _telefono_de(request.user),
    })


def solo_superusuarios(vista):
    """Solo entra el superusuario; el resto va al inicio."""
    @wraps(vista)
    def envuelta(request, *args, **kwargs):
        if not request.user.is_authenticated:
            url_login = reverse('login') + '?' + urlencode({'next': request.get_full_path()})
            return redirect(url_login)
        if not request.user.is_superuser:
            return redirect('index')
        return vista(request, *args, **kwargs)
    return envuelta


@requiere_sesion
def pedidos(request):
    if request.user.is_superuser:
        lista = Pedido.objects.select_related('usuario__perfil').prefetch_related('items')
        return render(request, 'tienda/pedidos.html', {
            'pedidos': lista,
            'es_admin': True,
            'estados': Pedido.ESTADOS,
        })

    lista = Pedido.objects.filter(usuario=request.user).prefetch_related('items')
    return render(request, 'tienda/pedidos.html', {
        'pedidos': lista,
        'es_admin': False,
    })


@solo_superusuarios
def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        estado = request.POST.get('estado')
        if estado in dict(Pedido.ESTADOS):
            pedido.estado = estado
            pedido.save(update_fields=['estado'])
    return redirect('pedidos')



def _guardar_producto(request, producto):
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('productos')

    return render(request, 'tienda/producto_form.html', {'form': form, 'producto': producto})


@solo_superusuarios
def producto_agregar(request):
    return _guardar_producto(request, None)


@solo_superusuarios
def producto_editar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return _guardar_producto(request, producto)


@solo_superusuarios
def productos_gestionar(request):
    accion = request.GET.get('accion', 'editar')
    if accion not in ('editar', 'eliminar'):
        accion = 'editar'
    return render(request, 'tienda/productos_gestionar.html', {
        'productos': Producto.objects.all(),
        'accion': accion,
    })


@solo_superusuarios
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        if producto.imagen:
            producto.imagen.delete(save=False)
        producto.delete()
        return redirect('productos')

    return render(request, 'tienda/producto_eliminar.html', {'producto': producto})
