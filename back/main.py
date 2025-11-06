from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ml_routes, users_routes, debug_routes

app = FastAPI(
    title="Health AI Backend",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas principales
app.include_router(ml_routes.router, prefix="/api/health", tags=["Health"])
app.include_router(users_routes.router, prefix="/api/users", tags=["Users"])

# 🔍 Ruta de debug Supabase
app.include_router(debug_routes.router, prefix="/api/debug", tags=["Debug"])

@app.get("/")
def root():
    return {"message": "Backend HealthAI activo ✅"}
