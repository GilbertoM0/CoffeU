from django.db import models

class VentaSemanal(models.Model):
    semana = models.IntegerField()
    producto = models.CharField(max_length=100)

    ventas_semana = models.IntegerField()
    inventario_inicial = models.IntegerField()
    inventario_final = models.IntegerField()

    reabastecio = models.BooleanField()  # True = sí, False = no
    cantidad_reabastecida = models.IntegerField(default=0)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Semana {self.semana} - {self.producto}"
