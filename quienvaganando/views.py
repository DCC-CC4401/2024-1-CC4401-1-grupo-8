from django.shortcuts import render
from quienvaganando.models import User, Torneo, Participante, Evento
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from quienvaganando.forms import *
from django.contrib.auth.decorators import login_required
# Create your views here.

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

@login_required
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

            return HttpResponseRedirect('/') # CAMBIAR RUTA
        else:
            return render(request, 'quienvaganando/torneo.html', {"form": form})