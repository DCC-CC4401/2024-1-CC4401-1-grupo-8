from django.shortcuts import render, get_object_or_404, redirect
from quienvaganando.models import *
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from quienvaganando.forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum, Count, Window, ExpressionWrapper, fields
from django.db.models.functions import Rank
from datetime import date, datetime
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied



def register_user(request):
    if request.method == 'GET': 
        # Si estamos cargando la página, mostrar el formulario de registro
        form_register = RegisterForm() 
        # Mostrar el template
        return render(request, "quienvaganando/register_user.html", {"form_register" : form_register}) 

    elif request.method == 'POST':
        # Recibir los datos en el formulario
        form_register = RegisterForm(request.POST)
        # Validar y crear el nuevo usuario
        if form_register.is_valid():
            username = form_register.cleaned_data["username"]
            contraseña = form_register.cleaned_data["contraseña"]
            User.objects.create_user(username=username, password=contraseña)
            login_user(request)
            # Redireccionar al home
            return HttpResponseRedirect('/') # CAMBIAR RUTA
        else:
            # Si no pasa la validación, se devuelve el formulario con los datos
            return render(request, 'quienvaganando/register_user.html', {"form_register": form_register})
    
def login_user(request):
    if request.method == 'GET':
        # Si estamos cargando la página, mostrar el formulario de login
        form_login = LoginForm()
        # Mostrar el template
        return render(request,"quienvaganando/login.html", {"form_login": form_login})
    elif request.method == 'POST':
        # Recibir los datos en el formulario
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            username = form_login.cleaned_data["username"]
            contraseña = form_login.cleaned_data["contraseña"]
            # La autentifiación del usuario se hacer para obtener el usuario,
            # pero sino es válido, se arroja un error en forms.LoginForm
            usuario = authenticate(username=username,password=contraseña)
            login(request,usuario)
            # Si el formulario es válido, retornamos al home
            return HttpResponseRedirect('/')
        else:
            # Si el usuario no es valido, se devuelve el formulario con los datos
            return render(request, 'quienvaganando/login.html', {"form_login": form_login})
 
def logout_user(request):
    logout(request)
    # Se cierra sesión y se envía al home
    return HttpResponseRedirect('/')

def home(request):
    # La ruta '/' debe redireccionar a '/torneos'
    return HttpResponseRedirect('/torneos')


def lista_torneos(request):
    if request.user.is_authenticated:
        # El usuario verá los torneos que ha creado
        mis_torneos = Torneo.objects.filter(owner=request.user)
    else:
        # Si no está autentificado, verá torneos sin dueño
        mis_torneos = Torneo.objects.filter(owner=None)
    return render(request, 'quienvaganando/lista_torneos.html', {"mis_torneos": mis_torneos})

@login_required(login_url="/login")
def nuevo_torneo(request):
    if request.method == 'GET': #Si estamos cargando la página
        form = NuevoTorneoForm()
        return render(request, "quienvaganando/torneo.html", {"form" : form}) #Mostrar el template
    elif request.method == 'POST':
        form = NuevoTorneoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            participantes = form.cleaned_data['participantes']
            eventos = form.cleaned_data['eventos']
            descripcion_eventos = form.cleaned_data['descripcion_eventos']

            # Crear el objeto Torneo y guardarlo en la base de datos
            torneo = Torneo.objects.create(
                nombre=nombre,
                owner=request.user
            )

            # Crear objetos Participante
            for participante in participantes:
                Participante.objects.create(
                    nombre=participante,
                    torneo=torneo
                )

            # Crear objetos Evento
            for nombre_evento, descripcion in zip(eventos, descripcion_eventos):
                Evento.objects.create(
                    nombre=nombre_evento,
                    descripcion=descripcion,
                    torneo=torneo
                )

            return HttpResponseRedirect('/')
        else:
            return render(request, 'quienvaganando/torneo.html', {"form": form})
        


