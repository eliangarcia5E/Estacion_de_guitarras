from django.urls import path
from . import views

urlpatterns = [
    # Páginas del sitio
    path('', views.index, name='index'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.productos, name='productos'),
    path('servicios/', views.servicios, name='servicios'),
    path('contacto/', views.contacto, name='contacto'),

    # Inicio de sesión y registro
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Compras y pedidos (solo con sesión iniciada)
    path('pago/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/', views.pago, name='pago'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedidos/<int:pedido_id>/estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),

    # Catálogo: administración de productos (solo superusuario)
    path('productos/agregar/', views.producto_agregar, name='producto_agregar'),
    path('productos/gestionar/', views.productos_gestionar, name='productos_gestionar'),
    path('productos/editar/<int:producto_id>/', views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:producto_id>/', views.producto_eliminar, name='producto_eliminar'),

    # Lista de usuarios registrados (solo superusuario)
    path('usuarios/', views.usuarios, name='usuarios'),

    # CRUD de empleados (solo administradores)
    path('empleados/', views.empleados, name='empleados'),
    path('empleados/agregar/', views.guardar_empleado, name='agregar_empleado'),
    path('empleados/editar/<int:empleado_id>/', views.guardar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:empleado_id>/', views.eliminar_empleado, name='eliminar_empleado'),
]
