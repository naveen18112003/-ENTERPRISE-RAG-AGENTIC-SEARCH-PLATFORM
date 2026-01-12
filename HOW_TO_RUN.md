# How to Run the App (Simple Guide)

Follow these steps to start the application properly. You will need to open **TWO separate terminal windows**.

## Step 0: Check your Token
Ensure you have added your API Key to the `.env` file in this folder:
```
OPENAI_API_KEY=sk-...
```
(Or `GITHUB_TOKEN` if you are using the free tier).

---

## Step 1: Start the Backend (Terminal 1)
Open a new terminal in this folder and run:

```powershell
# 1. Activate the environment
.\.venv\Scripts\Activate

# 2. Run the server on Port 8001
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8001
```

*Keep this terminal open! You should see "Application startup complete".*

---

## Step 2: Start the Frontend (Terminal 2)
Open a second, **separate** terminal window in this folder and run:

```powershell
# 1. Go to the public folder
cd public

# 2. Start the web server on Port 8080
python -m http.server 8080
```

*Keep this terminal open too!*

---

## Step 3: Open in Browser
Go to this link:
👉 **http://127.0.0.1:8080**

---

### Troubleshooting
*   **"Address already in use"**: Make sure you aren't running the command twice. Close old terminals.
*   **"Connection refused"**: Make sure Terminal 1 is running without errors.
*   **"Rate Limit"**: Check your `.env` file and use an OpenAI Key if possible.

---

## How to Ingest Documents

Since this is a lightweight app running in memory, there are two ways to ingest, depending on how you use it:

### Method 1: For the Web App (Recommended)
1.  Go to **http://127.0.0.1:8080**.
2.  Click the **Upload Icon** (arrow up) next to the search bar.
3.  Select a PDF or TXT file from your computer.
4.  It will be processed instantly and ready for search.
    *   *Note: If you restart the backend (Terminal 1), these files are cleared from memory.*

### Method 2: For CLI Mode
If you want to use the command line instead of the website:
1.  Put your PDF/TXT files in the `data/` folder.
2.  Run:
    ```powershell
    python main.py --ingest --query "Who is the CEO?"
    ```
