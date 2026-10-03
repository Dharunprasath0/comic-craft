# Deployment changes made

This package was converted from local Stable Diffusion to Google's hosted Gemini image generation so it can run on a normal Render FastAPI service.

Main changes:

- Removed `torch`, `diffusers`, `transformers`, and `accelerate`.
- Replaced the local `StableDiffusionPipeline` with `gemini-3.1-flash-image` through `google-genai`.
- Updated text-model defaults to `gemini-3.8-flash`.
- Added `render.yaml` and `/health` for Render deployment.
- Removed the public `/test-image` route to avoid easy quota abuse.
- Kept generated images/PDFs as temporary local files for simple student/demo deployment.
- Added unique PDF filenames and more robust absolute filesystem handling.

Only `GEMINI_API_KEY` must be supplied as a secret in Render. Do not place the real key in GitHub.
