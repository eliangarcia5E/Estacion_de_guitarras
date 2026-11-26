from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Empleado

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'puesto', 'email', 'telefono', 'activo')
    list_filter = ('puesto', 'activo')
    search_fields = ('nombre', 'apellido', 'email')
    list_editable = ('activo',)