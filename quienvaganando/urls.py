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
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>', views.overview_evento, name="overview_evento"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/eliminar/', views.eliminar_evento, name="eliminar_evento"),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/editar/', views.editar_evento, name="editar_evento"),#path('evento/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/agregar_partido/', views.agregar_partido, name="agregar_partido"),#path('agregar_partido/<int:evento_id>', views.agregar_partido, name='agregar_partido'),
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/<str:uuid_partido>/', views.eliminar_evento, name="eliminar_evento")#path('editar_partido/<int:id_torneo>/<int:id_evento>/<int:partido_id>/', views.editar_partido, name='editar_partido/')
]