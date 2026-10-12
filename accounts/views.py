from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render

from .models import (
    BankAccount,
    BankCard,
    Transaction,
    Loan,
    Deposit,
    CurrencyExchange,
    Notification,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password:
            messages.error(request, "Barcha maydonlarni to‘ldiring.")
            return redirect("register")

        if password != password2:
            messages.error(request, "Parollar bir xil emas.")
            return redirect("register")

        if len(password) < 6:
            messages.error(
                request,
                "Parol kamida 6 ta belgidan iborat bo‘lsin."
            )
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Bu username allaqachon mavjud."
            )
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "Bu email allaqachon ro‘yxatdan o‘tgan."
            )
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            "NOVA BANK hisobingiz muvaffaqiyatli yaratildi!"
        )

        return redirect("dashboard")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                "NOVA BANK hisobingizga xush kelibsiz!"
            )

            return redirect("dashboard")

        messages.error(
            request,
            "Username yoki parol noto‘g‘ri."
        )

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def dashboard(request):
    account, created = BankAccount.objects.get_or_create(
        user=request.user,
        defaults={
            "account_number": f"NOVA{request.user.id:08d}",
            "account_type": "standard",
            "balance": 0,
        }
    )

    cards = BankCard.objects.filter(
        user=request.user
    ).order_by("-created_at")

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")

    income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

    expenses = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type in ["expense", "transfer"]
    )

    context = {
        "account": account,
        "cards": cards,
        "transactions": transactions[:5],
        "income": income,
        "expenses": expenses,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )


@login_required(login_url="login")
def cards_view(request):
    cards = BankCard.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/cards.html",
        {
            "cards": cards,
        }
    )


@login_required(login_url="login")
def transfer_view(request):

    sender_account, created = BankAccount.objects.get_or_create(
        user=request.user,
        defaults={
            "account_number": f"NOVA{request.user.id:08d}",
            "account_type": "standard",
            "balance": 0,
        }
    )

    if request.method == "POST":

        recipient_account_number = request.POST.get(
            "account_number",
            ""
        ).strip()

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        # Hisob raqami tekshiriladi
        if not recipient_account_number:
            messages.error(
                request,
                "Qabul qiluvchining hisob raqamini kiriting."
            )
            return redirect("transfer")

        # Summa tekshiriladi
        if not amount_text:
            messages.error(
                request,
                "Transfer summasini kiriting."
            )
            return redirect("transfer")

        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            messages.error(
                request,
                "Transfer summasi noto‘g‘ri."
            )
            return redirect("transfer")

        # Musbat summa bo‘lishi kerak
        if amount <= 0:
            messages.error(
                request,
                "Transfer summasi 0 dan katta bo‘lishi kerak."
            )
            return redirect("transfer")

        # O'ziga transfer qilishni bloklaymiz
        if recipient_account_number == sender_account.account_number:
            messages.error(
                request,
                "O‘zingizning hisobingizga pul yubora olmaysiz."
            )
            return redirect("transfer")

        # Qabul qiluvchi hisobini topamiz
        try:
            recipient_account = BankAccount.objects.select_related(
                "user"
            ).get(
                account_number=recipient_account_number
            )
        except BankAccount.DoesNotExist:
            messages.error(
                request,
                "Bunday hisob raqami topilmadi."
            )
            return redirect("transfer")

        # Balans yetarliligini tekshiramiz
        if sender_account.balance < amount:
            messages.error(
                request,
                "Hisobingizda yetarli mablag‘ mavjud emas."
            )
            return redirect("transfer")

        # Transferni atomik tarzda amalga oshiramiz
        with transaction.atomic():

            sender_account.balance -= amount
            sender_account.save(
                update_fields=["balance"]
            )

            recipient_account.balance += amount
            recipient_account.save(
                update_fields=["balance"]
            )

            # Jo‘natuvchi transaction
            Transaction.objects.create(
                user=request.user,
                title=f"Transfer → {recipient_account.user.username}",
                transaction_type="transfer",
                amount=amount,
                status="completed",
                description=description
                or f"{recipient_account.account_number} hisobiga transfer"
            )

            # Qabul qiluvchi transaction
            Transaction.objects.create(
                user=recipient_account.user,
                title=f"Transfer ← {request.user.username}",
                transaction_type="income",
                amount=amount,
                status="completed",
                description=description
                or f"{sender_account.account_number} hisobidan transfer"
            )

        messages.success(
            request,
            f"${amount:,.2f} muvaffaqiyatli yuborildi!"
        )

        return redirect("transfer")

    return render(
        request,
        "accounts/transfer.html",
        {
            "account": sender_account,
        }
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        "Hisobdan muvaffaqiyatli chiqdingiz."
    )

    return redirect("home")

