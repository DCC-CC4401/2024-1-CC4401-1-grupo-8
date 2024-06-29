from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

# Modelo de usuario que extiende AbstractUser
class User(AbstractUser):
    pass
 
 # Las siguientes clases definen que atributos y relaciones tendrán los objetos de la base de datos:


class Torneo(models.Model):
    # Id del torneo creada con uuid
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
     # Nombre del torneo
    nombre = models.CharField(max_length=250)
    # Creador\dueño, esta relacionado con el usuario User
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
     # Metodo para representar el objeto torneo como una cadena de texto, en este caso por su nombre
    def __str__(self): return self.nombre


class Evento(models.Model):
    # Relacion del evento con el torneo
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    # Nombre del evento
    nombre = models.CharField(max_length=250)
    #Descripcion del evento
    descripcion = models.TextField(blank=True)
    # Metodo para representar el objeto torneo como una cadena de texto, en este caso por su nombre y torneo asociado
    def __str__(self): return f"{self.nombre} - {self.torneo}"


class Participante(models.Model):
    # Relacion entre participante y torneo
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    # Nombre del participante
    nombre = models.CharField(max_length=250)
    # Metodo para representar el objeto torneo como una cadena de texto, en este caso por su nombre y torneo asociado
    def __str__(self): return f"{self.nombre} - {self.torneo}"


class Posicion(models.Model):
    # Relacion entre evento y posicion
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    # Relacion entre evento y participante
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    # Posicion del participante en el torneo
    posicion = models.IntegerField(blank=True)  
    # Puntaje del participante en el torneo
    puntaje = models.IntegerField(blank=True)
     # Metodo para representar el objeto torneo como una cadena de texto, en este caso por el nombre del participante y evento asociado
    def __str__(self): return f"{self.participante.nombre} - {self.evento}"

# Esta clase define los atributos que tiene un objeto partido
class Partido(models.Model):
    # Relacion entre partido y el equipo a
    equipo_a = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='equipo_a')
    # Relacion entre partido y el equipo b
    equipo_b = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='equipo_b')
    
    # Relacion entre partido y evento
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    
    # fecha hora y lugar de un partido
    fecha = models.DateField(blank=True)
    hora = models.TimeField(blank=True)
    lugar = models.CharField(blank=True, max_length=250)
    
    resultado_a = models.CharField(blank=True, max_length=250)
    resultado_b = models.CharField(blank=True, max_length=250)
    
    # opcional por si hay más de un participante
    campo_extra_a = models.CharField(blank=True, max_length=250)
    campo_extra_b = models.CharField(blank=True, max_length=250)
    
    # categoría (ej. final, primera ronda)
    categoria = models.CharField(blank=True, max_length=250)