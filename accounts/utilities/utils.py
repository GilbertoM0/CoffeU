from django.core.mail import send_mail

from msusuarios import settings


def enviar_otp_mail(usr):
    asunto = "Envio de OTP Mail"
    mensaje = f"""
    Gracias por registrarte con nosotros. Tu codigo OTP es: {usr.otp_codigo}
    
    Este código es válido por 5 minjutos.
    
    Atte
    Equipo de soporte
    """
    # Utilizar el metodo send_mail
    send_mail(
        subject=asunto, # Asunto
        message=f"Este es tu codigo OTP: {usr.otp_codigo}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usr.email],
        fail_silently=False,
 )