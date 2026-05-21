FROM python:3.11-slim

# Crear un usuario no raíz para la ejecución segura (requerido por Hugging Face Spaces)
RUN useradd -m -u 1000 user

WORKDIR /app

# Instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto con los permisos del usuario creado
COPY --chown=user:user . .

# Cambiar al usuario no raíz
USER user

# Exponer el puerto estándar de Hugging Face Spaces
EXPOSE 7860

# Comando para arrancar la aplicación de Shiny en el puerto expuesto
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
