# Deploy to Streamlit Cloud

**Deploy the live leaderboard in 3 steps (2 minutes)**

## Step 1: Ensure Everything is Pushed to GitHub

```bash
# In compliance-leaderboard directory
git add .
git commit -m "Add Streamlit Cloud deployment files"
git push
```

**Important files that must be present:**
- ✅ `run_app.py` (entry point)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (configuration)
- ✅ `results/leaderboard.csv` (data)
- ✅ `results/scores.json` (scores)
- ✅ `app/page_*.py` (pages)
- ✅ `src/` (pipeline code)

## Step 2: Deploy on Streamlit Cloud

1. Go to: **https://share.streamlit.io/**
2. Sign in with GitHub (or create account)
3. Click **"New app"** button
4. Fill in deployment form:
   - **Repository:** `your-username/technical-ai-governance-hackathon` (or your fork)
   - **Branch:** `main`
   - **Main file path:** `compliance-leaderboard/run_app.py`
5. Click **"Deploy"**

### Important: Add Environment Variables

Before deploying, Streamlit Cloud needs API keys. Add these secrets:

1. In Streamlit Cloud app settings → **Secrets**
2. Add your `.env` values:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LITELLM_API_KEY=...
```

Or create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."
LITELLM_API_KEY = "..."
```

## Step 3: Verify Deployment

**Your live app is now at:**
```
https://share.streamlit.io/[username]/technical-ai-governance-hackathon/main/compliance-leaderboard/run_app.py
```

Or just visit **https://share.streamlit.io/** and search for "compliance-leaderboard"

---

## Features Available on Streamlit Cloud

✅ **Leaderboard Grid** - Interactive compliance score matrix
✅ **Model Deep Dive** - Detailed framework breakdowns per model
✅ **Requirement Browser** - View all 80 requirements with scores
✅ **Validation UI** - Human vs automatic scoring comparison
✅ **Methodology** - Framework definitions and scoring guidance

---

## Troubleshooting

### ❌ "Module not found" errors
**Solution:** Check `requirements.txt` includes all imports. Ensure all dependencies are listed.

### ❌ "API key not configured"
**Solution:** Add secrets to Streamlit Cloud:
1. App settings → Secrets
2. Paste environment variables
3. Redeploy

### ❌ "Data files not found"
**Solution:** Ensure paths are relative:
```python
# ✅ Correct
data = pd.read_csv("results/leaderboard.csv")

# ❌ Wrong (absolute path)
data = pd.read_csv("/Users/yulong/projects/.../results/leaderboard.csv")
```

### ❌ App loads slowly
**Solution:** First deployment takes ~2 minutes. Cached after that.

---

## Advanced: Custom Domain

To use a custom domain like `compliance.yoursite.com`:

1. In Streamlit Cloud app settings → **Custom domain**
2. Add your domain
3. Update DNS to point to Streamlit
4. Wait ~15 minutes for SSL certificate

---

## Update Your Deployment

Every time you push to GitHub, Streamlit Cloud **automatically redeploys**:

```bash
# Make changes locally
git add .
git commit -m "Update leaderboard"
git push
# → Streamlit Cloud redeploys automatically!
```

---

## Alternative: Deploy Locally

If you want to run locally instead of Streamlit Cloud:

```bash
cd compliance-leaderboard
streamlit run run_app.py
```

Opens at `http://localhost:8501`

---

## Pricing

**Streamlit Cloud is FREE** for:
- ✅ Public apps
- ✅ Community use
- ✅ Educational projects
- ✅ Open source projects

**Paid tier** ($50-300+/month) for:
- Private apps
- Increased computational resources
- Priority support

For this project, free tier is more than sufficient.

---

## Status Dashboard

Once deployed, you can:
- Monitor app health at Streamlit Cloud dashboard
- View logs and errors
- Manage environment variables
- Control app visibility (public/private)
- Enable/disable caching
- Set custom refresh rates

---

**Deployment time: 2-5 minutes**
**Live URL: `https://share.streamlit.io/...`**
**Auto-updates: Yes (every time you push to GitHub)**

Ready to go live! 🚀
