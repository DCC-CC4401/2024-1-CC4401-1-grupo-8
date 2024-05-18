from django.shortcuts import render
from quienvaganando.models import *
from django.db.models import Q, F, Sum, Count, Window
from django.db.models.functions import Rank


def overview_torneo(request, uuid_torneo):
    # Se obtiene el objeto torneo con la id uuid_torneo
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    if request.method == "GET":
        # Las siguientes consultas tienen como objetivo entregar la tabla de posiciones global del torneo a la plantilla  overview_torneo.html 
        # En particular, se clasificaran los participantes por puntaje, donde este puntaje asociado es la suma de los puntajes conseguidos en los eventos particulares del torneo
        # Se entregaran datos extra utiles como la cantidad de primeros, segundos, o terceros puestos obtenidos por los participantes en los distintos eventos del torneo
        
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
        
        
        # Renderiza la plantilla overview_torneo.html, pasando los datos calculados y obtenidos de las consultas
        return render(request, "quienvaganando/overview_torneo.html", {
            "nombre": torneo.nombre,
            "eventos": nombres_eventos,
            "header_tabla": ["Pos.", "Equipo", "1°", "2°", "3°", "Ptje."],
            "datos_tabla": datos_tabla
        })
