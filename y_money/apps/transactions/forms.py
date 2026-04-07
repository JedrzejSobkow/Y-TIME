from django import forms
from .models import Transaction, TransactionItem
from apps.wallets.models import Wallet

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["wallet", "title", "description", "type", "transaction_date", "transfer_mode", "recipient_wallet", "recipient_friend"]
        widgets = {
            "wallet": forms.Select(attrs={
                "class": "form-select form-select-lg",
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Np. Zakupy spożywcze...",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Opcjonalny opis...",
            }),
            "type": forms.Select(attrs={
                "class": "form-select form-select-lg",
            }),
            "transaction_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }
        
    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["transaction_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["type"].choices = Transaction.TransactionType.choices
        # Chacge User -> Profile
        if profile is not None:
            self.fields["wallet"].queryset = Wallet.objects.filter(owner=profile)
        else:
            self.fields["wallet"].queryset = Wallet.objects.none()
            

class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ["name", "amount"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nazwa pozycji...",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0.01",
            }),
        }