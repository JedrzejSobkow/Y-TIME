from django import forms
from .models import Wallet


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ["name", "description", "type", "currency", "is_default"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Np. Konto główne...",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Opcjonalny opis...",
            }),
            "type": forms.Select(attrs={
                "class": "form-select",
            }),
            "currency": forms.Select(attrs={
                "class": "form-select",
            }),
            "is_default": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].choices = Wallet.WalletType.choices
        self.fields["currency"].choices = Wallet.Currency.choices