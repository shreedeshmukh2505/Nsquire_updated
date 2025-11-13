# 🚀 NSquire Deployment Guide

Your code is ready for deployment! Follow these simple steps:

---

## ✅ Steps:

- [x] Create `requirements.txt` for Python dependencies
- [x] Create `railway.toml` for Railway configuration
- [x] Update Flask app for production (PORT configuration)
- [x] Create centralized API config (`src/config.js`)
- [x] Update all React components to use environment variables
- [x] Push code to GitHub: https://github.com/shreedeshmukh2505/Nsquire_updated
- [x] Initiate Railway deployment

---

## 🚂 STEP 1: Complete Railway Backend Deployment (5 minutes)

### 1.1 Open Railway Dashboard
Go to: **https://railway.app/project/55f7ac8d-2839-4962-af2a-223d063793b2**

### 1.2 Select Your Service
- You should see your "Nsquire" project
- Click on the service that's deploying

### 1.3 Add Environment Variables
Click on **"Variables"** tab and add:

```
Variable Name: COHERE_API_KEY
Value: YOUR_API_KEY
```

```
Variable Name: FLASK_ENV
Value: production
```

Click **"Add"** for each variable.

### 1.4 Generate Public Domain
- Click on **"Settings"** tab
- Scroll to **"Networking"** section
- Click **"Generate Domain"**
- You'll get a URL like: `https://something.up.railway.app`

**🎯 IMPORTANT: Copy this URL! You'll need it for Vercel.**

### 1.5 Check Deployment Status
- Go to **"Deployments"** tab
- Wait for the build to complete (green checkmark)
- Test the backend: Visit `https://your-railway-url.up.railway.app/health`
- You should see: `{"status": "ok", "database": "connected"}`

---

## ▲ STEP 2: Deploy Frontend to Vercel (5 minutes)

### 2.1 Go to Vercel Dashboard
Visit: **https://vercel.com/new**

### 2.2 Import Git Repository
- Click **"Add New..."** → **"Project"**
- Choose **"Import Git Repository"**
- Select: **username/NSquire**
- Click **"Import"**

### 2.3 Configure Project
Vercel will auto-detect settings. Verify:

- **Framework Preset**: Create React App ✅
- **Root Directory**: `./` ✅
- **Build Command**: `npm run build` ✅
- **Output Directory**: `build` ✅
- **Install Command**: `npm install` ✅

### 2.4 Add Environment Variable
**CRITICAL STEP:**

In **"Environment Variables"** section:
- **Name**: `REACT_APP_API_URL`
- **Value**: `https://your-railway-url.up.railway.app` (use YOUR Railway URL from Step 1.4)
- **Environments**: Check all three (Production, Preview, Development)

Click **"Add"**

### 2.5 Deploy
Click **"Deploy"**

Vercel will:
1. Clone your repository ⏳
2. Install npm dependencies ⏳
3. Build React app ⏳
4. Deploy to global CDN ⏳

Wait 2-3 minutes for deployment to complete.

### 2.6 Get Your Live URL
Once deployed, you'll see:
- **🎉 Congratulations!**
- Your live URL: `https://nsquire-updated.vercel.app` (or similar)

---

## 🧪 STEP 3: Test Your Deployment

### 3.1 Test Backend (Railway)
Open your Railway URL: `https://your-railway-url.up.railway.app/health`

✅ Expected: `{"status": "ok", "database": "connected"}`

### 3.2 Test Frontend (Vercel)
Open your Vercel URL: `https://your-app.vercel.app`

Test all features:
1. **Chatbot** - Ask: "What is the cutoff for PICT Computer Engineering?"
2. **Rank Predictor** - Enter rank: 10000, Category: GOPEN
3. **College Comparison** - Compare 2-3 colleges
4. **College Search** - Search for colleges by location/branch

---

## 🎯 DEPLOYMENT ARCHITECTURE

```
User's Browser
     ↓
[Vercel - Frontend]
  └─ React App on Global CDN
  └─ URL: https://your-app.vercel.app
     ↓ API Calls
[Railway - Backend]
  └─ Flask API + ML Models
  └─ SQLite Database (Persistent)
  └─ URL: https://your-backend.up.railway.app
```

