# Deployment Guide: GitHub + Vercel

## Step 1: Initialize Git Repository

```bash
# Navigate to project root
cd /Users/iffat180/Desktop/facial-recognition

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Face Recognition MVP with React frontend and FastAPI backend"
```

## Step 2: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository settings:
   - **Repository name**: `facial-recognition-mvp` (or your preferred name)
   - **Description**: "Face Recognition MVP with React frontend and FastAPI backend"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 3: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/facial-recognition-mvp.git

# Rename main branch if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 4: Deploy Frontend to Vercel

### Option A: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in (use GitHub account)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository:
   - Select `facial-recognition-mvp` from the list
   - Click **"Import"**
4. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend` (IMPORTANT!)
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`
5. Environment Variables (if needed):
   - Add `REACT_APP_API_URL` = `http://localhost:8000` (for local testing)
   - Or your backend URL if deploying backend separately
6. Click **"Deploy"**

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? facial-recognition-mvp
# - Directory? ./
# - Override settings? No
```

## Step 5: Update API URL for Production

After deploying, you'll need to update the API URL in the frontend:

1. **For Vercel deployment**, create a `vercel.json` in the `frontend` directory:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.herokuapp.com/:path*"
    }
  ]
}
```

2. **Or update `frontend/src/api/faceRecognition.ts`**:

```typescript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

3. **Add environment variable in Vercel**:
   - Go to Project Settings → Environment Variables
   - Add `REACT_APP_API_URL` = `https://your-backend-url.com`

## Step 6: Deploy Backend (Optional - for full stack)

The backend needs to be deployed separately. Options:

### Option A: Railway
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repository
4. Set root directory to `backend`
5. Add build command: `pip install -r requirements.txt`
6. Add start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option B: Render
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### Option C: Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `cd backend`
4. `heroku git:remote -a your-app-name`
5. `git push heroku main`

## Important Notes

1. **CORS Configuration**: Update `backend/app/main.py` to allow your Vercel domain:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:3001",
       "https://your-app.vercel.app"  # Add your Vercel URL
   ]
   ```

2. **Environment Variables**: Never commit `.env` files. Use Vercel/Railway environment variables.

3. **Build Output**: The frontend build is in `frontend/build/` - Vercel will use this.

4. **Backend Storage**: The `face_data/` directory won't persist on most platforms. Consider using cloud storage (S3, etc.) for production.

## Quick Commands Reference

```bash
# Git commands
git status
git add .
git commit -m "Your commit message"
git push origin main

# Vercel CLI
vercel                    # Deploy to preview
vercel --prod            # Deploy to production
vercel env add REACT_APP_API_URL  # Add environment variable
```

## Troubleshooting

- **Build fails**: Check that `frontend` is set as root directory in Vercel
- **API errors**: Ensure CORS allows your Vercel domain
- **Environment variables**: Make sure they're set in Vercel dashboard
- **Backend not accessible**: Check that backend is deployed and URL is correct
