from django import forms
from .models import User
from django.contrib.auth import authenticate
from django.forms import PasswordInput


class RegisterForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña", widget=PasswordInput())

    def clean_username(self):
        username = self.cleaned_data["username"]
        username_l = username.lower()
        # comparacion case-insensitive
        if User.objects.filter(username__iexact=username_l).exists():
            raise forms.ValidationError("¡El nombre de usuario ya existe!")
        return username

    def clean_contraseña(self):
        contraseña = self.cleaned_data["contraseña"]
        if len(contraseña) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 carácterres")
        return contraseña

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña", widget=PasswordInput())

    def clean(self):
        username = self.cleaned_data["username"]
        contraseña = self.cleaned_data["contraseña"]
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("¡El nombre de usuario no existe!")
        usuario = authenticate(username=username, password=contraseña)
        if usuario is None:
            raise forms.ValidationError("¡Nombre de usuario o contraseña incorrecta!")
        return self.cleaned_data