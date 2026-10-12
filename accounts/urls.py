from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("cards/", views.cards_view, name="cards"),
    path("transfer/", views.transfer_view, name="transfer"),
    path("analytics/", views.analytics_view, name="analytics"),
    path("loans/", views.loans_view, name="loans"),
    path("deposits/", views.deposits_view, name="deposits"),
    path("deposits/create/", views.deposit_create_view, name="deposit_create"),
    path("currency-exchange/", views.currency_exchange_view, name="currency_exchange"),
    path("notifications/", views.notifications_view, name="notifications"),
    path(
        "notifications/<int:pk>/read/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),
    path(
        "notifications/read-all/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read"
    ),
]