def overview_torneo(request, uuid_torneo):
        
    # Se obtiene el objeto torneo con la id uuid_torneo
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    if request.method == "GET":
        # Las siguientes consultas tienen como objetivo entregar la tabla de posiciones global del
        # torneo a la plantilla overview_torneo.html
        # En particular, se clasificaran los participantes por puntaje, donde este puntaje asociado
        # es la suma de los puntajes conseguidos en los eventos particulares del torneo
        # Se entregaran datos extra utiles como la cantidad de primeros, segundos, o terceros
        # puestos obtenidos por los participantes en los distintos eventos del torneo
        
        # Obtener lista de eventos del torneo
        nombres_eventos = (Evento.objects.filter(torneo=torneo)
            .values_list("nombre", flat=True).order_by("nombre"))
        
        # Obtener todas las posiciones de este torneo
        posiciones = Posicion.objects.filter(evento__torneo=torneo)
        
        # Sumar puntajes por equipo, contar lugares, agregar ranking
        resultados = (posiciones.values("participante", nombre=F("participante__nombre"))
            .annotate(primeros_lugares=Count("posicion", filter=Q(posicion=1)))
            .annotate(segundos_lugares=Count("posicion", filter=Q(posicion=2)))
            .annotate(terceros_lugares=Count("posicion", filter=Q(posicion=3)))
            .annotate(puntos=Sum("puntaje"))
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F('puntos').desc(),
                )
            )
        )
        
        # Formatear resultados del diccionario a una lista de listas y empezamos a crear la tabla
        datos_tabla = []
        for dict in resultados:
            
            # Para dejar la posición al principio, luego todos los otros elementos excepto la ID
            # del participante y la posición (que ya fue agregada)
            l = [dict["rank"]] + list(dict.values())[1:-1]
            datos_tabla.append(l)
        
        # Obtener participantes sin ninguna posicion
        filtro_vacios = Q(torneo=torneo) & Q(posicion__isnull=True)
        participantes_vacios = (Participante.objects.filter(filtro_vacios)
            .values_list("nombre", flat=True)
        )
        
        # Agregar participantes sin posicion a la tabla
        ultimo_lugar = len(datos_tabla)+1
        for participante in participantes_vacios:
            datos_tabla.append([ultimo_lugar, participante, 0, 0, 0, 0])
        
        
        # Renderiza la plantilla overview_torneo.html, pasando los datos calculados y obtenidos de
        # las consultas
        return render(request, "quienvaganando/overview_torneo.html", {
            "nombre": torneo.nombre,
            "eventos": nombres_eventos,
            "header_tabla": ["Pos.", "Equipo", "1°", "2°", "3°", "Ptje."],
            "datos_tabla": datos_tabla
        })
    
def overview_evento(request, uuid_torneo, nombre_evento):
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    evento = Evento.objects.get(nombre=nombre_evento, torneo=torneo)

    if request.method == "GET":
        # Solo el owner puede modificar el torneo
        is_owner = (torneo.owner == request.user)
        # Query para tabla de posiciones
        posiciones = Posicion.objects.filter(evento=evento.id).values_list().order_by("posicion")\
            .values("posicion", "puntaje", nombre=F("participante__nombre"))
        
        # Query partidos pasados
        pas1 = Partido.objects.filter(evento=evento.id).filter(fecha__lt=date.today())
        pas2 = Partido.objects.filter(evento=evento.id).filter(fecha=date.today()).filter(hora__lt=datetime.now())
        partidos_pasados = (pas1|pas2).values("id", "fecha", "categoria", "resultado_a", "resultado_b", "campo_extra_a", "campo_extra_b",
                                          nombre_equipo_a=F("equipo_a__nombre"), nombre_equipo_b=F("equipo_b__nombre")).order_by("-fecha", "-hora")
        # print(partidos_pasados)

        # Query partidos proximos
        prox1 = Partido.objects.filter(evento=evento.id).filter(fecha__gt=date.today())
        prox2 = Partido.objects.filter(evento=evento.id).filter(fecha=date.today()).filter(hora__gte=datetime.now())
        partidos_proximos = (prox1|prox2).values("id", "fecha", "hora", "lugar", "categoria", nombre_equipo_a=F("equipo_a__nombre"),
                                                  nombre_equipo_b=F("equipo_b__nombre")).order_by("fecha", "hora")
    
        return render(request, "quienvaganando/overview_evento.html", {
            "nombre_torneo": torneo.nombre,
            "nombre_evento": evento.nombre,
            "descripcion": evento.descripcion,
            "posiciones": posiciones,
            "descripcion": evento.descripcion,
            "partidos_pasados": partidos_pasados,
            "partidos_proximos": partidos_proximos,
            "is_owner": is_owner,
            "uuid_torneo": torneo.uuid
        })

def eliminar_evento(request, uuid_torneo, nombre_evento):
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento eliminado correctamente")
        return redirect('overview_torneo', uuid_torneo=uuid_torneo)
    else:
        return render(request, 'quienvaganando/eliminar_evento.html', {'evento': evento})
   
def eliminar_partido(request, uuid_torneo, nombre_evento, id_partido):
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    partido = get_object_or_404(Partido, id=id_partido, evento_id=evento.id)
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    partido.delete()
    messages.succes(request, "Partido eliminado correctamente")
    return redirect('overview_evento', uuid_torneo=uuid_torneo, nombre_evento=nombre_evento)