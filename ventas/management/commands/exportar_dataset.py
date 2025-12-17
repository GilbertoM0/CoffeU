from django.core.management.base import BaseCommand
from ventas.models import VentaSemanal
import pandas as pd

class Command(BaseCommand):
    help = "Exporta las ventas semanales como dataset CSV"

    def handle(self, *args, **kwargs):
        datos = VentaSemanal.objects.all().values()
        df = pd.DataFrame(datos)

        if df.empty:
            self.stdout.write(self.style.ERROR("La tabla VentaSemanal está vacía. Agrega ventas primero."))
            return

        # Quitar _state (lo mete Django solo)
        columnas = [c for c in df.columns if c != "_state"]

        df = df[columnas]
        df.to_csv("dataset_inventario.csv", index=False)

        self.stdout.write(self.style.SUCCESS("Dataset exportado como dataset_inventario.csv"))
