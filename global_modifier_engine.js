/*
 * FreeCPTCodeFinder Global Surgery Modifier Intelligence Engine
 * CMS-based educational logic for modifiers 58, 78, 79, and objective modifier 22 review.
 */
(function(root){
  'use strict';

  const CMS_LOGIC = {
    '58': {
      label: 'Modifier 58',
      summary: 'Staged or related procedure during the postoperative period.',
      bullets: [
        'Planned or anticipated procedure',
        'More extensive procedure than the original operation',
        'Therapy following a diagnostic procedure',
        'Begins a new postoperative global period'
      ],
      newGlobalPeriod: true
    },
    '78': {
      label: 'Modifier 78',
      summary: 'Unplanned return to the operating room for a related complication.',
      bullets: [
        'Unplanned return to OR or procedure room',
        'Related to the original procedure',
        'Used for complications such as bleeding, dehiscence, leak, injury, infected hematoma, or washout',
        'Does not begin a new postoperative global period'
      ],
      newGlobalPeriod: false
    },
    '79': {
      label: 'Modifier 79',
      summary: 'Unrelated procedure during the postoperative period.',
      bullets: [
        'Procedure is unrelated to the previous operation',
        'Requires a separate diagnosis, site, or clinical problem',
        'Begins a new postoperative global period'
      ],
      newGlobalPeriod: true
    }
  };

  const MOD22_PATTERNS = [
    { key: 'dense vascular adhesions', label: 'Dense vascular adhesions', re: /dense\s+(vascular\s+)?adhesions?/i },
    { key: 'prior multiple laparotomies', label: 'Prior multiple laparotomies', re: /(multiple|several|prior)\s+(previous\s+)?laparotom/i },
    { key: 'reoperative field', label: 'Reoperative field', re: /reoperative|re\s*-\s*operative|hostile abdomen|hostile reoperative abdomen/i },
    { key: 'severe inflammation', label: 'Severe inflammation', re: /severe\s+inflamm|phlegmon|marked\s+inflamm/i },
    { key: 'feculent peritonitis', label: 'Feculent peritonitis', re: /feculent\s+peritonitis|stool\s+contamination|gross\s+fecal/i },
    { key: 'major contamination', label: 'Major contamination', re: /major\s+contamination|gross\s+contamination|class\s+iv|dirty\s+case/i },
    { key: 'morbid obesity', label: 'Morbid obesity', re: /morbid\s+obesity|bmi\s*(>|greater than|of)?\s*40/i },
    { key: 'radiation fibrosis', label: 'Radiation fibrosis', re: /radiation\s+fibrosis|post\s*-?radiation/i },
    { key: 'mesh explantation', label: 'Mesh explantation', re: /mesh\s+(explant|removal|removed|excised)/i },
    { key: 'infected mesh', label: 'Infected mesh', re: /infected\s+mesh|mesh\s+infection/i },
    { key: 'large abdominal wall reconstruction', label: 'Large abdominal wall reconstruction', re: /large\s+abdominal\s+wall\s+reconstruction|complex\s+abdominal\s+wall/i },
    { key: 'difficult exposure', label: 'Difficult exposure', re: /difficult\s+exposure|exposure\s+was\s+difficult/i },
    { key: 'unexpected anatomy', label: 'Unexpected anatomy', re: /unexpected\s+anatomy|aberrant\s+anatomy|distorted\s+anatomy/i },
    { key: 'major blood loss', label: 'Major blood loss', re: /major\s+blood\s+loss|ebl\s*(>|greater than|of)?\s*(750|800|900|1000|1,000)/i }
  ];

  function yes(value){
    return value === true || String(value || '').toLowerCase() === 'yes';
  }

  function money(value){
    const n = Number(value || 0);
    return Number.isFinite(n) ? Number(n.toFixed(2)) : 0;
  }

  function percent(part, whole){
    const p = Number(part || 0);
    const w = Number(whole || 0);
    if (!p || !w) return 0;
    return Math.round((p / w) * 100);
  }

  function evaluateGlobalPeriod(answers){
    const a = answers || {};
    if (!yes(a.inGlobalPeriod)) {
      return {
        inGlobalPeriod: false,
        modifier: null,
        label: 'No postoperative global modifier indicated',
        explanation: 'Case continues through standard NCCI, MPPR, and multiple-procedure logic.'
      };
    }
    if (yes(a.planned) || yes(a.moreExtensive) || yes(a.therapyAfterDiagnostic)) {
      return {
        inGlobalPeriod: true,
        modifier: '58',
        confidence: 'high',
        reason: yes(a.planned) ? 'Planned or anticipated at the original operation.' :
          (yes(a.moreExtensive) ? 'More extensive than the original procedure.' : 'Therapy following a diagnostic procedure.'),
        education: CMS_LOGIC['58']
      };
    }
    if (yes(a.complicationReturnToOR)) {
      return {
        inGlobalPeriod: true,
        modifier: '78',
        confidence: 'high',
        reason: 'Unplanned return to the operating room for a related postoperative complication.',
        education: CMS_LOGIC['78']
      };
    }
    if (yes(a.unrelated)) {
      return {
        inGlobalPeriod: true,
        modifier: '79',
        confidence: 'high',
        reason: 'Procedure is unrelated to the prior operation.',
        education: CMS_LOGIC['79']
      };
    }
    return {
      inGlobalPeriod: true,
      modifier: null,
      confidence: 'low',
      warning: 'Documentation may not support modifiers 58, 78, or 79 based on the selected answers.',
      education: null
    };
  }

  function analyzeModifier22(input){
    const i = input || {};
    const report = String(i.operativeReport || '');
    const findings = Array.isArray(i.objectiveFindings) ? i.objectiveFindings.filter(Boolean) : [];
    const reasons = [];
    const seen = new Set();
    const add = (key, text) => {
      if (!key || seen.has(key)) return;
      seen.add(key);
      reasons.push(text);
    };

    MOD22_PATTERNS.forEach(pattern => {
      if (pattern.re.test(report) || findings.includes(pattern.key)) add(pattern.key, pattern.label + ' documented.');
    });

    const adhesiolysis = Number(i.adhesiolysisMinutes || 0);
    const total = Number(i.totalOperativeMinutes || i.actualMinutes || 0);
    if (adhesiolysis > 60) add('adhesiolysis_minutes', adhesiolysis + ' minutes of adhesiolysis documented.');
    const adhesiolysisPercent = percent(adhesiolysis, total);
    if (adhesiolysisPercent >= 30) add('adhesiolysis_percent', adhesiolysisPercent + '% of operative time devoted to adhesiolysis.');

    const expected = Number(i.expectedMinutes || 0);
    const actual = Number(i.actualMinutes || total || 0);
    const timePercent = expected && actual ? Math.round((actual / expected) * 100) : 0;
    if (timePercent > 150) add('time_over_expected', 'Operative time was ' + timePercent + '% of expected.');

    const bloodLoss = Number(i.bloodLossMl || 0);
    if (bloodLoss >= 750) add('blood_loss', bloodLoss + ' mL estimated blood loss documented.');

    const candidate = reasons.length >= 2 || adhesiolysis > 60 || timePercent > 150;
    return {
      candidate,
      title: candidate ? 'Possible Modifier 22 Candidate' : 'Modifier 22 not strongly supported by objective criteria entered',
      reasons,
      metrics: {
        adhesiolysisMinutes: adhesiolysis,
        totalOperativeMinutes: total,
        adhesiolysisPercent,
        expectedMinutes: expected,
        actualMinutes: actual,
        operativeTimePercentOfExpected: timePercent,
        bloodLossMl: bloodLoss
      }
    };
  }

  function generateModifier22Justification(input){
    const i = input || {};
    const analysis = i.analysis || analyzeModifier22(i);
    const code = String(i.cptCode || i.primaryCode || 'XXXXX');
    const facts = analysis.reasons || [];
    const metrics = analysis.metrics || {};
    const fragments = [];
    if (metrics.actualMinutes) fragments.push('Total operative time was ' + metrics.actualMinutes + ' minutes');
    if (metrics.expectedMinutes) fragments.push('expected time was ' + metrics.expectedMinutes + ' minutes');
    if (metrics.adhesiolysisMinutes) fragments.push(metrics.adhesiolysisMinutes + ' minutes were spent performing adhesiolysis');
    if (metrics.adhesiolysisPercent) fragments.push(metrics.adhesiolysisPercent + '% of operative time was adhesiolysis');
    if (metrics.bloodLossMl) fragments.push('estimated blood loss was ' + metrics.bloodLossMl + ' mL');

    const factSentence = facts.length ? ' Objective findings included: ' + facts.join(' ') : '';
    const metricSentence = fragments.length ? ' ' + fragments.join('; ') + '.' : '';
    return 'This procedure required substantially greater work than typically required for CPT ' + code +
      ' because the documented operative findings increased technical difficulty, operative time, and operative risk.' +
      metricSentence + factSentence +
      ' These objective findings support surgeon review for modifier 22.';
  }

  function estimateModifier22Impact(basePayment, appealIncreasePercent){
    const base = money(basePayment);
    const pct = Number(appealIncreasePercent || 20);
    const withAppeal = money(base * (1 + pct / 100));
    return {
      withoutModifier22: base,
      successfulAppealEstimate: withAppeal,
      estimatedIncrease: money(withAppeal - base),
      increasePercent: pct,
      label: 'Educational estimate only. Actual payer allowance depends on documentation, contract, and appeal review.'
    };
  }

  function buildTimeline(previous, today, modifier){
    const edu = modifier ? CMS_LOGIC[modifier] : null;
    return [
      { label: 'Original operation', value: previous && previous.code ? previous.code + (previous.date ? ' on ' + previous.date : '') : 'Previous surgery' },
      { label: 'Global period', value: 'Postoperative global period active' },
      { label: "Today's operation", value: today && today.codes ? today.codes.join(', ') : 'Current case' },
      { label: 'Recommended modifier', value: modifier ? '-' + modifier : 'No supported postoperative modifier' },
      { label: 'New global period', value: edu ? (edu.newGlobalPeriod ? 'Yes' : 'No') : 'Not applicable' }
    ];
  }

  const api = {
    CMS_LOGIC,
    MOD22_PATTERNS,
    evaluateGlobalPeriod,
    analyzeModifier22,
    generateModifier22Justification,
    estimateModifier22Impact,
    buildTimeline
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.GlobalModifierEngine = api;
})(typeof window !== 'undefined' ? window : globalThis);
