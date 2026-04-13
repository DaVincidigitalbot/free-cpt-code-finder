# FreeCPTCodeFinder Assistant Backend

## Purpose
Provides a real backend for the homepage AI assistant so the browser never holds model secrets.

## What it does
- exposes `GET /health`
- exposes `POST /assistant`
- grounds answers using `cpt_database.json`
- sends the grounded prompt to OpenAI when `OPENAI_API_KEY` is configured

## Expected request body
```json
{
  "question": "What CPT code fits laparoscopic appendectomy?",
  "caseLines": []
}
```

## Environment
- `OPENAI_API_KEY` required for real answers
- `OPENAI_MODEL` optional, defaults to `gpt-4.1-mini`
- `PORT` optional, defaults to `8787`

## Local run
```bash
cd assistant-backend
npm install
OPENAI_API_KEY=your_key_here npm start
```

## Frontend hook
On the site, set:
```html
<script>
window.FCCF_ASSISTANT_ENDPOINT = 'https://your-backend-host/assistant';
</script>
```
before the closing `</body>` or inject it at build time.

## Guardrails
- concise answers
- no fabricated CPT facts
- reminds user when documentation or payer policy changes the answer
- uses site CPT matches as grounding context
