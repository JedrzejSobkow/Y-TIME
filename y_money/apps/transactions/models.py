from django.db import models
from apps.core.models import TimeStampedModel
from apps.wallets.models import Wallet
from apps.users.models import Profile
from decimal import Decimal
from django.core.exceptions import ValidationError



class Transaction(TimeStampedModel):
    class TransactionType(models.TextChoices):
        EXPENSE = "expense", "Expense"
        INCOME = "income", "Income"
        TRANSFER = "transfer", "Transfer"

    class TransferMode(models.TextChoices):
        INTERNAL = "internal", "Internal"
        EXTERNAL = "external", "External"
        
        
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    transaction_date = models.DateTimeField()
    transfer_mode = models.CharField(max_length=10, choices=TransferMode.choices, blank=True, null=True)
    recipient_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        related_name="incoming_transfers",
        blank=True,
        null=True,
    )
    recipient_friend = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name="incoming_external_transfers",
        blank=True,
        null=True,
    )
    # TODO add counterparty
    
    @property
    def amount(self):
        return self.items.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
    
    class Meta:
        indexes = [
            models.Index(fields=["wallet", "transaction_date"])
        ]
        
        ordering = ["-transaction_date"]
        
    def clean(self):
        if self.pk and not self.items.exists():
            raise ValidationError("Transaction must have at least one item")

        if self.type != self.TransactionType.TRANSFER:
            if self.transfer_mode or self.recipient_wallet_id or self.recipient_friend_id:
                raise ValidationError("Transfer details are allowed only for transfer transactions")

        if self.type == self.TransactionType.TRANSFER:
            if self.transfer_mode not in self.TransferMode.values:
                raise ValidationError("Transfer mode is required for transfer transactions")

            if self.transfer_mode == self.TransferMode.INTERNAL:
                if not self.recipient_wallet_id:
                    raise ValidationError("Internal transfer requires recipient wallet")
                if self.recipient_friend_id:
                    raise ValidationError("Internal transfer cannot have friend recipient")

            if self.transfer_mode == self.TransferMode.EXTERNAL:
                if not self.recipient_friend_id:
                    raise ValidationError("External transfer requires friend recipient")
   
    
class TransactionItem(TimeStampedModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # TODO add category
    
    def __str__(self):
        return f"{self.name}: {self.amount}"