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

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "msusuarios.wsgi:application"]
