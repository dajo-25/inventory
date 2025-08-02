FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias y instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Creamos directorio donde montará Coolify la DB
RUN mkdir -p /data

# Exponemos el puerto de Flask
EXPOSE 5000

# Arrancamos con gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]