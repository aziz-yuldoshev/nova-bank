from django.db import models
from django.contrib.auth.models import User


class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ("standard", "Standard"),
        ("premium", "Premium"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="bank_account"
    )

    account_number = models.CharField(
        max_length=20,
        unique=True
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default="standard"
    )

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

    @property
    def formatted_balance(self):
        return f"${self.balance:,.2f}"


class BankCard(models.Model):
    CARD_TYPES = (
        ("debit", "Debit"),
        ("credit", "Credit"),
        ("platinum", "Platinum"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("blocked", "Blocked"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bank_cards"
    )

    card_number = models.CharField(
        max_length=19,
        unique=True
    )

    card_holder = models.CharField(
        max_length=150
    )

    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        default="debit"
    )

    expiry_date = models.CharField(
        max_length=5
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.card_holder} - {self.card_number}"

    @property
    def masked_number(self):
        return f"•••• •••• •••• {self.card_number[-4:]}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    )

    STATUS_CHOICES = (
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    title = models.CharField(
        max_length=200
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed"
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.amount}"

    @property
    def is_income(self):
        return self.transaction_type == "income"

    @property
    def is_expense(self):
        return self.transaction_type in ["expense", "transfer"]

class Loan(models.Model):

    LOAN_TYPES = (
        ("consumer", "Consumer Loan"),
        ("auto", "Auto Loan"),
        ("business", "Business Loan"),
        ("mortgage", "Mortgage"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    loan_type = models.CharField(
        max_length=30,
        choices=LOAN_TYPES,
        default="consumer"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    term_months = models.PositiveIntegerField()

    monthly_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    remaining_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - ${self.amount:,.2f}"

    @property
    def paid_amount(self):
        return self.amount - self.remaining_amount

    @property
    def progress(self):
        if self.amount == 0:
            return 0

        return int(
            (self.paid_amount / self.amount) * 100
        )

class Deposit(models.Model):

    DEPOSIT_TYPES = (
        ("standard", "Standard Deposit"),
        ("premium", "Premium Deposit"),
        ("flexible", "Flexible Deposit"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="deposits"
    )

    deposit_type = models.CharField(
        max_length=30,
        choices=DEPOSIT_TYPES,
        default="standard"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    term_months = models.PositiveIntegerField()

    expected_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    maturity_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - ${self.amount:,.2f}"

    @property
    def progress(self):
        if self.status == "completed":
            return 100

        if self.status == "cancelled":
            return 0

        return 50

class CurrencyExchange(models.Model):

    CURRENCY_CHOICES = (
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("RUB", "Russian Ruble"),
        ("UZS", "Uzbekistani Som"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="currency_exchanges"
    )

    from_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES
    )

    to_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    exchange_rate = models.DecimalField(
        max_digits=15,
        decimal_places=6
    )

    converted_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.amount} {self.from_currency} → "
            f"{self.converted_amount} {self.to_currency}"
        )


class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("transfer", "Transfer"),
        ("loan", "Loan"),
        ("deposit", "Deposit"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="info"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"