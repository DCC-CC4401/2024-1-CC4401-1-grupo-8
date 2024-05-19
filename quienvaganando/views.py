from django.shortcuts import render
from quienvaganando.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login,logout
# Create your views here.

def register_user(request):
    if request.method == 'GET': #Si estamos cargando la página
     return render(request, "quienvaganando/register_user.html") #Mostrar el template

    elif request.method == 'POST': #Si estamos recibiendo el form de registro
     #Tomar los elementos del formulario que vienen en request.POST
     nombre = request.POST['nombre']
     contraseña = request.POST['contraseña']
    
     #Crear el nuevo usuario
     user = User.objects.create_user(username=nombre, password=contraseña)

     #Redireccionar la página /tareas
     return HttpResponseRedirect('/') # CAMBIAR RUTA
    
def login_user(request):
    if request.method == 'GET':
        return render(request,"quienvaganando/login.html")
    if request.method == 'POST':
        username = request.POST['username']
        contraseña = request.POST['contraseña']
        usuario = authenticate(username=username,password=contraseña)
        if usuario is not None:
            login(request,usuario)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/register')
        
 
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def home(request):
    return render(request, "quienvaganando/home.html")