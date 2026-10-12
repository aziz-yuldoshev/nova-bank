from django.contrib import admin
from .models import (
    BankAccount,
    BankCard,
    Transaction,
    Loan,
    Deposit,
    CurrencyExchange,
    Notification,
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "account_number",
        "account_type",
        "balance",
        "created_at",
    )

    list_filter = (
        "account_type",
        "created_at",
    )

    search_fields = (
        "user__username",
        "account_number",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = (
        "card_holder",
        "card_number",
        "card_type",
        "balance",
        "status",
        "expiry_date",
    )

    list_filter = (
        "card_type",
        "status",
    )

    search_fields = (
        "card_holder",
        "card_number",
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "transaction_type",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "user__username",
        "description",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "loan_type",
        "amount",
        "interest_rate",
        "term_months",
        "monthly_payment",
        "remaining_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "loan_type",
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "deposit_type",
        "amount",
        "interest_rate",
        "term_months",
        "expected_profit",
        "total_amount",
        "status",
        "maturity_date",
        "created_at",
    )

    list_filter = (
        "deposit_type",
        "status",
        "term_months",
        "created_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

@admin.register(CurrencyExchange)
class CurrencyExchangeAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "from_currency",
        "to_currency",
        "amount",
        "exchange_rate",
        "converted_amount",
        "created_at",
    )

    list_filter = (
        "from_currency",
        "to_currency",
        "created_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__username",
        "title",
        "message",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )