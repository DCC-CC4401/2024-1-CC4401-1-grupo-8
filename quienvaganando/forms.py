from django import forms
from .models import User
from .models import Torneo, Evento, Participante, Partido
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
    descripcion_eventos = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), help_text="Ingrese las descripciones de los eventos en el mismo orden, separados por comas.", required=False, label="(Opcional) Descripción de los eventos")

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
        if eventos is not None and descripcion_eventos is not None and len(descripcion_eventos)!=0:
            if len(eventos) != len(descripcion_eventos):
                raise forms.ValidationError("El número de eventos y descripciones debe coincidir.")
        return cleaned_data

class AgregarEventoForm(forms.Form):
    nombre = forms.CharField(max_length=250, label="Nombre")
    descripcion = forms.CharField(required=False, label="Descripción")

    # inicialización para agregar el torneo actual como atributo
    def __init__(self, torneo, *args, **kwargs):
        super(AgregarEventoForm, self).__init__(*args, **kwargs)
        self.torneo = torneo
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        # revisa que el participante a agregar no exista
        if nombre.lower() in [e.nombre.lower() for e in Evento.objects.filter(torneo=self.torneo)]:
            raise forms.ValidationError("Ya existe un evento con este nombre")
        return nombre
    
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
    
class EditarEventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre del Evento',
            'descripcion': 'Descripción del Evento'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3})
        }
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        evento_id = self.instance.id  
        torneo_id = self.instance.torneo.id  
        
        
        if Evento.objects.filter(nombre__iexact=nombre, torneo_id=torneo_id).exclude(id=evento_id).exists():
            raise forms.ValidationError("Ya existe un evento con este nombre en el mismo torneo.")
        
        return nombre

    

class AgregarPartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['equipo_a', 'equipo_b', 'categoria', 'fecha', 'hora', 'lugar']
        labels = {
            'equipo_a': 'Nombre del equipo A',
            'equipo_b': 'Nombre del equipo B',
            'categoria': 'Categoría',
            'fecha': 'Fecha del partido',
            'hora': 'Hora del partido',
            'lugar': 'Lugar del partido'
        }

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'campo_extra_a': forms.Textarea(attrs={'rows': 3}),
            'campo_extra_b': forms.Textarea(attrs={'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        torneo_id = kwargs.pop('torneo_id', None)
        super().__init__(*args, **kwargs)
        if torneo_id:
            self.fields['equipo_a'].queryset = Participante.objects.filter(torneo_id=torneo_id)
            self.fields['equipo_b'].queryset = Participante.objects.filter(torneo_id=torneo_id)
        self.fields['categoria'].required = True
        self.fields['fecha'].required = True
        self.fields['hora'].required = True
        self.fields['lugar'].required = True    

    def clean(self):
        cleaned_data = super().clean()
        equipo_a = cleaned_data.get('equipo_a')
        equipo_b = cleaned_data.get('equipo_b')

        if equipo_a and equipo_b and equipo_a == equipo_b:
            raise forms.ValidationError("Los equipos no pueden ser iguales.")

        return cleaned_data
    
    
class EditarPartidoForm(forms.ModelForm):   
    class Meta:
        model = Partido
        fields = ['equipo_a', 'equipo_b', 'fecha', 'hora', 'lugar', 'resultado_a', 'resultado_b', 'campo_extra_a', 'campo_extra_b', 'categoria']
        labels = {
                'equipo_a': 'Nombre del Equipo A',
                'equipo_b': 'Nombre del Equipo B',
                'fecha': 'Fecha del Evento',
                'hora': 'Hora del Evento',
                'lugar': 'Lugar del Evento',
                'resultado_a': 'Resultado del Equipo A',
                'resultado_b': 'Resultado del Equipo B',
                'campo_extra_a': 'Campo Extra A',
                'campo_extra_b': 'Campo Extra B',
                'categoria': 'Categoria'
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'campo_extra_a': forms.Textarea(attrs={'rows': 3}),
            'campo_extra_b': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        id_torneo = kwargs.pop('id_torneo', None)
        super().__init__(*args, **kwargs)

        if id_torneo:
            self.fields['equipo_a'].queryset = Participante.objects.filter(torneo_id=id_torneo)
            self.fields['equipo_b'].queryset = Participante.objects.filter(torneo_id=id_torneo)

        if self.instance and self.instance.pk:
            if self.instance.fecha:
                self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%d')
            if self.instance.hora:
                self.fields['hora'].initial = self.instance.hora.strftime('%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        equipo_a = cleaned_data.get('equipo_a')
        equipo_b = cleaned_data.get('equipo_b')

        if equipo_a and equipo_b and equipo_a == equipo_b:
            raise forms.ValidationError("Los equipos no pueden ser iguales.")

        return cleaned_data

class EditarPuntajesForm(forms.Form):
    
    posicion = forms.IntegerField(min_value=1, required=False, label="Posición")
    puntaje = forms.IntegerField(min_value=0, required=False, label="Puntaje")

    def clean(self):
        cleaned_data = super().clean()
        posicion = cleaned_data.get('posicion')
        puntaje = cleaned_data.get('puntaje')

        if posicion is not None and puntaje is None:
            raise forms.ValidationError("Toda posición debe tener un puntaje asociado.")

        if puntaje is not None and posicion is None:
            raise forms.ValidationError("Todo puntaje debe tener una posición asociada.")

        return cleaned_data