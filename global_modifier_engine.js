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
    { key: 'major blood loss', label: 'Major blood loss', re: /major\s+blood\s+loss|ebl\s*(>|greater than|of)?\s*(750|800|900|1000|1,000)/i },
    { key: 'debridement depth and size', label: 'Debridement depth and size', re: /debridement[^.]{0,80}(skin|subcutaneous|fascia|muscle|bone)[^.]{0,80}(\d+(\.\d+)?\s*(sq\s*cm|cm2|cm\^2)|\d+\s*x\s*\d+\s*cm)/i },
    { key: 'bowel injury risk', label: 'Bowel injury risk', re: /bowel\s+injury\s+risk|risk\s+of\s+enterotomy|serosal\s+injur|enterotomy/i }
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

  function parseDate(value){
    if (!value) return null;
    const date = new Date(String(value) + (/^\d{4}-\d{2}-\d{2}$/.test(String(value)) ? 'T00:00:00' : ''));
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function daysBetween(start, end){
    const s = parseDate(start);
    const e = parseDate(end);
    if (!s || !e) return null;
    const dayMs = 24 * 60 * 60 * 1000;
    return Math.floor((Date.UTC(e.getFullYear(), e.getMonth(), e.getDate()) - Date.UTC(s.getFullYear(), s.getMonth(), s.getDate())) / dayMs);
  }

  function inferGlobalPeriodDays(code, metadata){
    const explicit = Number(metadata && (metadata.global_period_days ?? metadata.globalPeriodDays ?? metadata.globalPeriod));
    if ([0, 10, 90].includes(explicit)) return explicit;
    const c = String(code || '');
    if (!/^\d{5}$/.test(c)) return 0;
    if (/^99/.test(c)) return 0;
    const n = Number(c);
    if (n >= 10000 && n <= 19999) return 10;
    if (n >= 20000 && n <= 69999) return 90;
    return 0;
  }

  function determineGlobalPeriod(input){
    const i = input || {};
    const globalPeriodDays = inferGlobalPeriodDays(i.previousCode, i.metadata || i.previousMetadata || {});
    const postoperativeDay = daysBetween(i.previousDate, i.currentDate);
    const missing = [];
    if (!i.previousCode) missing.push('Previous CPT code');
    if (!i.previousDate) missing.push('Previous operation date');
    if (!i.currentDate) missing.push('Today operation date');
    const calculable = missing.length === 0 && postoperativeDay !== null;
    const inGlobalPeriod = calculable ? postoperativeDay >= 0 && postoperativeDay <= globalPeriodDays : null;
    return {
      previousCode: String(i.previousCode || ''),
      previousDate: i.previousDate || '',
      currentDate: i.currentDate || '',
      globalPeriodDays,
      postoperativeDay,
      inGlobalPeriod,
      calculable,
      missing,
      label: calculable
        ? ('Postoperative day ' + postoperativeDay + ' of a ' + globalPeriodDays + '-day global period. ' + (inGlobalPeriod ? 'Patient is still in the global period.' : 'Patient is outside the global period.'))
        : 'Global period cannot be calculated until the missing fields are documented.'
    };
  }

  function confidenceFromFacts(facts, missing, base){
    if ((missing || []).length) return 'Low';
    const count = (facts || []).length;
    if (base === 'high' && count >= 2) return 'High';
    if (count >= 2) return 'High';
    if (count === 1) return base === 'low' ? 'Moderate' : 'High';
    return 'Low';
  }

  function evaluateGlobalPeriod(answers){
    const a = answers || {};
    const facts = [];
    const educational = [];
    const missing = [];
    const globalStatus = a.globalStatus || null;
    if (globalStatus && globalStatus.calculable && globalStatus.inGlobalPeriod === false) {
      return {
        inGlobalPeriod: false,
        modifier: null,
        confidence: 'High',
        facts: [globalStatus.label],
        educationalGuidance: ['Postoperative modifiers 58, 78, and 79 are used when the current service occurs during the postoperative global period.'],
        documentationGaps: [],
        label: 'Outside postoperative global period',
        explanation: 'The calculated postoperative day is outside the previous CPT global period.'
      };
    }
    if (!yes(a.inGlobalPeriod)) {
      return {
        inGlobalPeriod: false,
        modifier: null,
        confidence: 'High',
        facts: globalStatus && globalStatus.calculable ? [globalStatus.label] : [],
        educationalGuidance: ['Standard Case Builder NCCI, MPPR, and multiple-procedure logic still applies.'],
        documentationGaps: [],
        label: 'No postoperative global modifier indicated',
        explanation: 'Case continues through standard NCCI, MPPR, and multiple-procedure logic.'
      };
    }
    if (!globalStatus || !globalStatus.calculable) missing.push('Previous CPT code, previous operation date, and today operation date are required to calculate global-period status.');
    else facts.push(globalStatus.label);
    if (a.sameSurgeon) facts.push('Same surgeon: ' + String(a.sameSurgeon) + '.');
    if (a.sameGroup) facts.push('Same group: ' + String(a.sameGroup) + '.');

    if (yes(a.planned) || yes(a.moreExtensive) || yes(a.therapyAfterDiagnostic)) {
      if (yes(a.planned)) facts.push('Documented as planned or anticipated at the original operation.');
      if (yes(a.moreExtensive)) facts.push('Documented as more extensive than the original procedure.');
      if (yes(a.therapyAfterDiagnostic)) facts.push('Documented as therapy following a diagnostic procedure.');
      educational.push('Modifier 58 applies to staged, more extensive, or therapeutic procedures during the postoperative period and begins a new global period.');
      return {
        inGlobalPeriod: true,
        modifier: '58',
        confidence: confidenceFromFacts(facts, missing, 'high'),
        facts,
        educationalGuidance: educational,
        documentationGaps: missing,
        reason: yes(a.planned) ? 'Planned or anticipated at the original operation.' :
          (yes(a.moreExtensive) ? 'More extensive than the original procedure.' : 'Therapy following a diagnostic procedure.'),
        education: CMS_LOGIC['58']
      };
    }
    if (yes(a.complicationReturnToOR)) {
      facts.push('Documented unplanned return to the operating room for a related postoperative complication.');
      if (a.complicationType) facts.push('Complication documented: ' + String(a.complicationType) + '.');
      educational.push('Modifier 78 applies to an unplanned return to the OR/procedure room for a related complication and does not begin a new global period.');
      return {
        inGlobalPeriod: true,
        modifier: '78',
        confidence: confidenceFromFacts(facts, missing, 'high'),
        facts,
        educationalGuidance: educational,
        documentationGaps: missing,
        reason: 'Unplanned return to the operating room for a related postoperative complication.',
        education: CMS_LOGIC['78']
      };
    }
    if (yes(a.unrelated)) {
      facts.push('Documented as unrelated to the prior operation.');
      if (a.unrelatedReason) facts.push('Unrelated rationale documented: ' + String(a.unrelatedReason) + '.');
      else missing.push('Specific unrelated diagnosis, site, or clinical problem.');
      educational.push('Modifier 79 applies to an unrelated procedure during the postoperative period and begins a new global period.');
      return {
        inGlobalPeriod: true,
        modifier: '79',
        confidence: confidenceFromFacts(facts, missing, 'moderate'),
        facts,
        educationalGuidance: educational,
        documentationGaps: missing,
        reason: 'Procedure is unrelated to the prior operation.',
        education: CMS_LOGIC['79']
      };
    }
    missing.push('Document whether the procedure was planned/staged, more extensive, therapy after diagnostic procedure, complication-related return to OR, or unrelated to the prior operation.');
    return {
      inGlobalPeriod: true,
      modifier: null,
      confidence: 'Low',
      facts,
      educationalGuidance: ['CMS postoperative modifiers require documented relationship to the prior operation.'],
      documentationGaps: missing,
      warning: 'Documentation may not support modifiers 58, 78, or 79 based on the selected answers.',
      education: null
    };
  }

  function extractOperativeNoteFindings(note){
    const report = String(note || '');
    const findings = [];
    const add = (key, label, value) => findings.push({ key, label, value: value || label });
    const time = report.match(/(?:operative|procedure|case)\s+time\s*(?:was|:)?\s*(\d{2,4})\s*(?:minutes|min)/i) || report.match(/(\d{2,4})\s*(?:minutes|min)\s+(?:of\s+)?(?:total\s+)?(?:operative|procedure|case)\s+time/i);
    if (time) add('operative time', 'Operative time', time[1] + ' minutes');
    const adhesiolysis = report.match(/(?:adhesiolysis|lysis of adhesions)[^.]{0,50}?(\d{2,4})\s*(?:minutes|min)/i) || report.match(/(\d{2,4})\s*(?:minutes|min)[^.]{0,50}?(?:adhesiolysis|lysis of adhesions)/i);
    if (adhesiolysis) add('adhesiolysis duration', 'Adhesiolysis duration', adhesiolysis[1] + ' minutes');
    const debridement = report.match(/debridement[^.]{0,120}?((?:skin|subcutaneous|fascia|muscle|bone)[^.]{0,80}?(?:\d+(?:\.\d+)?\s*(?:sq\s*cm|cm2|cm\^2)|\d+\s*x\s*\d+\s*cm))/i);
    if (debridement) add('debridement depth and size', 'Debridement depth and size', debridement[1].trim());
    MOD22_PATTERNS.forEach(pattern => {
      if (pattern.re.test(report) && !findings.some(f => f.key === pattern.key)) add(pattern.key, pattern.label);
    });
    return findings;
  }

  function analyzeModifier22(input){
    const i = input || {};
    const report = String(i.operativeReport || '');
    const findings = Array.isArray(i.objectiveFindings) ? i.objectiveFindings.filter(Boolean) : [];
    const extractedFindings = extractOperativeNoteFindings(report);
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

    const extractedAdhesiolysis = extractedFindings.find(f => f.key === 'adhesiolysis duration');
    const extractedTime = extractedFindings.find(f => f.key === 'operative time');
    const adhesiolysis = Number(i.adhesiolysisMinutes || (extractedAdhesiolysis && String(extractedAdhesiolysis.value).match(/\d+/)?.[0]) || 0);
    const total = Number(i.totalOperativeMinutes || i.actualMinutes || (extractedTime && String(extractedTime.value).match(/\d+/)?.[0]) || 0);
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
    const confidence = candidate ? (reasons.length >= 3 ? 'High' : 'Moderate') : (reasons.length === 1 ? 'Low' : 'Low');
    const documentationGaps = [];
    if (!report && findings.length === 0) documentationGaps.push('Operative note or objective findings.');
    if (!adhesiolysis && /adhesiolysis|lysis of adhesions/i.test(report)) documentationGaps.push('Duration of adhesiolysis.');
    if (!actual && !total) documentationGaps.push('Total operative time.');
    if (!expected) documentationGaps.push('Expected or typical operative time for comparison.');
    return {
      candidate,
      confidence,
      title: candidate ? 'Possible Modifier 22 Candidate' : 'Modifier 22 not strongly supported by objective criteria entered',
      reasons,
      extractedFindings,
      documentationGaps,
      educationalGuidance: ['Modifier 22 should be reviewed only when objective documentation supports substantially greater work than typical for the CPT code.'],
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
    determineGlobalPeriod,
    inferGlobalPeriodDays,
    extractOperativeNoteFindings,
    buildTimeline
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.GlobalModifierEngine = api;
})(typeof window !== 'undefined' ? window : globalThis);
