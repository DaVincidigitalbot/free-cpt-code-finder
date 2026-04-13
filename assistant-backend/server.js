import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const cptDbPath = path.join(projectRoot, 'cpt_database.json');
const openai = process.env.OPENAI_API_KEY ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) : null;
const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

let cptDb = [];
try {
  cptDb = JSON.parse(fs.readFileSync(cptDbPath, 'utf8'));
} catch (err) {
  console.error('Failed to load CPT database', err);
}

function searchCpt(query, limit = 8) {
  const q = String(query || '').toLowerCase().trim();
  if (!q || !Array.isArray(cptDb)) return [];
  const scored = cptDb.map(item => {
    const code = String(item.code || '');
    const desc = String(item.description || '');
    let score = 0;
    if (code === q) score += 100;
    if (code.startsWith(q)) score += 40;
    if (desc.toLowerCase().includes(q)) score += 25;
    for (const token of q.split(/\s+/)) {
      if (desc.toLowerCase().includes(token)) score += 5;
    }
    return { item, score };
  }).filter(x => x.score > 0).sort((a,b) => b.score - a.score).slice(0, limit);
  return scored.map(({ item }) => ({
    code: item.code,
    description: item.description,
    wrvu: item.work_rvu ?? item.wrvu ?? null,
    category: item.category ?? null
  }));
}

app.get('/health', (_req, res) => {
  res.json({ ok: true, openai: !!openai, cptRows: Array.isArray(cptDb) ? cptDb.length : 0 });
});

app.post('/assistant', async (req, res) => {
  const question = String(req.body?.question || '').trim();
  const caseLines = Array.isArray(req.body?.caseLines) ? req.body.caseLines.slice(0, 20) : [];
  if (!question) return res.status(400).json({ error: 'question required' });

  const matches = searchCpt(question, 10);
  const system = `You are the Free CPT Code Finder AI Assistant. You help with CPT coding, modifiers, wRVUs, and case-structure questions. Be concise, practical, and cautious. Never claim certainty when the rules are ambiguous. Never fabricate CPT facts. If the answer depends on documentation, operative details, payer policy, NCCI edits, or laterality/global-period context, say so clearly. Treat the provided CPT matches as grounding data. Prefer bullets over long paragraphs.`;
  const grounded = {
    question,
    likelyMatches: matches,
    activeCase: caseLines.map(l => ({ cpt: l.cpt, desc: l.desc, mods: l.mods || [], userMod: l.userMod || '', approach: l.approach || '', wrvu: l.baseWrvu || l.effWrvu || null }))
  };

  if (!openai) {
    return res.json({
      answer: `Backend is running, but OPENAI_API_KEY is not set yet. Top grounded matches for this question: ${matches.map(m => `${m.code} ${m.description}`).join(' | ') || 'none found'}.`
    });
  }

  try {
    const response = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4.1-mini',
      temperature: 0.2,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: `Use this grounded site data when answering:\n${JSON.stringify(grounded, null, 2)}` }
      ]
    });
    const answer = response.choices?.[0]?.message?.content?.trim() || 'No answer returned.';
    res.json({ answer, matches });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'assistant_failed', detail: err.message });
  }
});

const port = process.env.PORT || 8787;
app.listen(port, () => console.log(`Assistant backend listening on ${port}`));
