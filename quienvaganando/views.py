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
            messages.success(request, "Usuario creado exitosamente.")
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
            messages.success(request, f"Hola, {username}!")
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
            messages.success(request, "Torneo creado exitosamente.")
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

        # Obtener los eventos del torneo
        eventos_torneo = Evento.objects.filter(torneo=torneo)

        # Filtrar los partidos futuros y los de hoy en adelante
        prox1 = Partido.objects.filter(evento__in=eventos_torneo).filter(fecha__gt=date.today())
        prox2 = Partido.objects.filter(evento__in=eventos_torneo).filter(fecha=date.today()).filter(hora__gte=datetime.now().time())
        
        # Combinar ambas consultas y ordenar los resultados
        partidos_proximos = (prox1 | prox2).values("fecha", "hora", "lugar", "categoria",
                                                   nombre_evento=F("evento__nombre"),
                                                   nombre_equipo_a=F("equipo_a__nombre"),
                                                   nombre_equipo_b=F("equipo_b__nombre")).order_by("fecha", "hora")[:5]
        
        # verificar si el usuario es dueño del torneo, para mostrar botones de edición
        es_dueno = (request.user.is_authenticated and request.user == torneo.owner)

        # Renderiza la plantilla overview_torneo.html, pasando los datos calculados y obtenidos de
        # las consultas
        return render(request, "quienvaganando/overview_torneo.html", {
            "torneo": torneo,
            "eventos": nombres_eventos,
            "header_tabla": ["Pos.", "Equipo", "1°", "2°", "3°", "Ptje."],
            "proximos_partidos": partidos_proximos,
            "datos_tabla": datos_tabla,
            "es_dueno": es_dueno,
        })
        
def editar_participantes(request, uuid_torneo):
    
    # se obtiene el torneo y sus participantes
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    # si el usuario no es dueño, entrega error
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    
    participantes = Participante.objects.filter(torneo=torneo)
    nombres_participantes = [p.nombre for p in participantes]
    
    
    if request.method == "GET":
        # diccionario con nombres actuales (para que sean fácilmente editables en el form)
        info_actual = dict(zip(
            ["editar-" + nombre for nombre in nombres_participantes],
            nombres_participantes
        ))
        
        form_editar = EditarParticipantesForm(nombres_participantes, info_actual, prefix="editar")
        form_eliminar = EliminarParticipantesForm(torneo, nombres_participantes, prefix="eliminar")
        return render(request,  "quienvaganando/editar_participantes.html", {
            "torneo": torneo,
            "form_editar": form_editar,
            "form_eliminar": form_eliminar
        })
    
    if request.method == "POST":
        form_editar = EditarParticipantesForm(nombres_participantes, request.POST, prefix="editar")
        form_eliminar = EliminarParticipantesForm(torneo, nombres_participantes, request.POST, prefix="eliminar")
        
        # validar forms
        if form_editar.is_valid() and form_eliminar.is_valid():
            
            # cambiar nombres de participantes
            for p, nombre in zip(participantes, form_editar.cleaned_data.values()):
                p.nombre = nombre
                p.save()
            
            # eliminar participantes seleccionados
            for p, eliminar in zip(participantes, form_eliminar.cleaned_data.values()):
                if eliminar:
                    p.delete()
                
            return HttpResponseRedirect(f"/torneos/{uuid_torneo}")
        
        return render(request,  "quienvaganando/editar_participantes.html", {
            "form_editar": form_editar,
            "form_eliminar": form_eliminar,
        })

def editar_torneo(request, uuid_torneo):
    
    # Se obtiene el objeto torneo con la id uuid_torneo
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    # si el usuario no es dueño, entrega error
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    
    if request.method == "GET":
        form = EditarTorneoForm(instance=torneo)
        return render(request, "quienvaganando/editar_torneo.html", {"form": form, "uuid_torneo": uuid_torneo})
    if request.method == "POST":    
        form = EditarTorneoForm(request.POST, instance=torneo)
        # Se revisa la validez del form.
        # En caso de que lo sea, se obtiene el nuevo nombre y descripción para el torneo
        # Se reemplazan los antiguos nombre y descripción
        # Se guarda la información
        if form.is_valid():
            nuevo_nombre = form.cleaned_data['nombre']
            nueva_descripcion = form.cleaned_data['descripcion']
            torneo.nombre = nuevo_nombre
            torneo.descripcion = nueva_descripcion
            torneo.save()
            return HttpResponseRedirect(f"/torneos/{uuid_torneo}")
        return render(request, "quienvaganando/editar_torneo.html", {"form": form, "uuid_torneo": uuid_torneo})

