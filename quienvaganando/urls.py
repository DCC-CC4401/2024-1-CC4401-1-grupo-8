from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login'),
    path('logout/',views.logout_user, name='logout'),
    path('torneos/', views.lista_torneos, name='torneos'),
    path('crear_torneo/', views.nuevo_torneo, name='creacion_torneo'),
    path('torneos/<str:uuid_torneo>/', views.overview_torneo, name='overview_torneo'),
    path('torneos/<str:uuid_torneo>/agregar_evento', views.agregar_evento, name='agregar_evento'),
    path('torneos/<str:uuid_torneo>/agregar_participante', views.agregar_participante, name='agregar_participante'),
    path('torneos/<str:uuid_torneo>/editar_participantes', views.editar_participantes, name='editar_participantes'),
    path('torneos/<str:uuid_torneo>/editar', views.editar_torneo, name='editar_torneo'),
    path('torneos/<str:uuid_torneo>/editar/eliminar_torneo/', views.eliminar_torneo, name='eliminar_torneo'),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>', views.overview_evento, name="overview_evento"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/eliminar/', views.eliminar_evento, name="eliminar_evento"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/<str:id_partido>/eliminar/', views.eliminar_partido, name="eliminar_partido"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/editar/', views.editar_evento, name="editar_evento"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/agregar_partido/', views.agregar_partido, name="agregar_partido"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/<str:id_partido>/editar/', views.editar_partido, name="editar_partido"),
]