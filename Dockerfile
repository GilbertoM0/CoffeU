# Etapa base, imagen de pyhton
FROM python:3.12-slim
#Crea directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2 y compilaciones
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalamos dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Paso 7: Ejecutar makemigrations inyectando temporalmente la SECRET_KEY
# Usamos un valor fijo para el build. Esto es seguro porque no se usa en runtime de Gunicorn.
RUN SECRET_KEY="django-insecure-n5rnuw9x2$f!6+9^2q5z-m%8@_@#becnr$$(miy=npkw@-_b6w" python manage.py makemigrations ventastripe --no-input

# Paso 8: Aplicar migraciones inyectando temporalmente la SECRET_KEY
RUN SECRET_KEY="django-insecure-n5rnuw9x2$f!6+9^2q5z-m%8@_@#becnr$$(miy=npkw@-_b6w" python manage.py migrate --no-input


EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "msusuarios.wsgi:application"]