@login_required(login_url="login")
def analytics_view(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

    total_expenses = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )

    total_transfers = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "transfer"
    )

    transaction_count = transactions.count()

    completed_count = transactions.filter(
        status="completed"
    ).count()

    pending_count = transactions.filter(
        status="pending"
    ).count()

    context = {
        "transactions": transactions,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_transfers": total_transfers,
        "transaction_count": transaction_count,
        "completed_count": completed_count,
        "pending_count": pending_count,
    }

    return render(
        request,
        "accounts/analytics.html",
        context
    )

@login_required(login_url="login")
def loans_view(request):
    loans = Loan.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_amount = sum(
        loan.amount for loan in loans
    )

    remaining_amount = sum(
        loan.remaining_amount for loan in loans
    )

    active_loans = loans.filter(
        status="active"
    ).count()

    pending_loans = loans.filter(
        status="pending"
    ).count()

    context = {
        "loans": loans,
        "total_amount": total_amount,
        "remaining_amount": remaining_amount,
        "active_loans": active_loans,
        "pending_loans": pending_loans,
    }

    return render(
        request,
        "accounts/loans.html",
        context
    )

@login_required(login_url="login")
def deposits_view(request):

    deposits = Deposit.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_amount = sum(
        deposit.amount for deposit in deposits
    )

    total_profit = sum(
        deposit.expected_profit for deposit in deposits
    )

    active_deposits = deposits.filter(
        status="active"
    ).count()

    completed_deposits = deposits.filter(
        status="completed"
    ).count()

    context = {
        "deposits": deposits,
        "total_amount": total_amount,
        "total_profit": total_profit,
        "active_deposits": active_deposits,
        "completed_deposits": completed_deposits,
    }

    return render(
        request,
        "accounts/deposits.html",
        context
    )

from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .models import BankAccount, Transaction, Deposit


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1

    days_in_month = [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]

    day = min(source_date.day, days_in_month[month - 1])

    return date(year, month, day)


@login_required(login_url="login")
def deposit_create_view(request):

    if request.method == "POST":

        deposit_type = request.POST.get("deposit_type")
        amount_text = request.POST.get("amount")
        term_text = request.POST.get("term_months")

        allowed_types = {
            "standard": Decimal("10.00"),
            "premium": Decimal("13.00"),
            "flexible": Decimal("8.00"),
        }

        allowed_terms = [3, 6, 12, 24]

        if deposit_type not in allowed_types:
            messages.error(request, "Depozit turi noto‘g‘ri.")
            return redirect("deposit_create")

        try:
            amount = Decimal(amount_text)
        except (InvalidOperation, TypeError):
            messages.error(request, "Depozit summasini to‘g‘ri kiriting.")
            return redirect("deposit_create")

        try:
            term_months = int(term_text)
        except (ValueError, TypeError):
            messages.error(request, "Depozit muddatini to‘g‘ri tanlang.")
            return redirect("deposit_create")

        if amount <= 0:
            messages.error(request, "Depozit summasi 0 dan katta bo‘lishi kerak.")
            return redirect("deposit_create")

        if term_months not in allowed_terms:
            messages.error(request, "Depozit muddati noto‘g‘ri.")
            return redirect("deposit_create")

        account, created = BankAccount.objects.get_or_create(
            user=request.user,
            defaults={
                "account_number": f"408178{request.user.id:08d}",
                "account_type": "standard",
                "balance": 0,
            }
        )

        if account.balance < amount:
            messages.error(
                request,
                f"Hisobingizda yetarli mablag‘ yo‘q. "
                f"Balansingiz: ${account.balance:,.2f}"
            )
            return redirect("deposit_create")

        interest_rate = allowed_types[deposit_type]

        expected_profit = (
            amount
            * (interest_rate / Decimal("100"))
            * (Decimal(term_months) / Decimal("12"))
        ).quantize(Decimal("0.01"))

        total_amount = (
            amount + expected_profit
        ).quantize(Decimal("0.01"))

        maturity_date = add_months(
            date.today(),
            term_months
        )

        with transaction.atomic():

            account.balance -= amount
            account.save(update_fields=["balance"])

            Deposit.objects.create(
                user=request.user,
                deposit_type=deposit_type,
                amount=amount,
                interest_rate=interest_rate,
                term_months=term_months,
                expected_profit=expected_profit,
                total_amount=total_amount,
                status="active",
                maturity_date=maturity_date,
            )

            Transaction.objects.create(
                user=request.user,
                title="Depozit ochildi",
                transaction_type="expense",
                amount=amount,
                status="completed",
                description=(
                    f"{deposit_type.title()} depozit. "
                    f"Muddat: {term_months} oy. "
                    f"Foiz: {interest_rate}%."
                ),
            )

        messages.success(
            request,
            f"Depozit muvaffaqiyatli ochildi! "
            f"Kutilayotgan foyda: ${expected_profit:,.2f}"
        )

        return redirect("deposits")

    return render(
        request,
        "accounts/deposit_create.html"
    )

