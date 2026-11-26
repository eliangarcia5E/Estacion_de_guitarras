import re
from datetime import date

import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from .models import Empleado, PerfilUsuario, Producto


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'puesto', 'email', 'telefono', 'fecha_contratacion', 'activo']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date'}),
        }


class RegistroForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )
    email = forms.EmailField(label='Correo electrónico', max_length=254)
    telefono = forms.CharField(label='Número de celular (10 dígitos)', max_length=20)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].replace(' ', '').replace('-', '')
        if not re.fullmatch(r'\d{10}', telefono):
            raise ValidationError('El número de celular debe tener 10 dígitos.')
        return telefono

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe una cuenta con ese correo electrónico.')
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('password1')
        password2 = cleaned.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')

        if password1:
            usuario_temporal = User(
                username=cleaned.get('username', ''),
                email=cleaned.get('email', ''),
            )
            try:
                validate_password(password1, user=usuario_temporal)
            except ValidationError as error:
                self.add_error('password1', error)

        return cleaned


class PagoForm(forms.Form):
    direccion = forms.CharField(label='Dirección de envío', max_length=255)
    numero_tarjeta = forms.CharField(label='Número de tarjeta (16 dígitos)', max_length=19)
    vencimiento = forms.CharField(label='Fecha de vencimiento (MM/AA)', max_length=5)
    banco = forms.CharField(label='Nombre del banco', max_length=100)

    def clean_numero_tarjeta(self):
        numero = self.cleaned_data['numero_tarjeta'].replace(' ', '').replace('-', '')
        if not re.fullmatch(r'\d{16}', numero):
            raise ValidationError('El número de tarjeta debe tener 16 dígitos.')
        return numero

    def clean_vencimiento(self):
        vencimiento = self.cleaned_data['vencimiento'].strip()
        coincidencia = re.fullmatch(r'(0[1-9]|1[0-2])/(\d{2})', vencimiento)
        if not coincidencia:
            raise ValidationError('Usa el formato MM/AA, por ejemplo 08/29.')

        mes = int(coincidencia.group(1))
        anio = 2000 + int(coincidencia.group(2))
        hoy = date.today()
        if (anio, mes) < (hoy.year, hoy.month):
            raise ValidationError('La tarjeta ya está vencida.')
        return vencimiento


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'imagen']
        labels = {
            'nombre': 'Nombre del producto',
            'precio': 'Precio (MXN)',
            'descripcion': 'Descripción',
            'imagen': 'Imagen del producto',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'imagen': forms.FileInput(attrs={'accept': 'image/*', 'id': 'input-imagen'}),
        }
