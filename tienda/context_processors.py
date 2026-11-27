from django.contrib.auth.models import User


def usuarios_registrados(request):
    """Lista de usuarios para el menú del superusuario; a los demás no se les envía."""
    if request.user.is_authenticated and request.user.is_superuser:
        return {'usuarios_registrados': User.objects.order_by('username')}
    return {}
