# Dockerfile
# Define los pasos para construir la imagen de la aplicación FastAPI

# 1. Usar una imagen base oficial de Python
FROM  python:3.13.7-alpine3.21

# 2. Establecer el directorio de trabajo dentro del contenedordocker pull 
WORKDIR /app

# 3. Copiar el archivo de requerimientos
COPY ./requirements.txt .

# 4. Instalar dependencias del sistema para compilar paquetes como psutil
RUN apk add --no-cache curl build-base python3-dev musl-dev linux-headers

# 5. Instalar las dependencias de Python
# Nota: Para que --reload funcione, uvicorn necesita 'watchfiles'.
# Asegúrate de que tu requirements.txt incluya 'uvicorn[standard]' o 'watchfiles'.
RUN pip install --no-cache-dir -r requirements.txt

# 6. Crear usuario no-root para mayor seguridad
RUN addgroup -g 1001 -S appuser &&     adduser -D -s /bin/sh -u 1001 appuser -G appuser

# 7. Copiar el código de la aplicación
# Solo copiamos lo necesario para construir la imagen.
# El código fuente se montará a través de un volumen en desarrollo.
COPY ./incident_api /app/incident_api
COPY alembic.ini /app/
COPY alembic /app/alembic
COPY manage.py /app/
COPY .env /app/

# 8. Crear directorio de logs y cambiar propietario de los archivos de la aplicación
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app



# 6. Exponer el puerto que usará la aplicación
EXPOSE 8000

# 7. Comando para ejecutar la aplicación al iniciar el contenedor (orientado a producción)
# El comando para desarrollo se especifica en docker-compose.yml
CMD ["uvicorn", "incident_api.main:app", "--host", "0.0.0.0", "--port", "8000"]