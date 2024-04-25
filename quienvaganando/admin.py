from django.contrib import admin
from quienvaganando.models import User, Torneo, Evento, Participante, Posicion, Partido

admin.site.register(User)
admin.site.register(Torneo)
admin.site.register(Evento)
admin.site.register(Participante)
admin.site.register(Posicion)
admin.site.register(Partido)