from django.shortcuts import render
from quienvaganando.models import *
from django.db.models import Q, Sum, Count


def overview_torneo(request, uuid_torneo):
    
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    if request.method == "GET":
        
        # obtener lista de eventos del torneo
        
        eventos = Evento.objects.filter(torneo=torneo)
        nombres_eventos = [e.nombre for e in eventos]
        
        participantes = Participante.objects.filter(torneo=torneo)
        print([p.nombre for p in participantes])
        
        posiciones = Posicion.objects.filter(evento__torneo=torneo)
        
        print([(p.participante, p.posicion, p.puntaje) for p in posiciones])

        
        resultados = (posiciones.values("participante__nombre")
            .annotate(primeros_lugares=Count(Q(posicion=1)))
            .annotate(segundos_lugares=Count(Q(posicion=2)))
            .annotate(terceros_lugares=Count(Q(posicion=3)))
            .annotate(puntos=Sum("puntaje"))
            .order_by("puntos")
        )
        
        print(resultados)
        
        # obtener tabla de posiciones ??
        # - obtener posiciones cuyos eventos sean del torneo ✅
        # - agrupar por equipo, sumar puntos
        # -- contar primeros, segundos y terceros lugares (opcional?)
        # - ordenar segun puntajes
        
        # SELECT RANK, nombre_equipo, COUNT(1°), COUNT(2°), COUNT(3°), SUM(puntaje)
        # FROM posiciones
        # GROUP BY equipo
        # ORDER BY puntaje
        
        # dcc, valorant, 1er lugar, 1000 puntos
        # fias, valorant, 2do lugar, 500 puntos
        # ...
        
        return render(request, "quienvaganando/overview_torneo.html", {
            "nombre": torneo.nombre,
            "eventos": nombres_eventos,
            "header_tabla": ["Pos.", "Equipo", "1°", "2°", "3°", "Ptje."],
            "datos_tabla": [
                [1, "DCC", 2, 1, 3, 4000],
                [2, "FIAS", 1, 0, 0, 200]
            ]
        })
