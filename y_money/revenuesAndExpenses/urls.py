from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.addRevenueOrExpenseView, name='add-revenue-or-expense')
]