---

## 🔧 TROUBLESHOOTING

### Issue: Frontend shows "Network Error"
**Solution:**
1. Check if `REACT_APP_API_URL` is set correctly in Vercel
2. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
3. Verify the URL matches your Railway domain
4. Redeploy: Deployments tab → Click "..." → "Redeploy"

### Issue: Railway deployment failed
**Solution:**
1. Check Railway logs: Dashboard → Deployments → Click on deployment → View logs
2. Ensure environment variables are set correctly
3. Verify `requirements.txt` and `railway.toml` are in the repository

### Issue: Database not found
**Solution:**
1. Ensure `colleges.db` is committed to git
2. Check Railway logs for database-related errors
3. Railway should automatically persist the SQLite file

### Issue: CORS errors in browser
**Solution:**
Already configured! Your Flask app allows all origins. If you want to restrict:
1. Edit `EDI_project_sql.py` line 1063
2. Change `origins: "*"` to `origins: ["https://your-vercel-url.vercel.app"]`
3. Commit and push to trigger redeployment

---

## 💰 COST BREAKDOWN

### Railway (Backend)
- **Free Tier**: $5 monthly credit
- **Usage**: ~$5-10/month for light traffic
- **Limit**: ~500 execution hours/month
- **Upgrade**: Add payment method if you exceed

### Vercel (Frontend)
- **Free Tier**: 100GB bandwidth/month
- **Usage**: FREE for most projects
- **Limit**: ~100,000 page views/month
- **Upgrade**: $20/month for Pro (only if needed)

**Total Cost for Normal Usage: $0-5/month** 🎉

---

## 📊 MONITORING

### Railway Dashboard
- **Logs**: View real-time logs for debugging
- **Metrics**: CPU, Memory, Network usage
- **URL**: https://railway.app/dashboard

### Vercel Dashboard
- **Analytics**: Page views, performance
- **Deployments**: Git-based deployments
- **URL**: https://vercel.com/dashboard

---

## 🔄 FUTURE DEPLOYMENTS

Every time you push to GitHub:
- **Railway**: Auto-redeploys backend (if enabled)
- **Vercel**: Auto-redeploys frontend automatically

To enable auto-deploy on Railway:
1. Go to Settings
2. Enable "Automatic Deployments"

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Railway environment variables set (COHERE_API_KEY, FLASK_ENV)
- [ ] Railway public domain generated
- [ ] Railway deployment successful (green checkmark)
- [ ] Railway health check works (`/health` endpoint)
- [ ] Vercel environment variable set (REACT_APP_API_URL)
- [ ] Vercel deployment successful
- [ ] Frontend loads correctly
- [ ] Chatbot works
- [ ] Rank Predictor works
- [ ] College Comparison works
- [ ] College Search works

---

## 🎓 YOUR DEPLOYED URLs

Once complete, you'll have:

**Frontend (Vercel):**
`https://__________.vercel.app`

**Backend (Railway):**
`https://__________.up.railway.app`

**GitHub Repository:**
https://github.com/username/Nsquire_updated

---

## 🆘 NEED HELP?

If you encounter any issues:

1. **Check Railway Logs**: Railway Dashboard → Deployments → View Logs
2. **Check Vercel Logs**: Vercel Dashboard → Deployment → View Function Logs
3. **Browser Console**: Open DevTools (F12) → Console tab for errors
4. **Test Backend Directly**: Use the `/health` endpoint to verify backend

---

## 🎉 NEXT STEPS AFTER DEPLOYMENT

1. **Share Your Project**: Add URLs to your resume/portfolio
2. **Custom Domain** (Optional): Add your own domain in Vercel settings
3. **Monitoring**: Set up uptime monitoring with UptimeRobot (free)
4. **Security**: Regenerate Cohere API key if it was exposed in git history
5. **Documentation**: Update README.md with live URLs

---

**🚀 Happy Deploying!**

Generated by Claude Code
