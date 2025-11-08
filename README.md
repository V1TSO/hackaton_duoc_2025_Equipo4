GitHub Copilot Chat Assistant

# 🚀 hackaton_duoc_2025_Equipo4

<h3 align="center">Proyecto Hackathon Duoc UC 2025 — Equipo 4</h3>

<p align="center">
  <img alt="Jupyter" src="https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.x-3178c6?style=for-the-badge&logo=typescript" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
</p>

Descripción breve
- Repositorio multi-componente creado por el Equipo 4 para el Hackathon Duoc UC 2025. Contiene notebooks (ML/experimentación), backend en Python, frontend en TypeScript/Next.js y documentación / scripts de pruebas.

Archivos y documentos clave en la raíz
- MULTI_MODEL_ARCHITECTURE.md — arquitectura del sistema/modelos
- PROGRESO_V.md — bitácora de avance
- QUICK_START_TESTING.md — guía rápida para pruebas
- TESTING_INTEGRATION.md — pruebas de integración / E2E
- .env — variables de entorno (ver nota de seguridad)
- package-lock.json — lockfile de Node (indica componente frontend)

Estructura principal (resumen)

```
.
/
├── back/                   # Backend (FastAPI)
│   ├── app/
│   │   ├── agents/         # Lógica de LLM (OpenAI, RAG)
│   │   ├── core/           # Configuración y conexión a DB (Supabase)
│   │   ├── ml/             # Servicio de predicción (carga de .pkl)
│   │   ├── models/         # Modelos de datos Pydantic
│   │   ├── routes/         # Endpoints de la API (chat, users, health)
│   │   └── services/       # Lógica de negocio
│   ├── main.py             # Archivo principal de FastAPI
│   └── requirements.txt
│
├── front/                  # Frontend (Next.js 15)
│   ├── src/
│   │   ├── app/            # Rutas (App Router)
│   │   ├── components/     # Componentes de React
│   │   ├── lib/            # Clientes de API, Supabase, hooks
│   │   └── types/          # Tipos de TypeScript
│   ├── package.json
│   └── wrangler.jsonc      # Configuración de Cloudflare
│
├── ml/ (y /cardio)         # Proyecto de Machine Learning y Datos
│   ├── GUIA_HACKATHON_SALUD_NHANES_3.ipynb # Notebook principal
│   ├── data/               # (Vacío) Destino para datos NHANES
│   ├── kb/                 # Base de conocimiento para RAG
│   ├── models/             # (Generado) Modelos entrenados (.pkl)
│   ├── reports/            # Reporte técnico, métricas, fairness, SHAP
│   ├── descargar_nhanes.py # Script de descarga de datos
│   ├── convertir_nhanes.py # Script de conversión .XPT -> .CSV
│   └── requirements.txt
│
├── Desafio_Salud_NHANES_2025_duoc.pdf  # PDF oficial del desafío
└── README.md
```

2) Leer documentación base
- Abrir MULTI_MODEL_ARCHITECTURE.md para la arquitectura.
- Revisar PROGRESO_V.md para estado y asignaciones.
- Revisar QUICK_START_TESTING.md y TESTING_INTEGRATION.md para tests y flujos.

3) Frontend (carpeta front)
- Información clave (extraída de front/package.json):
  - Framework: Next.js 15
  - React: 19.1.0
  - Dependencias destacadas: @supabase/supabase-js, @supabase/ssr, @opennextjs/cloudflare, lucide-react, react-markdown, zod
  - Scripts disponibles:
    - dev: next dev --turbopack
    - build: next build
    - start: next start
    - lint: next lint
    - lint:fix: npx eslint . --ext .js,.ts,.jsx,.tsx --fix
    - pages:build: npx @cloudflare/next-on-pages
    - preview: npm run pages:build && wrangler pages dev
    - deploy: npm run pages:build && wrangler pages deploy
    - cf-typegen: wrangler types --env-interface CloudflareEnv ./env.d.ts

- Requisitos recomendados:
  - Node.js (LTS, p. ej. v18+ o la versión LTS que soporte Next 15), npm
  - Wrangler CLI instalado globalmente si vas a usar preview/deploy con Cloudflare: npm i -g wrangler
  - Acceso a cuenta Cloudflare para despliegue si usas wrangler pages deploy
  - Si usas Supabase, configurar variables de entorno correspondientes (URL, KEY, etc.)

