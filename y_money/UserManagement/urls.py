from django.urls import path
from UserManagement.views import test

urlpatterns = [
    path('', test, name="test-view")
]
