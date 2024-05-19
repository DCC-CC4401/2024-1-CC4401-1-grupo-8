from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

class User(AbstractUser):
    pass
    
class Torneo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=250)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self): return self.nombre

class Evento(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    
    def __str__(self): return f"{self.nombre} - {self.torneo}"
    
class Participante(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250)
    
    def __str__(self): return f"{self.nombre} - {self.torneo}"
    
class Posicion(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    posicion = models.IntegerField(blank=True)  # es necesario?
    puntaje = models.IntegerField(blank=True)
    
    def __str__(self): return f"{self.participante.nombre} - {self.evento}"

class Partido(models.Model):
    equipo_a = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='equipo_a')
    equipo_b = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='equipo_b')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    # faltan los otros atributos de un partido