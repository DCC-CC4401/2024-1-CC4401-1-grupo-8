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
    path('torneos/<str:uuid_torneo>/<str:nombre_evento>/<str:id_partido>/eliminar/', views.eliminar_partido, name="eliminar_partido"),
]