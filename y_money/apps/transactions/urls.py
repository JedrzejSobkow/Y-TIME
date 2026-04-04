from django.urls import path
from .views import TransactionCreateView, TransactionListView

urlpatterns = [
    path("add/", TransactionCreateView.as_view(), name="add-transaction"),
    path("wallet/<int:wallet_id>/", TransactionListView.as_view(), name="transaction-list"),

]