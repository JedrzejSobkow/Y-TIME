from django.db import models
from apps.core.models import TimeStampedModel
from apps.users.models import Profile
from decimal import Decimal

class Wallet(TimeStampedModel):
    class Currency(models.TextChoices):
        # TODO DO NOT HARDCODE THEM
        PLN = "pln", "Polish Złoty"
        EUR = "eur", "Euro"
        CZK = "czk", "Czech Koruna"
        USD = "usd", "United States dollar"
        
    class WalletType(models.TextChoices):
        # TODO DO NOT HARDCODE THEM
        CASH = "cash", "Cash"
        BANK_ACCOUNT = "bank_account", "Bank Account"
        CREDIT_CARD = "credit_card", "Credit Card"
        SAVINGS = "savings", "Savings"
        INVESTMENT = "investment", "Investment"
        OTHER = "other", "Other"
        
        
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="wallets")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=12, choices=WalletType.choices, default=WalletType.CASH)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.PLN)
    is_active = models.BooleanField(default=True)
    
    # TODO VERIFY IF INCOME OR OUTCOME
    @property
    def balance(self):
        return self.transactions.aggregate(total=models.Sum('items__amount'))['total'] or Decimal("0.00")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="unique_wallet")
        ]
        
        indexes = [
            models.Index(fields=["owner"])
        ]
        
    def __str__(self):
        return f"{self.name}: {self.balance} {self.currency}"