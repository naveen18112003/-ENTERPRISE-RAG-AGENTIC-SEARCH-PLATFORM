# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, Bitbucket)
3. **API Token**: GitHub Token or OpenAI API Key

## Method 1: Deploy via Vercel Dashboard (Recommended)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Project"**
3. Select your Git provider (GitHub/GitLab/Bitbucket)
4. Choose your repository
5. Click **"Import"**

### Step 3: Configure Project

**Framework Preset**: Other
**Root Directory**: `./` (leave as default)
**Build Command**: Leave empty (not needed)
**Output Directory**: `public`

### Step 4: Add Environment Variables

Before deploying, add your API token:

1. Click **"Environment Variables"** section
2. Add one of the following:

**Option A - GitHub Token (Free tier):**
- Name: `GITHUB_TOKEN`
- Value: `github_pat_xxxxxxxxxxxxxxxxxxxxxxxx`

**Option B - OpenAI API Key (Recommended):**
- Name: `OPENAI_API_KEY`
- Value: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx`

3. Click **"Add"**
4. Click **"Deploy"**

### Step 5: Wait for Deployment

Vercel will:
- Install dependencies from `requirements.txt`
- Build your API endpoints
- Deploy static frontend
- Provide you with a live URL (e.g., `https://your-project.vercel.app`)

---

## Method 2: Deploy via Vercel CLI

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

### Step 3: Deploy

Navigate to your project directory and run:

```bash
cd c:\Users\navee\OneDrive\Desktop\new\-ENTERPRISE-RAG-AGENTIC-SEARCH-PLATFORM
vercel
```

For production deployment:
```bash
vercel --prod
```

### Step 4: Set Environment Variables via CLI

```bash
vercel env add GITHUB_TOKEN
```

Or for OpenAI:
```bash
vercel env add OPENAI_API_KEY
```

Paste your token when prompted.

### Step 5: Redeploy

After adding environment variables:
```bash
vercel --prod
```

---

## Post-Deployment

### Testing Your Deployment

1. Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Try uploading a small document (<20 pages)
3. Test both RAG and Agentic modes

### Common Issues & Solutions

#### ❌ "Function Timeout"
**Problem**: Large file uploads or long queries timeout (10s limit)

**Solution**:
- Upload smaller files
- Split large documents into chunks
- Use OpenAI API instead of GitHub Token (faster)

#### ❌ "502 Bad Gateway"
**Problem**: Backend function failed to start

**Solution**:
- Check Vercel Function Logs
- Verify environment variables are set correctly
- Ensure `requirements.txt` has all dependencies

#### ❌ "Rate Limit Exceeded"
**Problem**: GitHub Token has daily limit (50 requests/24h)

**Solution**:
- Switch to OpenAI API Key
- Add `OPENAI_API_KEY` in Vercel dashboard
- Redeploy

#### ❌ "Upload fails silently"
**Problem**: File too large or processing timeout

**Solution**:
- Keep files under 5MB
- Max ~20 pages per upload
- Use text files instead of PDFs when possible

---

## Vercel Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "public/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "public/$1"
    }
  ]
}
```

### `.vercelignore`
```
.venv
__pycache__
*.pyc
.env
data/
```

---

## Important Notes

### Memory Limitations
- Vercel serverless functions are ephemeral
- Uploaded documents are stored **in-memory only**
- Documents are lost when function goes to sleep (~5 minutes of inactivity)
- For persistent storage, consider adding Redis or Pinecone integration

### Performance Tips
1. **Use OpenAI API** for better speed and reliability
2. **Pre-chunk large documents** before uploading
3. **Limit concurrent requests** to avoid rate limits
4. **Monitor function execution time** in Vercel dashboard

### Security
- Never commit `.env` file
- Rotate API keys regularly
- Use environment variables for all secrets
- Enable CORS only for trusted domains in production

---

## Monitoring & Debugging

### Vercel Dashboard
- **Overview**: Deployment status and metrics
- **Functions**: Execution logs and errors
- **Analytics**: Usage statistics
- **Settings**: Environment variables and domains

### Checking Logs

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click **"Functions"** tab
4. View real-time logs

### Debug Mode

Add to your `.env` (local only, never commit):
```bash
DEBUG=1
```

---

## Next Steps After Deployment

1. ✅ Test all endpoints (`/`, `/api/search`, `/api/upload`)
2. ✅ Upload a sample document
3. ✅ Test both RAG and Agentic modes
4. ✅ Monitor function execution times
5. ✅ Set up custom domain (optional)
6. ✅ Configure analytics (optional)

---

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables are set
3. Test locally first with `vercel dev`
4. Consult [Vercel Python docs](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

---

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/vercel/)
