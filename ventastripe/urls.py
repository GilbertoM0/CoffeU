# ventastripe/urls.py

from django.urls import path
from .views import CreateCheckoutSessionView, stripe_webhook, success_view

urlpatterns = [
    # 1. API para iniciar la sesión de Stripe (DRF - Requiere JWT)
    # Usamos .as_view() porque es una clase APIView
    path(
        'crear-sesion/',
        CreateCheckoutSessionView.as_view(),
        name='create_checkout_session'
    ),

    # 2. Endpoint del Webhook (Django Función - Llamada por Stripe)
    # Ruta crítica que debe estar expuesta públicamente
    path(
        'webhook/',
        stripe_webhook,
        name='stripe_webhook'
    ),

    # 3. Vista de Éxito (Django Función - Redirección del usuario)
    path(
        'pago/exitoso/',
        success_view,
        name='payment_success'
    ),
]