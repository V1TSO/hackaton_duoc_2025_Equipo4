from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ml_routes, users_routes, debug_routes, chat_routes # 1. Importar

app = FastAPI(
    title="Health AI Backend (Hackathon NHANES)",
    version="2.0 - Conversational",
)
# Rutas de Chat (El nuevo flujo principal)
app.include_router(
    chat_routes.router,
    prefix="/api/chat", 
    tags=["Chat Agent"]
)

# Rutas de Formulario (El flujo antiguo, se mantiene como "legacy" o para debug)
app.include_router(
    ml_routes.router, 
    prefix="/api/health", 
    tags=["Health (Form-based)"]
)
app.include_router(
    users_routes.router, 
    prefix="/api/users", 
    tags=["Users (Profile & History)"]
)

# Debug
app.include_router(debug_routes.router, prefix="/api/debug", tags=["Debug"])

@app.get("/")
def root():
    return {"message": "Backend HealthAI activo - Arquitectura Conversacional v2.0"}