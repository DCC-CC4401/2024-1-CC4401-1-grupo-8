from django.shortcuts import render
from quienvaganando.models import *


def overview_torneo(request, uuid_torneo):
    
    torneo = Torneo.objects.get(uuid=uuid_torneo)
    
    # 
    
    if request.method == "GET":
        return render(request, "quienvaganando/overview_torneo.html", {
            "nombre": torneo.nombre,
            "eventos": [],
            "header_tabla": ["Pos.", "Equipo", "1°", "2°", "3°", "Ptje."],
            "datos_tabla": [
                {1, "DCC", 2, 1, 3, 4000},
                {2, "FIAS", 1, 0, 0, 200}
            ]
        })
