# Conectar Frontend con Backend en Hugging Face Spaces

## 🔗 URLs del Backend

### URL del Space (página web)
```
https://huggingface.co/spaces/v1tso/cardiosense
```

### URL de la API (para llamadas HTTP)
```
https://v1tso-cardiosense.hf.space
```

**Formato general**: `https://{username}-{spacename}.hf.space`

---

## ✅ Configuración Actualizada

### 1. **client.ts** - Ya actualizado ✓

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://v1tso-cardiosense.hf.space";
```

### 2. **.env.local** - Ya actualizado ✓

```bash
# Backend API URL - Hugging Face Spaces
NEXT_PUBLIC_API_URL=https://v1tso-cardiosense.hf.space

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://chifwmdrktbewbodsobs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Availability
NEXT_PUBLIC_API_AVAILABLE=true
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Desarrollo Local (Conectado a HF Backend)

```bash
cd front
npm run dev
```

Abre: http://localhost:3000

**El frontend local se conectará automáticamente al backend en Hugging Face Spaces**

---

### Opción 2: Verificar Backend en Hugging Face

Antes de probar el frontend, verifica que el backend esté funcionando:

#### a) Verificar Status
```bash
curl https://v1tso-cardiosense.hf.space/
```

**Respuesta esperada**:
```json
{
  "status": "ok",
  "message": "HealthAI Backend API"
}
```

#### b) Verificar Health Endpoint
```bash
curl https://v1tso-cardiosense.hf.space/health
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "timestamp": "2025-11-07T..."
}
```

#### c) Verificar Docs de la API
Abre en tu navegador:
```
https://v1tso-cardiosense.hf.space/docs
```

Deberías ver la documentación interactiva de FastAPI (Swagger UI).

---

## 🧪 Probar la Conexión

### Test 1: Desde el Frontend

1. Ejecuta el frontend:
   ```bash
   npm run dev
   ```

2. Abre: http://localhost:3000

3. Ve al Chat (`/chat`)

4. Envía un mensaje: "Hola, quiero evaluar mi riesgo cardiovascular"

5. **Resultado esperado**:
   - El chatbot responde
   - Te hace preguntas para recolectar datos
   - Al completar, genera una predicción usando el modelo en HF Spaces

---

### Test 2: Verificar Network Requests

1. Abre DevTools (F12) en tu navegador

2. Ve a la pestaña **Network**

3. Envía un mensaje en el chat

4. **Deberías ver**:
   - Request a: `https://v1tso-cardiosense.hf.space/api/chat/message`
   - Status: `200 OK`
   - Response: JSON con la respuesta del chatbot

---

## 🔧 Troubleshooting

### Problema 1: CORS Error

**Error**:
```
Access to fetch at 'https://v1tso-cardiosense.hf.space/api/chat/message' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solución**: Verifica que el backend tenga CORS configurado para permitir `localhost:3000`

Chequea en `back/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Problema 2: Backend dormido (Space Sleeping)

**Error**: Timeout o error 503

**Solución**: 
1. Ve a: https://huggingface.co/spaces/v1tso/cardiosense
2. Si el Space está "sleeping", haz clic en **"Restart"**
3. Espera 1-2 minutos a que se inicie
4. Intenta de nuevo

---

### Problema 3: Variables de entorno no configuradas

Si el backend da error 503 al iniciar:

1. Ve a: https://huggingface.co/spaces/v1tso/cardiosense/settings
2. Scroll a **"Repository secrets"**
3. Añade (si no están):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `OPENAI_API_KEY`
4. Reinicia el Space

---

## 📊 Endpoints Disponibles

### 1. Chat Conversacional
```
POST https://v1tso-cardiosense.hf.space/api/chat/message
```

**Body**:
```json
{
  "content": "Hola, quiero evaluar mi riesgo",
  "session_id": "uuid-or-null"
}
```

---

### 2. Predicción Directa (Legacy)
```
POST https://v1tso-cardiosense.hf.space/api/predict
```

**Body**:
```json
{
  "edad": 45,
  "genero": "M",
  "imc": 27.5,
  "presion_sistolica": 130,
  "colesterol_total": 200,
  "tabaquismo": false,
  "actividad_fisica": "moderado",
  "horas_sueno": 7
}
```

---

## 🌐 Alternar entre Local y HF Backend

### Usar Backend Local (Desarrollo)

```bash
# En .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Usar Backend en Hugging Face (Producción)

```bash
# En .env.local
NEXT_PUBLIC_API_URL=https://v1tso-cardiosense.hf.space
```

**Nota**: Después de cambiar `.env.local`, reinicia el servidor de Next.js:
```bash
# Ctrl+C para detener
npm run dev
```

---

## ✅ Checklist de Verificación

- [ ] Backend funcionando en HF Spaces: https://v1tso-cardiosense.hf.space/
- [ ] Endpoint `/docs` accesible: https://v1tso-cardiosense.hf.space/docs
- [ ] Variables de entorno configuradas en HF Spaces (Settings > Secrets)
- [ ] `.env.local` actualizado con la URL correcta
- [ ] Frontend corriendo: `npm run dev`
- [ ] Chat responde correctamente
- [ ] Predicciones funcionando sin errores
- [ ] Network tab muestra requests a `v1tso-cardiosense.hf.space`

---

## 🎉 ¡Todo Listo!

Tu stack completo:
- **Frontend**: http://localhost:3000 (Next.js)
- **Backend**: https://v1tso-cardiosense.hf.space (FastAPI en HF Spaces)
- **Database**: Supabase
- **ML Models**: Diabetes + Cardiovascular (en HF Space)
- **AI Chat**: OpenAI GPT-4o-mini con RAG

¡Tu aplicación está completamente conectada! 🚀

