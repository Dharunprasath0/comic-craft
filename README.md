# ComicCraft — Render-ready AI Comic Story Creator

ComicCraft turns a short story idea into a five-panel comic. Gemini generates the outline and narration, **Gemini 3.1 Flash Image** generates the panel artwork through Google's hosted API, and the FastAPI app builds a downloadable PDF.

This deployment version does **not** run Stable Diffusion, PyTorch, or Diffusers on the web server, so it is lightweight enough for ordinary FastAPI hosting such as Render.

## Project flow

`User -> FastAPI -> Gemini text -> Gemini image API -> 5 panels -> PDF -> browser`

## 1. Local setup

Use Python 3.10+.

```bash
python -m venv env
```

Windows PowerShell:

```powershell
env\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

macOS/Linux:

```bash
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Then run:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## 2. Upload to GitHub

Upload the **contents of this folder** to a GitHub repository. The repository root should directly contain `app/`, `templates/`, `static/`, `requirements.txt`, and `render.yaml`.

Do **not** upload a real `.env`. It is already excluded by `.gitignore`.

## 3. Deploy on Render — easiest method

### Option A: Render Blueprint

1. Push this project to GitHub.
2. In Render choose **New -> Blueprint**.
3. Select your GitHub repository.
4. Render reads `render.yaml` automatically.
5. When asked for `GEMINI_API_KEY`, paste your real Gemini API key.
6. Create the service and wait for the build to finish.

### Option B: Normal Web Service

Create a **Web Service**, connect the GitHub repository, and use:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Add this Environment Variable in Render:

```text
GEMINI_API_KEY = your real Gemini API key
```

The optional model variables are already given in `.env.example` and `render.yaml`.

## Public routes

- `/` — comic creation page
- `/generate` — HTML form generation
- `/generate-comic/json` — JSON API
- `/docs` — FastAPI Swagger docs
- `/health` — Render health check

The old public `/test-image` route has been removed so strangers cannot use it to consume image-generation quota directly.

## Storage note

Render's normal filesystem is ephemeral. ComicCraft writes generated images and PDFs locally only so the current request can preview/download them. Files can disappear after a restart or redeploy. This is fine for a student demo. For permanent user libraries, move generated files to object storage later.

## API/key note

The ZIP intentionally contains **no real Gemini API key**. Keep the key in Render's Environment settings (or in a local `.env`) so it is not exposed in GitHub.

## Models used by default

- Outline: `gemini-3.8-flash`
- Narration: `gemini-3.8-flash`
- Panel images: `gemini-3.1-flash-image`

All three can be changed using environment variables without editing Python code.
