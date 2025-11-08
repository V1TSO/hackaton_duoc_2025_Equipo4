#!/bin/bash

# Script para iniciar el servidor backend desde el directorio correcto

cd "$(dirname "$0")"

# Activar el entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No se encontró el entorno virtual. Ejecuta: python3 -m venv venv"
    exit 1
fi

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo "Advertencia: No se encontró el archivo .env"
    echo "Asegúrate de tener configuradas las variables de entorno necesarias"
fi

# Iniciar el servidor con reload para desarrollo
echo "Iniciando servidor backend en http://localhost:8000"
echo "Presiona CTRL+C para detener"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

