from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),

     # Email activation
    path(
        "activation-sent/",
        views.activation_sent,
        name="activation_sent",
    ),

    path(
        "activate/<uidb64>/<token>/",
        views.activate,
        name="activate",
    ),
]