from django import forms
from .models import User
from .models import Torneo, Partido
from django.db.models import Q
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
        # Comparación case-insensitive
        nombre_comp = nombre.lower()
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
    
class EditarParticipantesForm(forms.Form):
    
    # agrega campos dinámicos dependiendo de los participantes a editar
    def __init__(self, participantes, *args, **kwargs):
        
        super(EditarParticipantesForm, self).__init__(*args, **kwargs)
        
        for p in participantes:
            self.fields[p] = forms.CharField(max_length=250, label=p)
            
    def clean(self):
        cleaned_data = super().clean()
        participantes = cleaned_data.values()
        
        # revisar que no hayan participantes repetidos
        participantes_comp = [p.lower() for p in participantes]
        if len(participantes_comp) != len(set(participantes_comp)):
            raise forms.ValidationError("Hay participantes repetidos")

        return cleaned_data
 
class EliminarParticipantesForm(forms.Form):
    
    # agrega campos dinámicos dependiendo de los participantes a eliiminar
    def __init__(self, torneo, participantes, *args, **kwargs):
        
        super(EliminarParticipantesForm, self).__init__(*args, **kwargs)
        self.torneo = torneo
        
        for p in participantes:
            self.fields[p] = forms.BooleanField(required=False, label=f"¿Eliminar {p}?")
    
    def clean(self):
        cleaned_data = super().clean()
        
        # para poder eliminar elementos de cleaned data sin afectar la iteración
        cleaned_data_iter = cleaned_data.copy()
        
        # si el equipo a eliminar tiene partidos, se envía un error
        for nombre, eliminar in cleaned_data_iter.items():
            existen_partidos = (
                (Q(equipo_a__nombre = nombre) | Q(equipo_b__nombre = nombre))
                & Q(evento__torneo=self.torneo)
            )
            if eliminar and Partido.objects.filter(existen_partidos).exists():
                self.add_error(nombre, forms.ValidationError("No puedes eliminar un participante que tenga partidos"))
                
        return cleaned_data
        
    
class EditarTorneoForm(forms.ModelForm):
    class Meta:
        model = Torneo
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5})
            }
        help_texts = {
            'nombre': "Nombre del Torneo", 
            'descripcion': "Descripción del Torneo"
            }

        def clean_nombre(self):
            nombre = self.cleaned_data["nombre"]
            nombre_antiguo = self.instance.nombre.lower()
            # Comparación case-insensitive
            nombre_comp = nombre.lower()
            if nombre_antiguo != nombre_comp and Torneo.objects.filter(nombre__iexact=nombre_comp).exists():
                raise forms.ValidationError("¡Ya existe un torneo con este nombre!")   
            return nombre