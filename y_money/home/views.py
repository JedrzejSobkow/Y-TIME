from django.shortcuts import render
from django.http import HttpResponse

def homeDashboard(request):
    return render(request, 'home/homePage.html')