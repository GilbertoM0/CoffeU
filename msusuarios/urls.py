

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def api_root(request):
    return JsonResponse(
        {
            "mensaje": "API de CoffeU activa",
            "endpoints": {
                "accounts": "/accounts/",
                "products": "/products/",
                "ventas": "/ventas/",
                "orders": "/orders/",
            },
        }
    )

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", api_root, name="api_root"),
    path("accounts/", include("accounts.urls")),
    path('products/', include('products.urls')),
    

    path('ventas/', include('ventas.urls')),
    path('orders/', include('orders.urls')),
]

