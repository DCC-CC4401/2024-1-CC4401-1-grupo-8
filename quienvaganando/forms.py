from django import forms
from .models import User, Torneo
from django.contrib.auth import authenticate

# falta agregar eventos
class NuevoTorneoForm(forms.Form):
    nombre = forms.CharField(label="Nombre del Torneo", max_length=250)
    participantes = forms.CharField(widget=forms.Textarea())

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        nombre.lower()
        if Torneo.objects.filter(nombre=nombre).exists():
            raise forms.ValidationError("¡Ya existe un torneo con este nombre!")   
        return nombre
    
    def clean_participantes(self):
        participantes = self.cleaned_data["participantes"]
        participantes = participantes.lower().strip(",")
        # ver que no hay repetidos
        if len(participantes != len(set(participantes))):
            raise forms.ValidationError("Hay participantes repetidos")
        return participantes


class RegisterForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña")

    def clean_username(self):
        username = self.cleaned_data["username"]
        username = username.lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("¡El nombre de usuario ya existe!")
        return username

    def clean_contraseña(self):
        contraseña = self.cleaned_data["contraseña"]
        if len(contraseña) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 carácterres")
        return contraseña

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña")

    def clean_username(self):
        username = self.cleaned_data["username"]
        username = username.lower()
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("¡El nombre de usuario no existe!")
        return username
    
    def clean_contraseña(self):
        username = self.cleaned_data["username"]
        contraseña = self.cleaned_data["contraseña"]
        usuario = authenticate(username=username,password=contraseña)
        if usuario is None:
            raise forms.ValidationError("¡Contraseña incorrecta!")
        return contraseña