from django.urls import path
from . import views

urlpatterns = [
    path("", views.WalletPanelView.as_view(), name="wallet-panel"),
    path("add/", views.WalletCreateView.as_view(), name="wallet-add"),
    path("<int:pk>/delete/", views.WalletDeleteView.as_view(), name="wallet-delete"),
]