from django.urls import path

from . import views

urlpatterns = [
    path('', view=views.homeDashboard, name='home-dashboard')
]