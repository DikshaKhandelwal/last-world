# Deployment Guide: Render + Vercel

## Prerequisites

- GitHub repository (push your code to GitHub first)
- Render account: https://render.com
- Vercel account: https://vercel.com
- Groq API key (optional, for fallback inference)

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Backend for Deployment

1. Create `backend/.env.production`:
   ```
   INFERENCE_MODE=groq
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   ```

2. Ensure `backend/requirements.txt` is up to date:
   ```bash
   cd backend
   pip freeze > requirements.txt
   ```

3. Verify `backend/main.py` runs on port 8000 (default).

### Step 2: Create Render Web Service

1. Go to https://render.com/dashboard and click **New → Web Service**
2. Connect your GitHub repository
3. Fill in the configuration:
   - **Name**: `last-model-backend`
   - **Environment**: `Python 3.11`
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```
     cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
     ```
   - **Instance Type**: Free (or Starter for production)

### Step 3: Set Environment Variables on Render

1. In the Render dashboard, go to **Environment → Environment Variables**
2. Add:
   - `INFERENCE_MODE` = `groq`
   - `GROQ_API_KEY` = (paste your key from Groq)
   - `GROQ_MODEL` = `llama-3.1-8b-instant`
   - `CORS_ORIGINS` = `https://your-vercel-frontend-url.vercel.app` (add after deploying frontend)

3. Click **Deploy Web Service**
4. Wait for build to complete (~3-5 minutes)
5. Note your backend URL: `https://last-model-backend.onrender.com`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend for Deployment

1. Update API URL in `frontend/src/lib/api.js`:
   ```javascript
   const API_BASE = process.env.REACT_APP_API_URL || 'https://last-model-backend.onrender.com'
   ```

2. Update `frontend/.env.production`:
   ```
   VITE_API_URL=https://last-model-backend.onrender.com
   ```

3. Verify `frontend/package.json` has:
   ```json
   {
     "scripts": {
       "build": "vite build",
       "preview": "vite preview"
     }
   }
   ```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login:
   ```bash
   vercel login
   ```

3. Deploy from project root:
   ```bash
   vercel --prod
   ```

4. Follow prompts:
   - Link to existing project or create new
   - Set root directory to `./frontend`
   - Configure build settings (Vercel auto-detects Vite)

#### Option B: Using GitHub Integration (Recommended)

1. Go to https://vercel.com/new
2. Select **GitHub** and authorize GitHub access
3. Choose your `last_model` repository
4. Configure:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variables:
   - `VITE_API_URL` = `https://last-model-backend.onrender.com`

6. Click **Deploy**
7. Note your frontend URL: `https://last-model-xxx.vercel.app`

### Step 3: Update Backend CORS Origin

1. Go back to Render dashboard
2. Go to **Environment → Environment Variables**
3. Update `CORS_ORIGINS`:
   ```
   https://last-model-xxx.vercel.app
   ```
4. Click **Redeploy**

---

## Part 3: Testing Deployment

1. Open your Vercel frontend URL
2. Test Level 1 (Code Review):
   - Go to game start
   - Upload one of the sample files from `samples/`
   - Verify the backend responds with analysis

3. Check browser console for API errors
4. Monitor Render logs via dashboard

---

## Part 4: Custom Domain (Optional)

### For Vercel:
1. Go to Vercel Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration steps

### For Render:
1. Go to Render Service Settings → Custom Domain
2. Add domain and follow DNS steps

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway on Render | Check backend logs in Render dashboard; ensure `START_COMMAND` is correct |
| CORS errors | Verify `CORS_ORIGINS` on Render matches your Vercel URL exactly |
| Frontend can't reach backend | Check `VITE_API_URL` is correct in Vercel environment variables |
| Build fails on Vercel | Run `npm run build` locally in `frontend/` to debug |
| Build fails on Render | Run `pip install -r backend/requirements.txt` locally to verify |

---

## Monitoring

- **Render**: Dashboard → Logs tab
- **Vercel**: Project → Deployments → View logs for each deployment

---

## Environment Variables Checklist

### Render (Backend)
- [ ] `INFERENCE_MODE=groq`
- [ ] `GROQ_API_KEY=...`
- [ ] `GROQ_MODEL=llama-3.1-8b-instant`
- [ ] `CORS_ORIGINS=https://...vercel.app`

### Vercel (Frontend)
- [ ] `VITE_API_URL=https://...onrender.com`

---

## Rollback

- **Vercel**: Click a previous deployment in the Deployments tab
- **Render**: Click previous deploys in the Render dashboard

---

## Cost Notes

- **Render Free Tier**: Spins down after 15 min of inactivity (cold start ~30s)
- **Vercel Free Tier**: Unlimited serverless functions, good for production
- **Groq API**: Free tier available, check pricing for scale

For persistent backend on Render, upgrade to **Starter** ($7/mo).
