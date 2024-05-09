from django.shortcuts import render
from quienvaganando.models import *
from django.db.models import Q, F, Sum, Count, Window
from django.db.models.functions import Rank


def overview_torneo(request, uuid_torneo):
    
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    if request.method == "GET":
        
        # obtener lista de eventos del torneo
        nombres_eventos = (Evento.objects.filter(torneo=torneo)
            .values_list("nombre", flat=True).order_by("nombre"))
        
        # obtener todas las posiciones de este torneo
        posiciones = Posicion.objects.filter(evento__torneo=torneo)
        
        # sumar puntajes por equipo, contar lugares, agregar ranking
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
        
        # formatear resultados del diccionario a una lista de listas
        datos_tabla = []
        for dict in resultados:
            
            l = [dict["rank"]] + list(dict.values())[1:-1]
            datos_tabla.append(l)
        
        # obtener participantes sin ninguna posicion
        filtro_vacios = Q(torneo=torneo) & Q(posicion__isnull=True)
        participantes_vacios = (Participante.objects.filter(filtro_vacios)
            .values_list("nombre", flat=True)
        )
        
        # agregar participantes sin posicion a la tabla
        ultimo_lugar = len(datos_tabla)+1
        for participante in participantes_vacios:
            datos_tabla.append([ultimo_lugar, participante, 0, 0, 0, 0])
        
        
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
            "datos_tabla": datos_tabla
        })
