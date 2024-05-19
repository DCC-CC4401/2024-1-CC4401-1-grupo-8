from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register_user, name='register_user'),
    path('login', views.login_user, name='login'),
    path('logout',views.logout_user, name='logout'),
    path('torneos', views.lista_torneos, name='torneos'),
    path('crear_torneo', views.nuevo_torneo, name='creacion_torneo'),
    path('torneos/<str:uuid_torneo>', views.overview_torneo, name='overview_torneo'),
]