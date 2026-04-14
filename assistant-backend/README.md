# FreeCPTCodeFinder Assistant Backend

## Purpose
Provides the real backend for the homepage AI assistant so the browser never holds model secrets.

## Render-ready deployment
This folder is prepared for direct Render deployment.

### Files included
- `server.js` → Express backend
- `package.json` → dependencies and start script
- `render.yaml` → Render Blueprint config
- `.env.example` → example environment values

## What it does
- exposes `GET /health`
- exposes `POST /assistant`
- grounds answers using `../cpt_database.json`
- sends the grounded prompt to Gemini when `GEMINI_API_KEY` is configured
- limits CORS to the production site origins by default

## Render deployment steps
### Option A: Blueprint
1. Push this repo to GitHub
2. In Render, click **New +** → **Blueprint**
3. Select this repo
4. Render will detect `assistant-backend/render.yaml`
5. Add your secret:
   - `GEMINI_API_KEY`
6. Deploy

### Option B: Manual web service
Use these exact settings:
- **Environment**: Node
- **Root Directory**: `assistant-backend`
- **Build Command**: `npm install`
- **Start Command**: `npm start`
- **Health Check Path**: `/health`

Environment variables:
- `GEMINI_API_KEY` = your Gemini API key
- `GEMINI_MODEL` = `gemini-2.5-flash`
- `ALLOWED_ORIGINS` = `https://freecptcodefinder.com,https://www.freecptcodefinder.com`

## Expected request body
```json
{
  "question": "What CPT code fits laparoscopic appendectomy?",
  "caseLines": []
}
```

## Expected response
```json
{
  "answer": "...",
  "matches": []
}
```

## Frontend hook
Once Render gives you a URL like:
- `https://freecptcodefinder-assistant.onrender.com`

set the site assistant endpoint to:
```html
<script>
window.FCCF_ASSISTANT_ENDPOINT = 'https://freecptcodefinder-assistant.onrender.com/assistant';
</script>
```

Then the homepage AI assistant becomes live.

## Health check
- `GET /health`

## Guardrails
- concise answers
- no fabricated CPT facts
- reminds users when documentation, payer policy, or NCCI/global rules change the answer
- uses site CPT matches as grounding context
- keeps model secrets off the static site
