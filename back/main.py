from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ml_routes, users_routes, debug_routes, chat_routes
import os

app = FastAPI(
    title="Health AI Backend (Hackathon NHANES)",
    version="2.0 - Conversational",
    description="FastAPI backend for health risk prediction and conversational AI coaching",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Allow Next.js frontend origins + localhost for development
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    # Add your Next.js production/preview URLs here:
    # "https://your-nextjs-app.vercel.app",
    # "https://your-custom-domain.com",
]

# In development, allow all origins
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {
        "message": "Backend HealthAI activo - Arquitectura Conversacional v2.0",
        "status": "healthy",
        "version": "2.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "HealthAI Backend"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )