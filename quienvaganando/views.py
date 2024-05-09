from django.shortcuts import render
from quienvaganando import User

# Create your views here.
from django.http import HttpResponseRedirect

def register_user(request):
    if request.method == 'GET': #Si estamos cargando la página
     return render(request, "todoapp/register_user.html") #Mostrar el template

    elif request.method == 'POST': #Si estamos recibiendo el form de registro
     #Tomar los elementos del formulario que vienen en request.POST
     nombre = request.POST['nombre']
     contraseña = request.POST['contraseña']
    
     #Crear el nuevo usuario
     user = User.objects.create_user(username=nombre, password=contraseña)

     #Redireccionar la página /tareas
     return HttpResponseRedirect('/') # CAMBIAR RUTA