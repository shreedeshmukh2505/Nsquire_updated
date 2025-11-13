# 🚂 Railway Deployment Guide - Step by Step

Follow these steps EXACTLY to deploy your NSquire backend to Railway.

---

## ✅ PRE-DEPLOYMENT CHECKLIST

All these are already done:
- [x] `requirements.txt` created with all Python dependencies
- [x] `railway.toml` configured with start command
- [x] `.env.production` created to disable ESLint warnings
- [x] Flask app configured to use PORT environment variable
- [x] All code pushed to GitHub: https://github.com/shreedeshmukh2505/Nsquire_updated
- [x] Latest commit: bc1c942 "Disable ESLint during production build"

---

## 🎯 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Create New Railway Project (1 minute)**

1. **Open Railway Dashboard**
   - Go to: https://railway.app/dashboard

2. **Create New Project**
   - Click **"New Project"** button (top right)
   - Select **"Deploy from GitHub repo"**

3. **Authorize GitHub** (if needed)
   - If prompted, click "Configure GitHub App"
   - Grant Railway access to your repositories
   - Select "Only select repositories"
   - Choose: **Nsquire_updated**
   - Click "Install & Authorize"

4. **Select Repository**
   - You'll see a list of your repos
   - Click on: **shreedeshmukh2505/Nsquire_updated**

5. **Railway Auto-Detection**
   - Railway will analyze your repo
   - It will detect: Python + Node.js (monorepo)
   - Click **"Deploy Now"**

---

### **STEP 2: Configure Build Settings (1 minute)**

Railway will start building immediately. While it's building:

1. **Click on your service** (in the Railway dashboard)
   - You'll see it's building (blue "Building" status)

2. **Go to Settings Tab**
   - Scroll down to find **"Build"** section
   - Verify these are detected:
     - Builder: **Nixpacks** ✅
     - Build Command: Automatically detected ✅
     - Start Command: `python EDI_project_sql.py` ✅

3. **Root Directory** (Important!)
   - Make sure "Root Directory" is: **/** (root of repo)
   - If it's anything else, change it to `/`

---

### **STEP 3: Add Environment Variables (1 minute)**

**CRITICAL:** Add these WHILE the first build is running (or after it completes):

1. **Click on "Variables" tab**

2. **Add Variable 1 - Cohere API Key**
   - Click **"+ New Variable"**
   - **Variable Name**: `COHERE_API_KEY`
   - **Value**: 'KEY'
   - Click **"Add"**

3. **Add Variable 2 - Flask Environment**
   - Click **"+ New Variable"** again
   - **Variable Name**: `FLASK_ENV`
   - **Value**: `production`
   - Click **"Add"**

4. **DO NOT add PORT variable**
   - Railway automatically provides PORT
   - Your Flask app is already configured to use it

After adding variables, Railway might trigger a rebuild. That's normal!

---

### **STEP 4: Monitor Build (2-3 minutes)**

1. **Go to "Deployments" tab**
   - You'll see the build in progress

2. **Click on the latest deployment** to see logs

3. **Watch for these stages:**
   ```
   ✓ Installing Node.js dependencies (npm ci)
   ✓ Building React app (npm run build)
   ✓ Installing Python dependencies
   ✓ Starting Flask server
   ```

4. **Expected Success:**
   - You'll see: **"Starting NSquire Chatbot with SQL Database..."**
   - Status changes to: **"Active" (green checkmark)** ✅

**If build fails:** Check the logs for errors and let me know!

---

### **STEP 5: Generate Public Domain (30 seconds)**

Once deployment is **Active**:

1. **Go to "Settings" tab**

2. **Scroll to "Networking" section**

3. **Click "Generate Domain"**
   - Railway will create a public URL
   - Format: `https://nsquire-production-xxxx.up.railway.app`

4. **📋 COPY THIS URL!**
   - Save it somewhere - you need it for Vercel
   - Example: `https://newapp-production-a1b2.up.railway.app`

---

### **STEP 6: Test Your Backend (30 seconds)**

1. **Open your Railway URL + /health**
   - Example: `https://your-railway-url.up.railway.app/health`

2. **Expected Response:**
   ```json
   {"status": "ok", "database": "connected"}
   ```

3. **If you see this** ✅
   - Your backend is LIVE!
   - Database is working!
   - Ready for frontend deployment!

4. **If you see an error** ❌
   - Check the "Logs" tab in Railway
   - Look for Python errors
   - Verify environment variables are set

---

## 🎉 SUCCESS CHECKLIST

Before moving to Vercel, verify:
- [ ] Railway deployment shows "Active" status (green)
- [ ] Environment variables COHERE_API_KEY and FLASK_ENV are set
- [ ] Public domain is generated
- [ ] `/health` endpoint returns: `{"status": "ok", "database": "connected"}`
- [ ] You have copied and saved your Railway URL

---

## 🔧 TROUBLESHOOTING

### Problem: Build fails with ESLint errors
**Solution:**
- Check that `.env.production` file exists in repo
- It should contain: `DISABLE_ESLINT_PLUGIN=true`
- If missing, it's already in your latest commit (bc1c942)

### Problem: Build fails with "Cannot find module 'cohere'"
**Solution:**
- Check `requirements.txt` exists in repo root
- Verify it contains: `cohere==4.37`
- Check Railway "Settings" > "Root Directory" is set to `/`

### Problem: Build fails with "Port already in use"
**Solution:**
- This shouldn't happen on Railway
- Verify `EDI_project_sql.py` uses: `port = int(os.environ.get('PORT', 5001))`
- Already configured in your code ✅

### Problem: Deployment succeeds but /health returns 404
**Solution:**
- Check Railway logs for Flask app startup
- Verify Flask app is running: look for "Running on http://0.0.0.0:XXXX"
- Check that `EDI_project_sql.py` has the `/health` route (it does ✅)

### Problem: Database errors in logs
**Solution:**
- Verify `colleges.db` file exists in your repo
- Check it's not in `.gitignore`
- The database should be 488KB

---

## 📊 EXPECTED BUILD TIME

- **Node.js install**: ~15-20 seconds
- **React build**: ~20-30 seconds
- **Python install**: ~30-40 seconds
- **Total**: 2-3 minutes

---

## 🔗 YOUR RAILWAY PROJECT

After setup, you'll have:
- **Project Name**: Nsquire (or whatever you named it)
- **Service**: newapp
- **Repository**: shreedeshmukh2505/Nsquire_updated
- **Branch**: main
- **Public URL**: https://[your-service].up.railway.app

---

## ➡️ NEXT STEP: VERCEL DEPLOYMENT

Once Railway backend is working, proceed to deploy frontend on Vercel.

You'll need:
- Your Railway URL (from Step 5)
- GitHub repository (already connected)

Check `DEPLOYMENT_GUIDE.md` for Vercel deployment steps!

---
