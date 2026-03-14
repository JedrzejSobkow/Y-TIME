from django.db import models
from apps.core.models import TimeStampedModel
from apps.wallets.models import Wallet
from decimal import Decimal
from django.core.exceptions import ValidationError



class Transaction(TimeStampedModel):
    class TransactionType(models.TextChoices):
        EXPENSE = "expense", "Expense"
        INCOME = "income", "Income"
        TRANSFER = "transfer", "Transfer"
        
        
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    transaction_date = models.DateTimeField()
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
   
    
class TransactionItem(TimeStampedModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # TODO add category
    
    def __str__(self):
        return f"{self.name}: {self.amount}"