@login_required(login_url="login")
def currency_exchange_view(request):

    currencies = {
        "USD": "US Dollar",
        "EUR": "Euro",
        "RUB": "Russian Ruble",
        "UZS": "Uzbekistani Som",
    }

    # Demo kurslar:
    # 1 USD = 12,000 UZS
    # 1 EUR = 13,000 UZS
    # 1 RUB = 130 UZS
    rates_to_uzs = {
        "USD": Decimal("12000"),
        "EUR": Decimal("13000"),
        "RUB": Decimal("130"),
        "UZS": Decimal("1"),
    }

    if request.method == "POST":

        from_currency = request.POST.get("from_currency")
        to_currency = request.POST.get("to_currency")
        amount_text = request.POST.get("amount")

        if from_currency not in currencies:
            messages.error(
                request,
                "Boshlang‘ich valyuta noto‘g‘ri."
            )
            return redirect("currency_exchange")

        if to_currency not in currencies:
            messages.error(
                request,
                "Qabul qiluvchi valyuta noto‘g‘ri."
            )
            return redirect("currency_exchange")

        if from_currency == to_currency:
            messages.error(
                request,
                "Bir xil valyutalarni ayirboshlab bo‘lmaydi."
            )
            return redirect("currency_exchange")

        try:
            amount = Decimal(amount_text)
        except (InvalidOperation, TypeError):
            messages.error(
                request,
                "Summani to‘g‘ri kiriting."
            )
            return redirect("currency_exchange")

        if amount <= 0:
            messages.error(
                request,
                "Summa 0 dan katta bo‘lishi kerak."
            )
            return redirect("currency_exchange")

        # Demo bank account
        account, created = BankAccount.objects.get_or_create(
            user=request.user,
            defaults={
                "account_number": f"408178{request.user.id:08d}",
                "account_type": "standard",
                "balance": 0,
            }
        )

        # Demo tizimda asosiy hisob USD hisoblanadi.
        if from_currency == "USD":

            if account.balance < amount:
                messages.error(
                    request,
                    f"Hisobingizda yetarli mablag‘ yo‘q. "
                    f"Balansingiz: ${account.balance:,.2f}"
                )
                return redirect("currency_exchange")

        # UZS / EUR / RUB uchun demo balanslar
        # keyinchalik alohida valyuta balanslarini qo‘shamiz.

        from_rate = rates_to_uzs[from_currency]
        to_rate = rates_to_uzs[to_currency]

        amount_in_uzs = amount * from_rate

        converted_amount = (
            amount_in_uzs / to_rate
        ).quantize(
            Decimal("0.01")
        )

        exchange_rate = (
            from_rate / to_rate
        ).quantize(
            Decimal("0.000001")
        )

        with transaction.atomic():

            if from_currency == "USD":

                account.balance -= amount
                account.save(
                    update_fields=["balance"]
                )

            CurrencyExchange.objects.create(
                user=request.user,
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                exchange_rate=exchange_rate,
                converted_amount=converted_amount,
            )

            Transaction.objects.create(
                user=request.user,
                title="Valyuta ayirboshlash",
                transaction_type="transfer",
                amount=amount,
                status="completed",
                description=(
                    f"{amount:,.2f} {from_currency} → "
                    f"{converted_amount:,.2f} {to_currency}"
                ),
            )

        messages.success(
            request,
            f"Ayirboshlash muvaffaqiyatli! "
            f"{amount:,.2f} {from_currency} → "
            f"{converted_amount:,.2f} {to_currency}"
        )

        return redirect("currency_exchange")

    return render(
        request,
        "accounts/currency_exchange.html",
        {
            "currencies": currencies,
        }
    )

@login_required(login_url="login")
def notifications_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    unread_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        "accounts/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        }
    )


@login_required(login_url="login")
def mark_notification_read(request, pk):
    notification = Notification.objects.filter(
        pk=pk,
        user=request.user
    ).first()

    if notification:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    return redirect("notifications")


@login_required(login_url="login")
def mark_all_notifications_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect("notifications")