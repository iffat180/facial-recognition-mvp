# Deploy Backend to Render - Complete Guide

## Prerequisites
- GitHub repository with your code pushed
- Render account (sign up at [render.com](https://render.com))

## Step 1: Prepare Backend for Render

The backend is already prepared with:
- ✅ `requirements.txt` with all dependencies
- ✅ `runtime.txt` specifying Python 3.9 (for compatibility)
- ✅ `start.sh` script for deployment
- ✅ FastAPI app configured

**Important**: The `runtime.txt` file specifies Python 3.9 to avoid compatibility issues with newer Python versions.

## Step 2: Create Render Account & Connect GitHub

1. Go to [render.com](https://render.com)
2. Sign up/Login (use **"Sign up with GitHub"** for easiest setup)
3. Authorize Render to access your GitHub repositories

## Step 3: Create New Web Service

1. In Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. You'll see a list of your GitHub repositories
4. Click **"Connect"** next to `facial-recognition-mvp` (or your repo name)

## Step 4: Configure Service Settings

Fill in the following settings:

### Basic Settings:
- **Name**: `facial-recognition-backend` (or your preferred name)
- **Environment**: Select **"Python 3"**
- **Python Version**: **IMPORTANT** - Manually set to `3.9.18` in Render settings (or Render will auto-detect from `runtime.txt` in backend folder)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)

**⚠️ CRITICAL**: If `runtime.txt` isn't detected, manually set Python version:
1. After creating service, go to **Settings** → **Environment**
2. Add environment variable: `PYTHON_VERSION` = `3.9.18`
3. Or in **Build & Deploy** settings, specify Python version directly

### ⚠️ CRITICAL: Root Directory
- **Root Directory**: `backend` 
  - This tells Render where your backend code is located
  - Without this, Render will look in the root directory and fail

### Build & Start Commands:
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
  
- **Start Command**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
  - Or use the start script:
  ```bash
  chmod +x start.sh && ./start.sh
  ```

### Instance Type:
- **Free**: 512MB RAM (sufficient for MVP)
- **Starter**: $7/month (if you need more resources)

## Step 5: Set Python Version (CRITICAL!)

**⚠️ IMPORTANT**: Render might not auto-detect `runtime.txt`. You MUST manually set Python version:

### Option A: In Service Settings (Recommended)
1. After creating the service, go to **Settings** tab
2. Scroll to **"Build & Deploy"** section
3. Find **"Python Version"** field
4. Enter: `3.9.18` or just `3.9`
5. Click **"Save Changes"**
6. Render will redeploy automatically

### Option B: Environment Variable
1. Go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Key: `PYTHON_VERSION`
4. Value: `3.9.18`
5. Click **"Save Changes"**

**Note**: The `runtime.txt` file in the `backend/` folder should work, but if Render still uses Python 3.13, manually set it as above.

## Step 6: Deploy

1. Scroll down and click **"Create Web Service"**
2. Render will start building your service
3. You'll see build logs in real-time
4. First deployment takes **5-10 minutes** (installing dependencies, downloading DeepFace models)

## Step 7: Get Your Backend URL

Once deployment completes:
- Your backend will be available at: `https://facial-recognition-backend.onrender.com`
- Copy this URL - you'll need it for the frontend

## Step 8: Update CORS Settings

After deployment, update your backend to allow requests from your frontend:

1. Edit `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-frontend-app.vercel.app",  # Your Vercel frontend URL
        "https://facial-recognition-backend.onrender.com"  # Your Render backend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Commit and push:
```bash
git add backend/app/main.py
git commit -m "Update CORS for production deployment"
git push origin main
```

3. Render will automatically redeploy (if auto-deploy is enabled)

## Step 9: Update Frontend to Use Render Backend

### Option A: Environment Variable (Recommended)

1. Go to your Vercel project dashboard
2. Settings → Environment Variables
3. Add:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://facial-recognition-backend.onrender.com`
   - **Environment**: Production, Preview, Development
4. Redeploy your Vercel app

### Option B: Update Code Directly

Edit `frontend/src/api/faceRecognition.ts`:
```typescript
const API_BASE = process.env.REACT_APP_API_URL || 'https://facial-recognition-backend.onrender.com';
```

## Step 10: Test Your Deployment

1. **Test Backend**: Visit `https://facial-recognition-backend.onrender.com/`
   - Should see: `{"message":"Face Recognition MVP API","version":"1.0.0",...}`

2. **Test Frontend**: Visit your Vercel URL
   - Try enrolling a face
   - Check browser console for any errors

## Important Notes

### Render Free Tier Limitations:
- ⚠️ **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30 seconds (cold start)
- 512MB RAM limit
- 100GB bandwidth/month

### Storage:
- ⚠️ **Ephemeral storage**: The `face_data/` directory is lost on redeploy
- For production, consider:
  - Render Disk (persistent storage)
  - AWS S3
  - Google Cloud Storage
  - Database for embeddings

### Monitoring:
- Check **"Logs"** tab in Render dashboard for errors
- Check **"Metrics"** tab for performance
- Set up **"Health Checks"** if needed

### Troubleshooting:

**Build fails:**
- Check build logs in Render dashboard
- Ensure `requirements.txt` is correct
- Verify Python version compatibility

**Service won't start:**
- Check start command is correct
- Verify `app.main:app` path
- Check logs for error messages

**CORS errors:**
- Ensure frontend URL is in `allow_origins` list
- Check that backend URL is correct in frontend

**Slow first request:**
- Normal on free tier (cold start)
- Consider upgrading to paid tier for always-on service

## Quick Reference

**Render Dashboard**: https://dashboard.render.com
**Your Backend URL**: `https://facial-recognition-backend.onrender.com`
**API Docs**: `https://facial-recognition-backend.onrender.com/docs` (Swagger UI)

## Next Steps

1. ✅ Backend deployed to Render
2. ✅ Frontend deployed to Vercel
3. ✅ CORS configured
4. ✅ API URL updated in frontend
5. 🎉 Your app is live!
