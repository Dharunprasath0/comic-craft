# ComicCraft — Render + Free-Tier Cloudflare Image Generation

ComicCraft is a FastAPI web application that turns a short prompt into a five-panel comic. Gemini generates the comic outline and narration; Cloudflare Workers AI generates the panel artwork with FLUX.1 Schnell; the application then builds a preview and downloadable PDF.

## Why this deployment version exists

The original project ran Stable Diffusion locally with PyTorch/Diffusers. That needs substantially more RAM/GPU capacity than a normal free Render web service. A later deployment version used Gemini image generation, but Gemini image API quota can require paid billing. This version instead calls Cloudflare Workers AI for images, so the Render server stays lightweight.

## Architecture

Browser -> FastAPI/Render -> Gemini text API -> Cloudflare Workers AI images -> PDF export

## 1. Required accounts

You need:

1. A Google AI Studio Gemini API key for the two text-generation calls.
2. A free Cloudflare account for Workers AI image generation.
3. GitHub and Render accounts for deployment.

## 2. Get Cloudflare Workers AI credentials

In Cloudflare:

1. Open the Cloudflare dashboard.
2. Go to **Workers AI**.
3. Choose **Use REST API**.
4. Create a **Workers AI API Token** and copy it.
5. Copy the **Account ID** shown on the same setup page.

Keep both values secret. Do not commit them to GitHub.

## 3. Local setup

```bash
python -m venv env
```

Windows PowerShell:

```powershell
env\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```text
GEMINI_API_KEY=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_API_TOKEN=...
```

Run:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## 4. Push to GitHub

From this `comiccraft` folder:

```bash
git init
git add .
git commit -m "ComicCraft free image deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If `origin` already exists, use:

```bash
git remote set-url origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## 5. Deploy on Render

This repository includes `render.yaml`.

1. Render -> **New** -> **Blueprint**.
2. Select the GitHub repository.
3. Add the requested secret environment variables:
   - `GEMINI_API_KEY`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_API_TOKEN`
4. Deploy.

The Blueprint already supplies:

```text
GEMINI_FLASH_MODEL=gemini-3.5-flash-lite
GEMINI_PRO_MODEL=gemini-3.5-flash-lite
CLOUDFLARE_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell
CLOUDFLARE_IMAGE_STEPS=4
```

## 6. Free-tier note

This is a free-tier deployment, not unlimited compute. Gemini text and Cloudflare Workers AI each enforce their own free usage/rate limits. When a daily quota is reached, generation must wait until that provider resets its allowance.

## 7. Tests

The included tests mock external AI calls, so they can validate the application without consuming API quota:

```bash
pip install -r requirements-dev.txt
pytest
```

## Project structure

```text
comiccraft/
├── app/
├── templates/
├── static/
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── render.yaml
├── .env.example
└── README.md
```

## Security

Never commit `.env`, Gemini keys, Cloudflare tokens, or any other secret to GitHub. Store production secrets only in Render Environment Variables.
