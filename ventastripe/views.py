# ventastripe/views.py

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings
from django.shortcuts import render  # Necesario para success_view
import stripe

from .models import Order, OrderItem, Producto
from .serializers import OrderCreateSerializer  # Necesario para CreateCheckoutSessionView
from rest_framework.views import APIView  # Necesario para CreateCheckoutSessionView
from rest_framework.permissions import IsAuthenticated  # Necesario para CreateCheckoutSessionView
from rest_framework.response import Response  # Necesario para CreateCheckoutSessionView

# --- Configuración de Stripe (Asegúrate de que STRIPE_SECRET_KEY y WEBHOOK_SECRET estén en settings) ---
stripe.api_key = settings.STRIPE_SECRET_KEY
WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Maneja los eventos de webhook de Stripe (Ej: pago completado)."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    # 1. Verificar la firma del Webhook (Seguridad)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Firma inválida
        return HttpResponse(status=400)
    except Exception as e:
        # Otro error
        return HttpResponse(status=500)

    # 2. Manejar el evento de pago completado
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Obtenemos el ID de la Orden de nuestra DB que guardamos en la metadata
        order_id = session.get('metadata', {}).get('order_id')

        if order_id is None:
            return HttpResponse(status=400)  # Sin ID de orden no se puede procesar

        # Usamos una transacción atómica para garantizar que la DB no quede inconsistente
        try:
            with transaction.atomic():
                # select_for_update() bloquea la fila para prevenir race conditions
                order = Order.objects.select_for_update().get(id=order_id)

                # Prevenir doble procesamiento (idempotencia)
                if order.status == 'pending':
                    order.status = 'paid'
                    order.stripe_session_id = session.id
                    order.save()

                    # 3. Disminuir el stock de los productos
                    for item in order.items.all():
                        # Asegúrate de usar select_for_update también en el producto si es necesario
                        product = Producto.objects.get(id=item.product_id)

                        # Asumiendo que la validación de stock pasó en el serializer,
                        # simplemente lo disminuimos
                        product.stock -= item.quantity
                        product.save()

                    # Log/Notificación: Envío de email de confirmación, etc.
                    print(f"✅ Pago exitoso y orden {order_id} actualizada. Stock ajustado.")

        except Order.DoesNotExist:
            print(f"Error: Orden {order_id} no encontrada.")
            return HttpResponse(status=404)
        except Exception as e:
            # Error de base de datos o lógica
            print(f"Error fatal al procesar webhook: {e}")
            return HttpResponse(status=500)

    # 4. Devolver 200 OK a Stripe para confirmar la recepción del evento
    return HttpResponse(status=200)


# ----------------------------------------------------------------------
# Vistas de Usuario (Requieren implementación de URLs)
# ----------------------------------------------------------------------

### 2. 💸 Vista de Creación de Sesión (`CreateCheckoutSessionView`)




# ventastripe/views.py (Continuación)

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # 1. VALIDACIÓN (Usando el Serializer creado en el Paso 2)
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = request.user

        try:
            # 2. CREACIÓN DE LA ORDEN PENDIENTE (DB)
            order = Order.objects.create(user=user, status='pending')
            line_items = []

            for item_data in validated_data['cart_items']:
                product = item_data['product_instance']
                quantity = item_data['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )

                # Prepara el line item para Stripe (Stripe usa centavos)
                line_items.append({
                    'price_data': {
                        'currency': 'mxn',
                        'product_data': {'name': product.name},
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': quantity,
                })

            order.calculate_total()

            # 3. CREAR SESIÓN DE CHECKOUT EN STRIPE
            success_url_base = request.build_absolute_uri('/ventastripe/pago/exitoso/')  # OJO con la ruta
            cancel_url_base = request.build_absolute_uri('/carrito/')  # Ruta del Frontend o vista de Django

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url_base + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url_base,
                metadata={'order_id': order.id}
            )

            return Response({'url': checkout_session.url})

        except Exception as e:
            # Si falla Stripe, borramos la orden pendiente para que no quede basura
            order.delete()
            return Response({'error': str(e)}, status=400)


### 3. 🖼️ Vista de Éxito de Redirección (`success_view`)



# ventastripe/views.py (Continuación)

def success_view(request):
    """Vista a la que Stripe redirige al usuario tras un pago exitoso."""

    session_id = request.GET.get('session_id')

    if not session_id:
        # En un entorno real, puedes registrar este intento de acceso o redirigir
        return HttpResponseBadRequest("Falta el ID de Sesión de Stripe.")

    try:
        # Buscamos la orden usando el ID de sesión de Stripe (el Webhook ya debió haberla marcado como 'paid')
        order = Order.objects.get(stripe_session_id=session_id)

        context = {
            'order_id': order.id,
            'status': order.get_status_display(),
            'total': order.total_amount,
            'message': '¡Gracias por tu compra en CoffeU! Tu pedido ha sido recibido y está siendo procesado.'
        }

        # Necesitas crear este template: ventastripe/templates/ventastripe/payment_success.html
        return render(request, 'ventastripe/payment_success.html', context)

    except Order.DoesNotExist:
        # Si el webhook aún no llega o hubo un error de redirección
        context = {
            'message': 'Tu pago se procesó. Estamos esperando la confirmación final de Stripe. Revisa tu email/app en un momento.'
        }
        # Puedes usar otro template de "pendiente de confirmación"
        return render(request, 'ventastripe/payment_pending.html', context)
    except Exception as e:
        # Manejo de cualquier otro error
        return render(request, 'ventastripe/payment_error.html', {'error': str(e)})