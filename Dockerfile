# Etapa de construcción
FROM python:3.11-slim as builder

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa de producción
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para producción
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde la etapa de construcción
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código de la aplicación
COPY . .

# Cambiar permisos
RUN chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Agregar el directorio de Python al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Exponer puerto
EXPOSE 7070

# Variables de entorno por defecto
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7070", "wsgi:app"]
