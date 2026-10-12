from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),

    # Language switcher
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    # Home
    path("", views.home, name="home"),

    # Accounts
    path("", include("accounts.urls")),
)