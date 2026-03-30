from django.views.generic import CreateView, ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http.response import JsonResponse
from django.db import transaction
from .forms import TransactionForm, TransactionItemForm
from .models import TransactionItem
from apps.users.models import Profile
import json

class TransactionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        form = TransactionForm(profile=profile)
        return render(request, "transactions/transaction_create.html", {"form": form})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            profile = Profile.objects.get(user=request.user)
            form = TransactionForm(data, profile=profile)
            
            if not form.is_valid():
                return JsonResponse({
                    "success": False, 
                    "errors": form.errors
                    }, status=400)
            
            items_data = data.get("items", [])
            if not items_data:
                return JsonResponse({
                    "success": False,
                    "errors": {"items": ["Dodaj co najmniej jedną pozycję."]}
                }, status=400)
                
            item_forms = [TransactionItemForm(item) for item in items_data]
            item_forms = [TransactionItemForm(data=item) for item in items_data]
            item_errors = {}
            for i, item_form in enumerate(item_forms):
                if not item_form.is_valid():
                    item_errors[f"item_{i}"] = item_form.errors
                    
            if item_errors:
                return JsonResponse({
                    "success": False,
                    "errors": item_errors
                }, status=400)
                
            transaction_type = form.cleaned_data["type"]
            total = sum(item_form.cleaned_data["amount"] for item_form in item_forms)

            if transaction_type == "income" and total < 0:
                return JsonResponse({
                    "success": False,
                    "errors": {"items": ["Łączna kwota wpływu musi być nieujemna."]}
                }, status=400)

            if transaction_type == "expense" and total > 0:
                return JsonResponse({
                    "success": False,
                    "errors": {"items": ["Łączna kwota wydatku musi być niedodatnia."]}
                }, status=400)
            
            with transaction.atomic():
                new_transaction = form.save()
                
                TransactionItem.objects.bulk_create([
                    TransactionItem(
                        transaction = new_transaction,
                        name = item_form.cleaned_data["name"],
                        amount = item_form.cleaned_data["amount"],
                    )
                    for item_form in item_forms
                ])
                
            return JsonResponse({
                    "success": True,
                    "message": "Transakcja zapisana.",
                    "transaction_id": new_transaction.id,
                }, status=201)
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "errors": {"non_field": [str(e)]}
            }, status=400)