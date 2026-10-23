"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin,messages
from django.urls import include,path
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


@require_POST
def clear_cache_view(request):
   
    cache.clear()

    messages.success(
        request,
        "Cache cleared successfully!"
    )
   
    return redirect("admin:index")

urlpatterns = [
    path(
            "admin/clear-cache/",
            admin.site.admin_view(clear_cache_view),
            name="admin-clear-cache",
        ),
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path("accounts/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
   

]
