# 🚀 Quick Deployment Reference Card

## 📋 WHAT YOU NEED

### GitHub Repository (Ready ✅)
- **URL**: https://github.com/shreedeshmukh2505/Nsquire_updated
- **Branch**: main
- **Latest Commit**: bc1c942 "Disable ESLint during production build"

### Environment Variables for Railway
```
COHERE_API_KEY = TsY1cWlAAL00usoIgNEeHLxkiYO9vzSSwzZQKppW
FLASK_ENV = production
```

### Project Files (All Present ✅)
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.toml` - Railway configuration
- ✅ `EDI_project_sql.py` - Flask backend
- ✅ `colleges.db` - Database (452KB)
- ✅ `models.py` - Database models
- ✅ `ml_models.py` - ML models
- ✅ `.env.production` - Production config
- ✅ `src/config.js` - API configuration

---

## 🚂 RAILWAY DEPLOYMENT (5 minutes)

### Quick Steps:
1. **Go to**: https://railway.app/dashboard
2. **Click**: "New Project" → "Deploy from GitHub repo"
3. **Select**: shreedeshmukh2505/Nsquire_updated
4. **Add Variables** (while building):
   - `COHERE_API_KEY` = `TsY1cWlAAL00usoIgNEeHLxkiYO9vzSSwzZQKppW`
   - `FLASK_ENV` = `production`
5. **Wait**: 2-3 minutes for build
6. **Generate Domain**: Settings → Networking → Generate Domain
7. **Test**: Visit `https://your-url.up.railway.app/health`

### Expected Response:
```json
{"status": "ok", "database": "connected"}
```

---

## ▲ VERCEL DEPLOYMENT (3 minutes)

### Quick Steps:
1. **Go to**: https://vercel.com/new
2. **Import**: shreedeshmukh2505/Nsquire_updated
3. **Add Environment Variable**:
   - Name: `REACT_APP_API_URL`
   - Value: `https://your-railway-url.up.railway.app`
4. **Deploy**: Click "Deploy"
5. **Wait**: 2-3 minutes
6. **Test**: Open your Vercel URL

---

## 📞 SUPPORT

### Detailed Guides in This Repo:
- `RAILWAY_DEPLOYMENT_STEPS.md` - Detailed Railway guide
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `README.md` - Project overview

### Test All Features:
- ✅ Chatbot - Ask about colleges
- ✅ Rank Predictor - Enter rank and predict
- ✅ College Comparison - Compare colleges
- ✅ College Search - Search and filter

---

## 🎯 DEPLOYMENT CHECKLIST

### Railway (Backend):
- [ ] New project created from GitHub
- [ ] Environment variables added
- [ ] Build completed (green checkmark)
- [ ] Domain generated
- [ ] `/health` endpoint working

### Vercel (Frontend):
- [ ] Project imported from GitHub
- [ ] Environment variable added (REACT_APP_API_URL)
- [ ] Build completed
- [ ] Site is live
- [ ] Can access chatbot
- [ ] Can predict colleges
- [ ] Can compare colleges

---

## 💰 COST (FREE TIER)

**Railway**: $5 credit/month (enough for 500+ hours)
**Vercel**: 100GB bandwidth/month (free forever)
**Total**: $0 for normal usage! 🎉

---

## 🎓 YOUR FINAL URLs

Once deployed:

**Backend (Railway)**:
`https://__________________.up.railway.app`

**Frontend (Vercel)**:
`https://__________________.vercel.app`

**GitHub**:
https://github.com/shreedeshmukh2505/Nsquire_updated

---

**Ready to deploy? Follow RAILWAY_DEPLOYMENT_STEPS.md!**