def eliminar_torneo(request, uuid_torneo):
    
    torneo = get_object_or_404(Torneo, uuid=uuid_torneo)
    
    # si el usuario no es dueño, entrega error
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    
    if request.method == "POST":
        torneo.delete()
        messages.success(request, "Torneo eliminado correctamente")
        return redirect('home')
    else:
        return render(request, 'quienvaganando/eliminar_torneo.html', {'torneo': torneo})

      
def agregar_participante(request, uuid_torneo):
    
    # se obtiene el torneo y sus participantes
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    # si el usuario no es dueño, entrega error
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    
    
    if request.method == "GET":
        form = AgregarParticipanteForm(torneo)
        return render(request,  "quienvaganando/agregar_participante.html", {"form": form})
    
    if request.method == "POST":    
        form = AgregarParticipanteForm(torneo, request.POST)
        
        # validar form y agregar participante
        if form.is_valid():
            nombre = form.cleaned_data.get("nombre")
            Participante.objects.create(
                nombre=nombre,
                torneo=torneo
            )
            return HttpResponseRedirect(f"/torneos/{uuid_torneo}")

        return render(request,  "quienvaganando/agregar_participante.html", {"form": form})

def agregar_evento(request, uuid_torneo):

    # se obtiene el torneo y sus participantes
    torneo = Torneo.objects.get(uuid=uuid_torneo)

    # si el usuario no es dueño, entrega error
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied


    if request.method == "GET":
        form = AgregarEventoForm(torneo)
        return render(request, "quienvaganando/agregar_evento.html", {"form": form})

    if request.method == "POST":    
        form = AgregarEventoForm(torneo, request.POST)

        # validar form y agregar evento
        if form.is_valid():
            nombre = form.cleaned_data.get("nombre")
            descripcion = form.cleaned_data.get("descripcion")
            Evento.objects.create(
                nombre=nombre,
                descripcion = descripcion,
                torneo=torneo
            )
            return HttpResponseRedirect(f"/torneos/{uuid_torneo}")

        return render(request,  "quienvaganando/agregar_evento.html", {"form": form})

    
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

@login_required
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
    
@login_required
def editar_evento(request, uuid_torneo, nombre_evento):
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    #evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        form = EditarEventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirige a la página principal o a donde desees
    else:
        form = EditarEventoForm(instance=evento)

    return render(request, 'quienvaganando/editar_evento.html', {'form': form, "uuid_torneo": uuid_torneo, "nombre_evento":nombre_evento})
   
@login_required
def agregar_partido(request, uuid_torneo, nombre_evento):
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    torneo_id = evento.torneo.id
    
    if request.method == 'GET':
        form = AgregarPartidoForm(torneo_id=torneo_id)
        return render(request, "quienvaganando/agregar_partido.html", {"form": form, "uuid_torneo": uuid_torneo, "nombre_evento":nombre_evento})
    
    elif request.method == 'POST':
        form = AgregarPartidoForm(request.POST, torneo_id=torneo_id)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.evento = evento
            partido.save()
            return redirect('home')
        else:
            return render(request, 'quienvaganando/agregar_partido.html', {"form": form, "uuid_torneo": uuid_torneo, "nombre_evento":nombre_evento})
        
@login_required
def editar_partido(request, uuid_torneo, nombre_evento, id_partido):
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    id_torneo = evento.torneo.id  # Asumiendo que Evento tiene una relación con Torneo
    partido = get_object_or_404(Partido, id=id_partido)
    ### 
    if request.method == 'POST':
        form = EditarPartidoForm(request.POST, instance=partido, id_torneo=id_torneo)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EditarPartidoForm(instance=partido, id_torneo=id_torneo)
    
    return render(request, 'quienvaganando/editar_partido.html', {'form': form})


@login_required
def eliminar_partido(request, uuid_torneo, nombre_evento, id_partido):
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    evento = get_object_or_404(Evento, torneo__uuid=uuid_torneo, nombre=nombre_evento)
    partido = get_object_or_404(Partido, id=id_partido, evento_id=evento.id)
    if not (request.user.is_authenticated and request.user == torneo.owner):
        raise PermissionDenied
    partido.delete()
    messages.success(request, "Partido eliminado correctamente")
    return redirect('overview_evento', uuid_torneo=uuid_torneo, nombre_evento=nombre_evento)