- Comandos de arranque:
```bash
cd front
npm install
npm run dev          # desarrollo (Next dev --turbopack)
# Para producción local / build:
npm run build
npm run start        # iniciar build (next start)

# Para previsualizar con Cloudflare Pages localmente (requiere wrangler):
npm run preview

# Para desplegar en Cloudflare Pages (requiere wrangler configurado):
npm run deploy
```

- Notas:
  - Existe script cf-typegen para generar tipado de variables de entorno usando wrangler: `npm run cf-typegen` (genera ./env.d.ts).
  - Revisa / crea un `.env` o la forma de inyectar variables (env.d.ts es referencia de tipos).

4) Backend (carpeta back)
- Archivos clave detectados:
  - back/main.py (entrypoint)
  - back/requirements.txt (dependencias)
  - back/test_api_live.sh (script de pruebas/healthy-checks)
  - back/tests/ (carpeta de pruebas)

- Requisitos recomendados:
  - Python 3.10+
  - pip
  - virtualenv/venv
  - (Opcional) Docker si prefieres contenerizar

- Pasos genéricos para crear entorno e instalar dependencias:
```bash
cd back
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
```

- Ejecutar el servicio backend:
  - Si el proyecto usa un servidor ASGI (por ejemplo FastAPI) y main.py exporta `app`, una alternativa/es estándar:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

- Ejecutar pruebas y chequeos:
```bash
# Ejecutar script de comprobación en el repo (script incluido)
bash test_api_live.sh

# Ejecutar pruebas unitarias (si pytest está configurado)
pytest
```

- Notas:
  - Revisa back/README.md para instrucciones específicas del servicio (ya existe un README en back/).
  - Ajusta puertos y variables de entorno según back/.env o la documentación del servicio.

5) Notebooks / ML (carpeta ml)
- Requisitos:
  - Python 3.10+, JupyterLab/Notebook
  - Instalar dependencias listadas en ml/requirements.txt o un requirements general si existe

- Arranque:
```bash
cd ml
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # si existe
jupyter lab
```

6) Variables de entorno y seguridad
- Revisa `.env` en la raíz. Si contiene valores reales, cámbialos por `.env.example` con placeholders.
- Nunca subir secretos (API keys, credenciales) al repositorio público.
- Para despliegues: usar secretos/variables de entorno de la plataforma (Cloudflare, Supabase, hosting backend).

------------------------------------------------------------
PRUEBAS E INTEGRACIÓN
------------------------------------------------------------
- Documentación de pruebas:
  - QUICK_START_TESTING.md — guía rápida
  - TESTING_INTEGRATION.md — flujo de integración / E2E
- Script detectado: back/test_api_live.sh — script útil para comprobar endpoints en vivo.
- Ejecuta pytest en back/ si hay pruebas unitarias.

------------------------------------------------------------
DESPLIEGUE
------------------------------------------------------------
- Frontend: preparado para Cloudflare Pages (scripts `pages:build`, `deploy`, `preview` con wrangler).
- Backend: se puede contenerizar con Docker; si no, desplegar en VM / servicio que soporte Python (Heroku, GCP Cloud Run, AWS ECS/EKS, etc.).
- ML: modelo/artefactos pueden ser exportados y servidos por el backend o mediante endpoint separado.

------------------------------------------------------------
CONTRIBUCIONES
------------------------------------------------------------
¿Quieres contribuir al proyecto? ¡Excelente! 

**📖 Lee nuestra [Guía de Contribución](CONTRIBUTING.md)** para aprender cómo:
- Hacer un fork del repositorio
- Configurar tu entorno de desarrollo
- Crear ramas de trabajo
- Mantener tu fork actualizado
- Enviar pull requests

**Flujo resumido:**
1. Haz un fork del repositorio en GitHub
2. Clona tu fork localmente
3. Crea una rama: `feature/descripcion` o `fix/descripcion`
4. Haz commits claros y prueba localmente
5. Abre un pull request con descripción detallada

Para instrucciones completas paso a paso en español e inglés, consulta [CONTRIBUTING.md](CONTRIBUTING.md).

------------------------------------------------------------
AUTORES / LICENCIA
------------------------------------------------------------
- Equipo 4 — Hackathon Duoc UC 2025
