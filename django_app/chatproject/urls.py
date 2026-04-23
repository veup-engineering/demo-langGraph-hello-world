"""URL configuration for chatproject."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/chat/", permanent=False)),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="chat/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("chat/", include("chat.urls")),
    path("api/", include("api.urls")),
]
