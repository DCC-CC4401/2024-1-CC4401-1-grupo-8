from django import forms
from .models import User
from .models import Torneo, Participante
from django.contrib.auth import authenticate
from django.forms import PasswordInput


class RegisterForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña", widget=PasswordInput(), help_text="La contraseña debe tener al menos 8 caracteres")

    def clean_username(self):
        username = self.cleaned_data["username"]
        username_l = username.lower()
        # comparacion case-insensitive
        if User.objects.filter(username__iexact=username_l).exists():
            raise forms.ValidationError("¡El nombre de usuario ya existe!")
        return username

    def clean_contraseña(self):
        contraseña = self.cleaned_data["contraseña"]
        # Validar largo de contraseñas
        if len(contraseña) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres")
        return contraseña

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    contraseña = forms.CharField(label="Contraseña", widget=PasswordInput())

    def clean(self):
        username = self.cleaned_data["username"]
        contraseña = self.cleaned_data["contraseña"]
        # Validar que no hay repetidos
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("¡El nombre de usuario no existe!")
        usuario = authenticate(username=username, password=contraseña)
        # Validar que el usuario es correcto
        if usuario is None:
            raise forms.ValidationError("¡Nombre de usuario o contraseña incorrecta!")
        return self.cleaned_data

class NuevoTorneoForm(forms.Form):
    nombre = forms.CharField(label="Nombre del Torneo", max_length=250)
    participantes = forms.CharField(widget=forms.Textarea(attrs={'rows':5}), help_text="Ingrese los nombres de los participantes separados por comas.")
    eventos = forms.CharField(widget=forms.Textarea(attrs={'rows':5}), help_text="Ingrese los nombres de los eventos separados por comas.")
    descripcion_eventos = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), help_text="Ingrese las descripciones de los eventos en el mismo orden, separados por comas.")

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        nombre_comp = nombre.lower()
        # Comparación case-insensitive
        if Torneo.objects.filter(nombre__iexact=nombre_comp).exists():
            raise forms.ValidationError("¡Ya existe un torneo con este nombre!")   
        return nombre
    
    def clean_participantes(self):
        participantes = self.cleaned_data["participantes"]
        participantes_list = [p.strip() for p in participantes.split(',') if p.strip()]
        # ver que no hay repetidos
        participantes_comp = list(map(lambda nombre: nombre.lower(), participantes_list))
        if len(participantes_comp) != len(set(participantes_comp)):
            raise forms.ValidationError("Hay participantes repetidos")
        
        return participantes_list
    
    def clean_eventos(self):
        eventos = self.cleaned_data["eventos"]
        eventos_list = [e.strip() for e in eventos.split(',') if e.strip()]
        # ver que no hay repetidos
        eventos_comp = list(map(lambda nombre: nombre.lower(), eventos_list))
        if len(eventos_comp) != len(set(eventos_comp)):
            raise forms.ValidationError("Hay eventos repetidos")
        return eventos_list
    
    def clean_descripcion_eventos(self):
        descripcion_eventos = self.cleaned_data["descripcion_eventos"]
        descripcion_list = [d.strip() for d in descripcion_eventos.split(',') if d.strip()]
        return descripcion_list
    
    def clean(self):
        cleaned_data = super().clean()
        eventos = cleaned_data.get("eventos")
        descripcion_eventos = cleaned_data.get("descripcion_eventos")
        # Ver que la cantidad de eventos y descripcones de eventos son iguales
        if eventos is not None and descripcion_eventos is not None:
            if len(eventos) != len(descripcion_eventos):
                raise forms.ValidationError("El número de eventos y descripciones debe coincidir.")
        return cleaned_data
    
class AgregarParticipanteForm(forms.Form):
    
    nombre = forms.CharField(max_length=250, label="Nombre")
    
    # inicialización para agregar el torneo actual como atributo
    def __init__(self, torneo, *args, **kwargs):
        super(AgregarParticipanteForm, self).__init__(*args, **kwargs)
        self.torneo = torneo
    
    def clean_nombre(self):
        
        nombre = self.cleaned_data.get("nombre")
        
        # revisa que el participante a agregar no exista
        if nombre.lower() in [p.nombre.lower() for p in Participante.objects.filter(torneo=self.torneo)]:
            raise forms.ValidationError("Ya existe un participante con este nombre")

        return nombre