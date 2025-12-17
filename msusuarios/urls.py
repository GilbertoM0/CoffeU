

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path('products/', include('products.urls')),
<<<<<<< HEAD
    
=======
    path('ventas/', include('ventas.urls')),
    path('orders/', include('orders.urls')),
>>>>>>> 4b13c376906265c0c77a995e4eec7d8eb069b8b7
]
