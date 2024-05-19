from django.shortcuts import render
from quienvaganando.models import *
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from quienvaganando.forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum, Count, Window
from django.db.models.functions import Rank



def register_user(request):
    if request.method == 'GET': #Si estamos cargando la página
        form_register = RegisterForm()
        return render(request, "quienvaganando/register_user.html", {"form_register" : form_register}) #Mostrar el template

    elif request.method == 'POST':
        form_register = RegisterForm(request.POST)
        #Crear el nuevo usuario
        if form_register.is_valid():
            username = form_register.cleaned_data["username"]
            contraseña = form_register.cleaned_data["contraseña"]
            User.objects.create_user(username=username, password=contraseña)
            login_user(request)
            #Redireccionar al home
            return HttpResponseRedirect('/') # CAMBIAR RUTA
        else:
            return render(request, 'quienvaganando/register_user.html', {"form_register": form_register})
    
def login_user(request):
    if request.method == 'GET':
        form_login = LoginForm()
        return render(request,"quienvaganando/login.html", {"form_login": form_login})
    elif request.method == 'POST':
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            username = form_login.cleaned_data["username"]
            contraseña = form_login.cleaned_data["contraseña"]
            usuario = authenticate(username=username,password=contraseña)
            # si usuario is None, el formulario no es valido
            login(request,usuario)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'quienvaganando/login.html', {"form_login": form_login})
 
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def home(request):
    return HttpResponseRedirect('/torneos')


def lista_torneos(request):
    if request.user.is_authenticated:
        mis_torneos = Torneo.objects.filter(owner=request.user)
    else:
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