---
title: HealthAI Backend API
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# HealthAI Backend

FastAPI backend for health risk prediction and conversational AI coaching, powered by ML models and RAG system.

## Stack
- **FastAPI** - REST API framework
- **Supabase** - Authentication & Database
- **OpenAI** - Conversational AI coach
- **XGBoost** - ML prediction models
- **RAG System** - Knowledge base with BM25 retrieval

## Features
- 🤖 Conversational health coaching with OpenAI
- 📊 Cardiovascular risk prediction (ML models)
- 💬 Chat history with sliding window management
- 🔍 RAG-based knowledge retrieval
- 🔐 Supabase authentication
- 📈 User health profile tracking

## API Endpoints

### Chat
- `POST /api/chat/message` - Send message to conversational agent
- `GET /api/chat/history/{user_id}` - Get chat history

### Health Predictions
- `POST /api/health/predict-form` - Form-based risk prediction
- `GET /api/health/history/{user_id}` - Prediction history

### Users
- `GET /api/users/profile/{user_id}` - Get user profile
- Various user management endpoints

### Debug
- `GET /api/debug/kb-info` - Knowledge base statistics
- `POST /api/debug/rag-search` - Test RAG search

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (see .env.example)
cp .env.example .env
# Edit .env with your actual credentials

# Run locally
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

Interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Deployment to HuggingFace Spaces

### Prerequisites
1. HuggingFace account
2. GitHub repository with this code
3. Required API keys (Supabase, OpenAI)

### Step-by-Step Deployment

#### 1. Prepare Your Repository
Ensure your repository has:
- ✅ `Dockerfile` (configured for port 7860)
- ✅ `requirements.txt` (all dependencies)
- ✅ `README.md` with HuggingFace metadata (YAML frontmatter)
- ✅ `.dockerignore` (excludes venv, cache files)
- ✅ ML models in `app/ml/models/`

#### 2. Create a New Space
1. Go to https://huggingface.co/new-space
2. Choose a name for your Space (e.g., `your-username/healthai-backend`)
3. Select **Docker** as the SDK
4. Choose visibility (Public or Private)
5. Click "Create Space"

#### 3. Link to GitHub Repository
**Option A: Direct Git Push**
```bash
# Add HuggingFace remote
git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME

# Push to HuggingFace
git push hf main
```

**Option B: GitHub Sync**
1. In your Space settings, enable GitHub sync
2. Connect your GitHub repository
3. Changes pushed to GitHub will auto-deploy to HuggingFace

#### 4. Configure Environment Variables
In your Space settings (⚙️ Settings > Variables and Secrets):

Add these variables:
```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_ANON_KEY = your-anon-key-here
OPENAI_API_KEY = sk-your-openai-api-key
ENVIRONMENT = production
```

**Important**: Mark sensitive keys as **Secrets** (🔒 icon) to hide them from logs.

Optional variables:
```
COLAB_URL = (if using external ML service)
TOKEN_BUDGET_TOTAL = 8000
TOKEN_BUDGET_HISTORY_PCT = 0.30
TOKEN_BUDGET_RAG_PCT = 0.70
SLIDING_WINDOW_SIZE = 10
```

#### 5. Monitor Build Status
- Your Space will automatically build using the Dockerfile
- Check the "Build" tab for logs and progress
- First build may take 5-10 minutes
- Once complete, status will show "Running"

#### 6. Test Your Deployment
Your API will be available at:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
```

Test the health check:
```bash
curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
```

Access API documentation:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs
```

### Troubleshooting

**Build Fails**
- Check build logs in the "Build" tab
- Verify all dependencies in `requirements.txt`
- Ensure ML model files exist in `app/ml/models/`

**Environment Variables Not Working**
- Restart the Space after adding variables
- Check variable names match exactly (case-sensitive)
- Verify secrets are marked correctly

**CORS Errors from Frontend**
- Update `allowed_origins` in `main.py` with your frontend URL
- Or set `ENVIRONMENT=development` to allow all origins (not recommended for production)

## Next.js Frontend Integration

### 1. Update CORS Origins
In `main.py`, add your Next.js deployment URLs:

```python
allowed_origins = [
    "http://localhost:3000",
    "https://your-nextjs-app.vercel.app",  # Add your production URL
    "https://preview-123-your-app.vercel.app",  # Preview deployments
]
```

### 2. Configure API Client
Create an API client in your Next.js app:

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
                     'https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space';

export async function sendChatMessage(userId: string, message: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send message');
  }
  
  return response.json();
}

export async function getHealthPrediction(data: any) {
  const response = await fetch(`${API_BASE_URL}/api/health/predict-form`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
}
```

### 3. Environment Variables (Next.js)
Add to your `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
```

### 4. Example Usage

```typescript
// components/ChatInterface.tsx
import { sendChatMessage } from '@/lib/api';

export function ChatInterface({ userId }: { userId: string }) {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');

  const handleSend = async () => {
    try {
      const result = await sendChatMessage(userId, message);
      setResponse(result.response);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <input 
        value={message} 
        onChange={(e) => setMessage(e.target.value)} 
      />
      <button onClick={handleSend}>Send</button>
      <p>{response}</p>
    </div>
  );
}
```

## API Testing Examples

### Chat Message
```bash
curl -X POST "https://YOUR-SPACE.hf.space/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "message": "What are the risk factors for heart disease?"
  }'
```

### Health Prediction
```bash
curl -X POST "https://YOUR-SPACE.hf.space/api/health/predict-form" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "sex": "M",
    "bmi": 28.5,
    "smoking": true
  }'
```

### Get Chat History
```bash
curl "https://YOUR-SPACE.hf.space/api/chat/history/test-user-123"
```

## Production Checklist

Before deploying to production:

- [ ] Update CORS origins with actual frontend URLs
- [ ] Set `ENVIRONMENT=production` in Space settings
- [ ] Verify all environment secrets are configured
- [ ] Test all API endpoints with production URLs
- [ ] Set up monitoring/logging (HuggingFace provides basic logs)
- [ ] Document API URL for frontend team
- [ ] Test error handling and rate limiting
- [ ] Verify ML models are included in deployment
- [ ] Test Supabase connection and authentication

## Support & Resources

- **HuggingFace Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **API Documentation**: `/docs` endpoint on your deployed Space
