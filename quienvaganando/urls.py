from django.urls import path
from . import views

urlpatterns = [
    path('torneos/<str:uuid_torneo>', views.overview_torneo, name='overview_torneo'),
]