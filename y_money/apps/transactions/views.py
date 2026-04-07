from django.views.generic import CreateView, ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http.response import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .forms import TransactionForm, TransactionItemForm
from .models import TransactionItem, Transaction
from apps.users.models import Profile
from apps.wallets.models import Wallet

import json

class TransactionCreateView(LoginRequiredMixin, View):
    def get(self, request, wallet_id=None):
        profile = Profile.objects.get(user=request.user)
        
        initial_data = {}
        if wallet_id:
            wallet = get_object_or_404(Wallet, pk=wallet_id, owner=profile)
            initial_data['wallet'] = wallet
            
        form = TransactionForm(profile=profile, initial=initial_data)
        
        wallets = Wallet.objects.filter(owner=profile).only("id", "currency")
        wallet_currencies = {str(w.id): w.currency.upper() for w in wallets}

        transfer_wallet_options = [
            {
                "id": w.id,
                "name": w.name,
                "currency": w.currency.upper(),
            }
            for w in Wallet.objects.filter(owner=profile).only("id", "name", "currency")
        ]

        friend_profiles = profile.get_friends().select_related("user")
        friend_transfer_options = []
        friend_default_wallet_map = {}
        for friend in friend_profiles:
            has_default_wallet = friend.wallets.filter(is_default=True, is_active=True).exists()
            label_base = friend.user.get_full_name().strip() or friend.user.username
            if has_default_wallet:
                label = label_base
            else:
                label = f"{label_base} (brak domyslnego portfela)"

            friend_transfer_options.append(
                {
                    "id": friend.id,
                    "label": label,
                    "has_default_wallet": has_default_wallet,
                }
            )
            friend_default_wallet_map[str(friend.id)] = has_default_wallet

        return render(
            request, 
            "transactions/transaction_create.html", 
            {
                "form": form,
                "wallet_currencies_json": json.dumps(wallet_currencies),
                "transfer_wallet_options": transfer_wallet_options,
                "friend_transfer_options": friend_transfer_options,
                "friend_default_wallet_map_json": json.dumps(friend_default_wallet_map),
            },
        )
    
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

            recipient_wallet = None
            recipient_friend = None
            transfer_mode = None

            if transaction_type == Transaction.TransactionType.TRANSFER:
                transfer_mode = data.get("transfer_mode")

                if transfer_mode not in Transaction.TransferMode.values:
                    return JsonResponse(
                        {
                            "success": False,
                            "errors": {"transfer_mode": ["Wybierz typ przelewu."]},
                        },
                        status=400,
                    )

                source_wallet = form.cleaned_data["wallet"]

                if transfer_mode == Transaction.TransferMode.INTERNAL:
                    recipient_wallet_id = data.get("recipient_wallet")
                    if not recipient_wallet_id:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {"recipient_wallet": ["Wybierz portfel odbiorcy."]},
                            },
                            status=400,
                        )

                    try:
                        recipient_wallet = Wallet.objects.get(id=recipient_wallet_id, owner=profile)
                    except Wallet.DoesNotExist:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {"recipient_wallet": ["Wybrany portfel odbiorcy nie istnieje."]},
                            },
                            status=400,
                        )

                    if recipient_wallet.id == source_wallet.id:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {"recipient_wallet": ["Dla przelewu wewnetrznego wybierz inny portfel."]},
                            },
                            status=400,
                        )

                if transfer_mode == Transaction.TransferMode.EXTERNAL:
                    recipient_friend_id = data.get("recipient_friend")
                    if not recipient_friend_id:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {"recipient_friend": ["Wybierz znajomego odbiorce."]},
                            },
                            status=400,
                        )

                    friend_ids = set(profile.get_friends().values_list("id", flat=True))
                    try:
                        recipient_friend_id_int = int(recipient_friend_id)
                    except (TypeError, ValueError):
                        recipient_friend_id_int = None

                    if not recipient_friend_id_int or recipient_friend_id_int not in friend_ids:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {"recipient_friend": ["Wybrany odbiorca nie jest Twoim znajomym."]},
                            },
                            status=400,
                        )

                    recipient_friend = Profile.objects.get(id=recipient_friend_id_int)
                    recipient_wallet = recipient_friend.wallets.filter(is_default=True, is_active=True).first()
                    if recipient_wallet is None:
                        return JsonResponse(
                            {
                                "success": False,
                                "errors": {
                                    "recipient_friend": [
                                        "Wybrany znajomy nie ma domyslnego portfela. Nie mozna wyslac przelewu."
                                    ]
                                },
                            },
                            status=400,
                        )
            total = sum(item_form.cleaned_data["amount"] for item_form in item_forms)

            if transaction_type == "income" and total < 0:
                return JsonResponse({
                    "success": False,
                    "errors": {"items": ["Łączna kwota wpływu musi być nieujemna."]}
                }, status=400)

            if transaction_type in ["expense", "transfer"] and total > 0:
                message = (
                    "Łączna kwota przelewu musi być niedodatnia."
                    if transaction_type == "transfer"
                    else "Łączna kwota wydatku musi być niedodatnia."
                )
                return JsonResponse({
                    "success": False,
                    "errors": {"items": [message]}
                }, status=400)
            
            with transaction.atomic():
                new_transaction = form.save(commit=False)
                new_transaction.transfer_mode = transfer_mode
                new_transaction.recipient_wallet = recipient_wallet
                new_transaction.recipient_friend = recipient_friend
                new_transaction.save()
                
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
            

class TransactionListView(LoginRequiredMixin, View):
    def get(self, request, wallet_id):
        profile = Profile.objects.get(user=request.user)
        wallet = get_object_or_404(Wallet, id=wallet_id, owner=profile)

        transactions = wallet.transactions.prefetch_related("items")

        type_filter = request.GET.get("type")
        if type_filter in Transaction.TransactionType.values:
            transactions = transactions.filter(type=type_filter)

        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        if date_from:
            transactions = transactions.filter(transaction_date__date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__date__lte=date_to)

        return render(request, "transactions/transaction_list.html", {
            "wallet": wallet,
            "transactions": transactions,
            "type_filter": type_filter or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
            "counts": transactions.aggregate(
                income=Count("id", filter=Q(type="income")),
                expense=Count("id", filter=Q(type="expense")),
                transfer=Count("id", filter=Q(type="transfer")),
            ),
        })
        
class TransactionDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        profile = Profile.objects.get(user=request.user)
        transaction_obj = get_object_or_404(
            Transaction.objects.select_related("wallet").prefetch_related("items"),
            pk=pk,
            wallet__owner=profile,
        )

        return render(
            request,
            "transactions/transaction_detail.html",
            {"transaction": transaction_obj},
        )