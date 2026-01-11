# Getting Started - API Token Setup

## Quick Guide: Where to Get Your API Token

You need **one** of these tokens to run the platform:

---

## Option 1: GitHub Token (Free, but Limited)

### Pros:
- ✅ Free to use
- ✅ Good for testing

### Cons:
- ❌ **50 requests per 24 hours limit** (you've hit this!)
- ❌ Wait time: ~24 hours between batches

### Steps:

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Login to your GitHub account

2. **Generate New Token**
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - Name it: "RAG Platform" or similar
   - Select scopes: Check `read:packages` (minimum)
   - Set expiration: Choose "No expiration" or "90 days"
   - Click **"Generate token"**

3. **Copy Token**
   - **IMPORTANT**: Copy the token immediately (starts with `github_pat_`)
   - You won't be able to see it again!

4. **Add to `.env` file**
   ```bash
   GITHUB_TOKEN=github_pat_your_token_here
   ```

---

## Option 2: OpenAI API Key (Recommended)

### Pros:
- ✅ **No daily limit** (pay-as-you-go)
- ✅ Better for demos and production
- ✅ More reliable
- ✅ Free credits available for new accounts

### Cons:
- ❌ Costs money (but very cheap for demos)
- ❌ Requires payment method

### Steps:

1. **Go to OpenAI Platform**
   - Visit: https://platform.openai.com/api-keys
   - Login or create an account

2. **Create API Key**
   - Click **"Create new secret key"**
   - Name it: "RAG Platform" or similar
   - Click **"Create secret key"**
   - **IMPORTANT**: Copy the key immediately (starts with `sk-`)
   - You won't be able to see it again!

3. **Add Credits (if needed)**
   - New accounts often include $5-18 free credits
   - For production: Go to https://platform.openai.com/account/billing
   - Add payment method if needed
   - **Pricing**: Very cheap (~$0.01-0.03 per query)

4. **Add to `.env` file**
   ```bash
   OPENAI_API_KEY=sk-your_key_here
   ```

---

## Setting Up Your `.env` File

1. **Create `.env` file** in the project root (same folder as `README.md`)

2. **Add your token** (choose ONE):
   ```bash
   # For GitHub Models (free but limited)
   GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # OR for OpenAI API (recommended)
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Important Notes:**
   - Remove any spaces or newlines
   - Don't commit `.env` to git (it's in `.gitignore`)
   - Restart the backend server after adding/changing tokens

---

## Which Should You Use?

### Use GitHub Token if:
- You're just testing/learning
- You don't mind the 50 requests/24h limit
- You want to keep costs at $0

### Use OpenAI API Key if:
- You're preparing for a demo/interview
- You need more than 50 requests per day
- You want reliable, unlimited access
- **RECOMMENDED for this project!**

---

## Troubleshooting

### "Token not found"
- Check that `.env` file exists in project root
- Verify the variable name is correct (`GITHUB_TOKEN` or `OPENAI_API_KEY`)
- No quotes around the token value
- Restart the backend server

### "Invalid token"
- Make sure you copied the entire token
- Check for extra spaces or newlines
- For GitHub: Token must start with `github_pat_`
- For OpenAI: Key must start with `sk-`

### "Rate limit exceeded" (GitHub)
- You've used all 50 free requests
- Wait ~24 hours OR switch to OpenAI API key

---

## Example `.env` File

```bash
# Example .env file

# Option 1: GitHub Models (free tier - 50 requests/24h)
# GITHUB_TOKEN=github_pat_11AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

# Option 2: OpenAI API (recommended - pay-as-you-go)
OPENAI_API_KEY=sk-proj-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

**Note**: Comment out (add `#`) the one you're NOT using.

---

## Need Help?

- **GitHub Token Issues**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **OpenAI API Issues**: https://platform.openai.com/docs/api-reference/authentication
- **Rate Limits**: See README.md troubleshooting section

