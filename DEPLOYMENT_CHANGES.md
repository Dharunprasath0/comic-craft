# Deployment Changes — Free Image Version

This version is designed for a zero-cost student/demo deployment within the providers' free-tier limits.

## What changed

- Local Stable Diffusion, PyTorch and Diffusers remain removed.
- Paid Gemini image generation has been removed.
- Comic-panel images are generated through Cloudflare Workers AI using FLUX.1 Schnell.
- Gemini is used only for text generation (outline and narration), using `gemini-3.5-flash-lite` by default.
- The existing FastAPI frontend, 5-panel workflow, preview and PDF export remain intact.
- `/test-image` stays removed so a public visitor cannot directly consume image quota from that developer endpoint.

## Required Render secrets

- `GEMINI_API_KEY`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

Optional values are already supplied in `render.yaml`.
