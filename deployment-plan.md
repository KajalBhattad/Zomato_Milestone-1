# Deployment Plan — Zomato Milestone 1

## Architecture Overview

```
┌────────────────────────┐         ┌──────────────────────────────┐
│     Vercel             │  HTTP   │     Railway                  │
│  (Static Frontend)     │ ──────► │  (FastAPI Backend)           │
│  src/static/index.html │         │  POST /api/v1/recommend      │
│                        │ ◄────── │  GET  /api/v1/health         │
└────────────────────────┘         └──────────────────────────────┘
                                              │
                                              │ Loads at startup
                                              ▼
                                   HuggingFace Dataset
                                   (ManikaSaini/zomato-...)
```

The frontend (`src/static/index.html`) is a standalone HTML/CSS/JS file deployed to **Vercel**.  
The backend (`src/main.py` FastAPI app) runs on **Railway** and exposes the REST API.

---

## Step 1 — Prepare the Backend for Railway

### 1a. Add CORS Middleware to `src/main.py`

Railway will serve the API on a different domain than Vercel, so the backend must allow cross-origin requests.

Add `CORSMiddleware` after the app is created in `src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],  # Replace with your actual Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **Tip:** During initial testing you can set `allow_origins=["*"]` to allow all origins, then lock it down to your Vercel URL once deployed.

### 1b. Create a `Procfile` at the Project Root

Railway uses `Procfile` to know how to start the app.

```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### 1c. Ensure `requirements.txt` Is Up to Date

Your current `requirements.txt` already includes all runtime dependencies. Make sure `uvicorn` is listed (it is). Remove `pytest` from the production requirements or move it to a `requirements-dev.txt`:

```
# requirements.txt (production only)
groq>=0.9.0
datasets>=2.19.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.1
fastapi>=0.111.0
uvicorn>=0.30.0
streamlit>=1.35.0

# requirements-dev.txt
pytest>=8.2.0
```

---

## Step 2 — Prepare the Frontend for Vercel

### 2a. Update the API Base URL in `src/static/index.html`

After Railway deployment, your backend will have a public URL like `https://your-app.up.railway.app`. You need to update the frontend's API calls to point to this URL instead of relative paths.

Find all `fetch('/api/v1/...')` calls in `src/static/index.html` and change them to use the full Railway URL:

```js
// Before (relative path — only works when served by FastAPI)
const response = await fetch('/api/v1/recommend', { ... });

// After (absolute Railway URL)
const API_BASE = "https://your-railway-app.up.railway.app";
const response = await fetch(`${API_BASE}/api/v1/recommend`, { ... });
```

Define `API_BASE` as a constant at the top of the `<script>` block so it's easy to update.

### 2b. Create a `vercel.json` at the Project Root

Tell Vercel where the static frontend lives and set up clean routing:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/static/index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "src/static/index.html"
    }
  ]
}
```

---

## Step 3 — Deploy the Backend to Railway

1. **Push your code to GitHub** (if not already done).

2. **Go to [railway.app](https://railway.app)** → New Project → Deploy from GitHub Repo → select `zomato-milestone1`.

3. **Set Environment Variables** in Railway dashboard under _Variables_:

   | Variable | Value |
   |---|---|
   | `GROQ_API_KEY` | Your Groq API key |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` |
   | `GROQ_TEMPERATURE` | `0.3` |
   | `HF_DATASET_NAME` | `ManikaSaini/zomato-restaurant-recommendation` |
   | `MAX_CANDIDATES` | `30` |
   | `TOP_K_RESULTS` | `5` |
   | `BUDGET_LOW_MAX` | `500` |
   | `BUDGET_MEDIUM_MAX` | `1500` |

4. Railway will auto-detect Python and the `Procfile`, then build and deploy.

5. **Copy the generated Railway URL** — you'll need it for the frontend (e.g., `https://zomato-milestone1.up.railway.app`).

6. **Verify the backend is healthy**:
   ```
   GET https://your-railway-app.up.railway.app/api/v1/health
   ```
   Expected response:
   ```json
   { "status": "healthy", "cache_initialized": true, "groq_configured": true }
   ```

---

## Step 4 — Deploy the Frontend to Vercel

1. **Update the `API_BASE` URL** in `src/static/index.html` with your Railway URL from Step 3.

2. **Commit and push** the changes.

3. **Go to [vercel.com](https://vercel.com)** → New Project → Import Git Repository → select `zomato-milestone1`.

4. **Configure the project**:
   - Framework Preset: **Other**
   - Root Directory: leave as `/` (the `vercel.json` handles routing)
   - No build command needed (static file)

5. Click **Deploy**. Vercel will provide a public URL like `https://zomato-milestone1.vercel.app`.

6. **Update CORS in `src/main.py`** — replace `"*"` with your actual Vercel URL:
   ```python
   allow_origins=["https://zomato-milestone1.vercel.app"],
   ```
   Redeploy on Railway (it auto-redeploys on git push).

---

## Step 5 — Verify End-to-End

Test the full flow from your Vercel frontend:

1. Open your Vercel URL in the browser.
2. Submit a restaurant recommendation request via the UI.
3. Check the browser's Network tab — the `POST /api/v1/recommend` call should go to your Railway URL and return a `200 OK` with recommendations.

---

## Files Changed / Created

| File | Action | Purpose |
|---|---|---|
| `src/main.py` | Modify | Add `CORSMiddleware` |
| `Procfile` | Create | Tells Railway how to start the app |
| `vercel.json` | Create | Tells Vercel where the static frontend is |
| `src/static/index.html` | Modify | Replace relative API paths with Railway URL |
| `requirements.txt` | Modify (optional) | Remove `pytest` from prod dependencies |
| `requirements-dev.txt` | Create (optional) | Dev-only dependencies |

---

## Environment Variables Reference

### Railway (Backend)

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key from console.groq.com |
| `GROQ_MODEL` | No | Defaults to `llama-3.3-70b-versatile` |
| `GROQ_TEMPERATURE` | No | Defaults to `0.3` |
| `HF_DATASET_NAME` | No | HuggingFace dataset path |
| `MAX_CANDIDATES` | No | Filter candidate pool size (default: 30) |
| `TOP_K_RESULTS` | No | Number of final results (default: 5) |
| `BUDGET_LOW_MAX` | No | Low budget threshold in INR (default: 500) |
| `BUDGET_MEDIUM_MAX` | No | Medium budget threshold in INR (default: 1500) |

### Vercel (Frontend)

No server-side environment variables needed — the frontend is fully static. The Railway URL is hardcoded in `index.html`.

---

## Important Notes

- The HuggingFace dataset is **downloaded at startup** by `initialize_cache()`. Railway's free tier may be slow on the first cold start. Consider upgrading to a paid plan if cold-start times are too long.
- `.env` is in `.gitignore` and will **not** be pushed — configure all secrets via Railway's environment variable dashboard.
- Railway's free tier provides 500 hours/month. For a production app, consider the Hobby plan.
- Vercel's free (Hobby) plan is sufficient for this static frontend.
