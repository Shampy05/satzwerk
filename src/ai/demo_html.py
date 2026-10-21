DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Satzwerk — Closed-Loop 5-Rung SLA Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .hidden-rung { display: none !important; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen py-10 px-4 font-sans">
  <div class="max-w-3xl mx-auto space-y-6">
    <!-- Header -->
    <header class="border-b border-slate-800 pb-4">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <span>⚡</span> Satzwerk
        </h1>
        <div class="flex items-center gap-2">
          <label for="cefrSelect" class="text-xs text-slate-400 font-medium">Target CEFR:</label>
          <select id="cefrSelect" onchange="onLevelChange()" class="bg-slate-800 border border-slate-700 text-indigo-300 text-xs font-mono rounded-lg px-2.5 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="A1">A1 (Foundation)</option>
            <option value="A2">A2 (Elementary)</option>
            <option value="B1" selected>B1 (Intermediate)</option>
            <option value="B2">B2 (Upper-Int)</option>
          </select>
          <span class="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
            Closed-Loop SLA
          </span>
        </div>
      </div>
      <p class="text-sm text-slate-400 mt-1">
        Active German morphosyntactic production:
        <span class="text-indigo-400 font-medium">L1 Locate</span> &rarr;
        <span class="text-amber-400 font-medium">L2 Underline</span> &rarr;
        <span class="text-sky-400 font-medium">L3 Category Badge</span> &rarr;
        <span class="text-amber-300 font-medium">L4 Rule Hint</span> &rarr;
        <span class="text-emerald-400 font-medium">L5 Rewrite</span>.
      </p>
    </header>

    <!-- Optional Auth / Error Ledger Bar -->
    <div class="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50 space-y-3">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div class="flex items-center gap-2 flex-1 min-w-[240px]">
          <span class="text-xs font-semibold text-slate-400 shrink-0">🔑 JWT Token (Optional):</span>
          <input id="jwtInput" type="password" oninput="onTokenChange()" placeholder="Paste access_token to enable PostgreSQL Error Ledger..." class="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
        </div>
        <button onclick="fetchWeaknesses()" class="text-xs px-3 py-1 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-slate-300 border border-slate-600/50 transition">
          📊 Refresh Ledger
        </button>
      </div>
      <div id="ledgerBar" class="flex items-center gap-2 flex-wrap text-xs">
        <span class="text-slate-500">Top Weaknesses (Error Ledger):</span>
        <span id="ledgerBadges" class="text-slate-400 italic">Guest mode (paste JWT token to track &amp; weight personal errors)</span>
      </div>
    </div>

    <!-- Step 1: Playful Writing Prompt Elicitation Card -->
    <div class="bg-gradient-to-br from-indigo-950/50 via-slate-800/70 to-slate-800/60 rounded-xl p-5 border border-indigo-500/30 space-y-3 shadow-lg">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400">Step 1 &bull; Elicitation Prompt</span>
          <div id="promptTargets" class="flex items-center gap-1.5"></div>
        </div>
        <button id="promptBtn" onclick="generatePrompt()" class="text-xs px-3.5 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-500 text-white font-medium transition flex items-center gap-1.5 shadow">
          <span id="promptSpinner" class="hidden animate-spin">&#9696;</span>
          <span id="promptBtnText">🎲 Generate Fun Writing Prompt</span>
        </button>
      </div>
      <p id="promptText" class="text-sm text-slate-200 leading-relaxed">
        Click <strong>"🎲 Generate Fun Writing Prompt"</strong> to get a playful scenario tailored to your CEFR level and Error Ledger weaknesses—or write freely below!
      </p>
    </div>

    <!-- Step 2: Draft & Multi-Attempt Revision Box -->
    <div class="bg-slate-800/60 rounded-xl p-5 border border-slate-700/60 space-y-4 shadow-xl">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2.5">
          <label for="draftInput" class="text-sm font-semibold text-slate-300">Step 2 &bull; Your German Draft</label>
          <span id="attemptBadge" class="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono border border-slate-600">
            Attempt #1 (Initial Draft)
          </span>
        </div>
        <span class="text-xs text-slate-400">Wrap uncertain words with <code class="text-indigo-300 bg-slate-900 px-1 py-0.5 rounded border border-slate-700">?words?</code></span>
      </div>

      <textarea id="draftInput" rows="4" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-200 placeholder-slate-600 font-mono" placeholder="e.g. Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.">Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.</textarea>

      <!-- Revision Guidance Banner (Shown when user is on Attempt 2+ or has active errors) -->
      <div id="revisionBanner" class="hidden text-xs bg-amber-950/40 border border-amber-700/50 text-amber-200 p-3 rounded-lg flex items-center justify-between gap-3">
        <div>
          <strong>🔄 Self-Repair Mode:</strong> Use the L1–L4 hints below to edit your sentence above and click <strong>"Re-Submit Revised Draft"</strong> to see if you fixed the errors on your own! <em>(Revisions don't double-penalize your Error Ledger.)</em>
        </div>
        <button onclick="resetDraftAttempt()" class="shrink-0 text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 transition">
          New Draft
        </button>
      </div>

      <div class="flex items-center justify-between pt-1 flex-wrap gap-2">
        <div class="flex gap-2 flex-wrap">
          <button onclick="setExample(1)" class="text-xs px-2.5 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition">Example 1 (Case &amp; WO)</button>
          <button onclick="setExample(2)" class="text-xs px-2.5 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition">Example 2 (Valid ?Hypothesis?)</button>
          <button onclick="setExample(3)" class="text-xs px-2.5 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition">Example 3 (Clean Draft)</button>
        </div>
        <button id="analyzeBtn" onclick="analyzeDraft()" class="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition shadow-lg shadow-indigo-600/30 flex items-center gap-2">
          <span id="btnSpinner" class="hidden animate-spin">&#9696;</span>
          <span id="btnText">Analyze Draft (Attempt #1)</span>
        </button>
      </div>

      <!-- Live Pipeline Status Progress -->
      <div id="statusIndicator" class="hidden text-xs text-indigo-300 bg-indigo-950/40 border border-indigo-800/40 p-2.5 rounded-lg flex items-center gap-2 animate-pulse">
        <span>🔄</span> <span id="statusText">Running 2-stage verification (Generator &rarr; Deterministic Gate &rarr; Critic LLM)...</span>
      </div>
    </div>

    <!-- Confirmed Hypotheses Banner -->
    <div id="confirmedBanner" class="hidden p-4 rounded-xl text-sm border bg-emerald-950/30 border-emerald-700/50 text-emerald-200 space-y-1"></div>

    <!-- Error/Notice Banner -->
    <div id="noticeBanner" class="hidden p-4 rounded-xl text-sm border"></div>

    <!-- Results Section -->
    <div id="resultsSection" class="space-y-4 hidden">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">Detected Feedback Cards (5-Rung Ladder)</h2>
        <span id="cardCount" class="text-xs text-slate-500"></span>
      </div>
      <div id="cardsContainer" class="space-y-4"></div>
    </div>
  </div>

  <script>
    const TAXONOMY_DESCRIPTIONS = {
      "WO-V2": { name: "Verb-Second in Main Clauses", cefr: "A1", hint: "The finite verb must be the second constituent." },
      "WO-SEP": { name: "Separable-Verb Split", cefr: "A1", hint: "Separable prefix moves to the clause end." },
      "WO-VF": { name: "Verb-Final in Subordinate Clauses", cefr: "A2", hint: "Finite verb goes to the end after weil/dass/wenn/ob." },
      "WO-KLAM": { name: "Verbal Bracket (Satzklammer)", cefr: "A1", hint: "Participle or infinitive stays at the very end." },
      "WO-TMP": { name: "TeKaMoLo Ordering", cefr: "B1", hint: "Adverbial order: Temporal before Manner before Place." },
      "KAS-AKK": { name: "Accusative Direct Object", cefr: "A1", hint: "Direct objects take accusative case." },
      "KAS-DAT": { name: "Dative Object / Dative Verb", cefr: "A2", hint: "Indirect objects or dative verbs (helfen, danken) take dative." },
      "KAS-GEN": { name: "Genitive Case", cefr: "B2", hint: "Possession or genitive prepositions (wegen, während, trotz)." },
      "KAS-PREP": { name: "Fixed Preposition Case", cefr: "A2", hint: "mit/aus/bei/nach/von/zu require Dative; für/ohne/gegen require Accusative." },
      "KAS-2WEG": { name: "Two-Way Preposition (Wechselpräposition)", cefr: "A2", hint: "Accusative for direction/motion, Dative for fixed location." },
      "ADJ-END": { name: "Adjective Declension", cefr: "B1", hint: "Adjective ending must match the article and case pattern." },
      "ART-GEN": { name: "Article & Gender Agreement", cefr: "A1", hint: "The determiner must match the grammatical gender of the noun." },
      "N-PL": { name: "Plural Formation", cefr: "A1", hint: "Incorrect plural noun ending." },
      "PRO-REL": { name: "Relative Pronoun", cefr: "B1", hint: "Relative pronoun agrees in gender/number with antecedent." },
      "PRO-KAS": { name: "Pronoun Case Reference", cefr: "A2", hint: "Check personal pronoun case (mir vs. mich, ihm vs. ihn)." },
      "V-KONJ": { name: "Verb Conjugation", cefr: "A1", hint: "Subject-verb agreement or stem vowel change in present tense." },
      "V-TEMP": { name: "Tense Formation", cefr: "A2", hint: "Perfekt auxiliary (haben vs. sein) or past tense form." },
      "V-PART": { name: "Participle Formation", cefr: "A2", hint: "Formation of Partizip II (ge- prefix, -t vs. -en ending)." },
      "V-K2": { name: "Konjunktiv II", cefr: "B1", hint: "Hypothetical, polite, or subjunctive verb forms." },
      "V-REFL": { name: "Reflexive Pronoun", cefr: "A2", hint: "Missing or incorrect reflexive pronoun (sich freuen)." },
      "PREP-W": { name: "Preposition Choice", cefr: "B1", hint: "Wrong preposition used for a verb or noun idiom." },
      "ORTH": { name: "Spelling & Capitalization", cefr: "A1", hint: "Check noun capitalization, umlauts, or ß/ss." },
      "WORTW": { name: "Word Choice", cefr: "B2", hint: "Grammatically valid but unidiomatic German phrasing." },
      "SONST": { name: "General Syntax / Other", cefr: "B2", hint: "Grammar issue not covered by other specific codes." }
    };

    let attemptNumber = 1;
    let isRevision = false;

    function getHeaders() {
      const headers = { 'Content-Type': 'application/json' };
      const token = document.getElementById('jwtInput').value.trim();
      if (token) {
        headers['Authorization'] = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      }
      return headers;
    }

    function updateAttemptUI() {
      const badge = document.getElementById('attemptBadge');
      const btnText = document.getElementById('btnText');
      const revBanner = document.getElementById('revisionBanner');

      if (isRevision) {
        badge.textContent = `Attempt #${attemptNumber} (Revision)`;
        badge.className = "text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono border border-amber-500/40";
        btnText.textContent = `🔄 Re-Submit Revised Draft (Attempt #${attemptNumber})`;
        revBanner.classList.remove('hidden');
      } else {
        badge.textContent = "Attempt #1 (Initial Draft)";
        badge.className = "text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono border border-slate-600";
        btnText.textContent = "Analyze Draft (Attempt #1)";
        revBanner.classList.add('hidden');
      }
    }

    function resetDraftAttempt() {
      attemptNumber = 1;
      isRevision = false;
      updateAttemptUI();
      document.getElementById('resultsSection').classList.add('hidden');
      document.getElementById('noticeBanner').classList.add('hidden');
      document.getElementById('confirmedBanner').classList.add('hidden');
    }

    function onLevelChange() {
      if (document.getElementById('jwtInput').value.trim()) {
        fetchWeaknesses();
      }
    }

    function onTokenChange() {
      const token = document.getElementById('jwtInput').value.trim();
      if (token) {
        fetchWeaknesses();
      } else {
        document.getElementById('ledgerBadges').innerHTML =
          '<span class="text-slate-400 italic">Guest mode (paste JWT token to track &amp; weight personal errors)</span>';
      }
    }

    async function fetchWeaknesses() {
      const token = document.getElementById('jwtInput').value.trim();
      const ledgerBadges = document.getElementById('ledgerBadges');
      if (!token) {
        ledgerBadges.innerHTML = '<span class="text-slate-400 italic">Guest mode (paste JWT token to track &amp; weight personal errors)</span>';
        return;
      }

      try {
        const res = await fetch('/ai/weaknesses', { headers: getHeaders() });
        if (!res.ok) throw new Error('Unauthorized or invalid token');
        const codes = await res.json();
        if (!codes.length) {
          ledgerBadges.innerHTML = '<span class="text-emerald-400">No recorded errors in ledger yet!</span>';
          return;
        }
        ledgerBadges.innerHTML = codes.map((code, i) => {
          const meta = TAXONOMY_DESCRIPTIONS[code] || { name: code, cefr: '?' };
          return `<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono">#${i + 1} ${code} (${meta.cefr})</span>`;
        }).join(' ');
      } catch (err) {
        ledgerBadges.innerHTML = `<span class="text-rose-400">${err.message}</span>`;
      }
    }

    async function generatePrompt() {
      const btn = document.getElementById('promptBtn');
      const spinner = document.getElementById('promptSpinner');
      const btnText = document.getElementById('promptBtnText');
      const promptText = document.getElementById('promptText');
      const promptTargets = document.getElementById('promptTargets');
      const level = document.getElementById('cefrSelect').value;

      btn.disabled = true;
      spinner.classList.remove('hidden');
      btnText.textContent = "Generating...";

      try {
        const res = await fetch(`/ai/writing_prompt?target_level=${encodeURIComponent(level)}`, {
          headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || data.detail || 'Failed to generate prompt');

        promptText.textContent = data.prompt;
        promptTargets.innerHTML = (data.target_patterns || []).map(code => {
          const meta = TAXONOMY_DESCRIPTIONS[code] || { cefr: '' };
          return `<span class="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-mono" title="${meta.name || code}">🎯 ${code}</span>`;
        }).join('');

        // Starting a new prompt resets the attempt counter to Attempt #1
        resetDraftAttempt();
      } catch (err) {
        promptText.innerHTML = `<span class="text-rose-400">Error: ${err.message}</span>`;
      } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
        btnText.textContent = "🎲 Generate Fun Writing Prompt";
      }
    }

    function setExample(num) {
      const input = document.getElementById('draftInput');
      if (num === 1) {
        input.value = "Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.";
      } else if (num === 2) {
        input.value = "Ich helfe ?dem Mann?, weil ich heute Zeit habe.";
      } else {
        input.value = "Gestern bin ich mit meiner Schwester ins Kino gegangen.";
      }
      resetDraftAttempt();
    }

    function focusQuoteInDraft(quote) {
      const textarea = document.getElementById('draftInput');
      textarea.focus();
      const idx = textarea.value.indexOf(quote);
      if (idx !== -1) {
        textarea.setSelectionRange(idx, idx + quote.length);
      }
    }

    async function analyzeDraft() {
      const text = document.getElementById('draftInput').value.trim();
      if (!text) return;

      const level = document.getElementById('cefrSelect').value;
      const btn = document.getElementById('analyzeBtn');
      const btnText = document.getElementById('btnText');
      const spinner = document.getElementById('btnSpinner');
      const notice = document.getElementById('noticeBanner');
      const confirmedBanner = document.getElementById('confirmedBanner');
      const resultsSection = document.getElementById('resultsSection');
      const cardsContainer = document.getElementById('cardsContainer');
      const cardCount = document.getElementById('cardCount');
      const statusIndicator = document.getElementById('statusIndicator');

      btn.disabled = true;
      btnText.textContent = "Analyzing...";
      spinner.classList.remove('hidden');
      statusIndicator.classList.remove('hidden');
      notice.classList.add('hidden');
      confirmedBanner.classList.add('hidden');
      resultsSection.classList.add('hidden');
      cardsContainer.innerHTML = '';

      try {
        const response = await fetch('/ai/analyze-draft', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            sentence: text,
            target_level: level,
            is_revision: isRevision
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || data.detail || 'Analysis failed.');
        }

        // Refresh ledger if logged in and this was an initial draft
        if (!isRevision && document.getElementById('jwtInput').value.trim()) {
          fetchWeaknesses();
        }

        // Display confirmed inline '?' hypotheses if any
        if (data.confirmed_hypotheses && data.confirmed_hypotheses.length > 0) {
          const pills = data.confirmed_hypotheses.map(
            h => `<code class="px-2 py-0.5 rounded bg-emerald-900/60 border border-emerald-600/50 text-emerald-200 font-mono">✓ ${h}</code>`
          ).join(' ');
          confirmedBanner.innerHTML = `
            <div class="font-semibold text-emerald-300">✅ Confirmed Inline Hypotheses (?...?):</div>
            <div class="text-xs text-emerald-200/90 flex items-center gap-2 flex-wrap pt-1">
              Your marked hypothesis was 100% grammatically correct: ${pills}
            </div>
          `;
          confirmedBanner.classList.remove('hidden');
        }

        // If 0 error cards -> Success!
        if (!data.cards || data.cards.length === 0) {
          notice.className = "p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-800/60 text-emerald-300 block";
          if (isRevision) {
            notice.innerHTML = `🎉 <strong>All errors resolved on Attempt #${attemptNumber}!</strong> Your self-correction succeeded. Click <strong>"🎲 Generate Fun Writing Prompt"</strong> above for your next challenge!`;
          } else {
            notice.innerHTML = "🎉 <strong>Clean draft on your first try!</strong> Zero grammatical errors detected.";
          }
          attemptNumber = 1;
          isRevision = false;
          updateAttemptUI();
          return;
        }

        // Errors were found -> Enter Revision Mode so the learner can edit & retry!
        attemptNumber += 1;
        isRevision = true;
        updateAttemptUI();

        cardCount.textContent = `${data.cards.length} error card(s) remaining — edit your draft above to fix them!`;
        resultsSection.classList.remove('hidden');

        data.cards.forEach((card, idx) => {
          const meta = TAXONOMY_DESCRIPTIONS[card.pattern_code] || { name: card.pattern_code, cefr: "?", hint: "Grammar category" };
          const safeQuote = card.quote.replace(/'/g, "\\'");
          const cardEl = document.createElement('div');
          cardEl.className = "bg-slate-800/70 border border-slate-700/80 rounded-xl p-5 space-y-4 shadow-lg";

          cardEl.innerHTML = `
            <!-- Top Section: L1 & L2 (Underline) -->
            <div class="flex items-start justify-between gap-4 flex-wrap">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-700 text-indigo-300 border border-indigo-400/20 font-mono">
                    L1: Sentence ${card.sentence_index + 1}
                  </span>
                  <span class="text-xs text-slate-400">Underlined Error (L2):</span>
                </div>
                <div class="text-xl font-mono font-medium text-amber-300 underline decoration-wavy decoration-amber-500/80 underline-offset-4">
                  "${card.quote}"
                </div>
              </div>
              <button onclick="focusQuoteInDraft('${safeQuote}')" class="text-xs px-3 py-1.5 rounded-lg bg-slate-700/70 hover:bg-indigo-600/40 text-slate-200 border border-slate-600 transition flex items-center gap-1.5">
                <span>✏️</span> Edit &amp; Fix in Draft
              </button>
            </div>

            <!-- Graduated Ladder Rungs -->
            <div class="space-y-3 pt-2 border-t border-slate-700/40">
              <!-- L3: Category Badge (Hidden initially) -->
              <div id="rung3-${idx}" class="hidden-rung bg-slate-900/80 p-3.5 rounded-lg border border-sky-500/30 flex items-center justify-between gap-4 flex-wrap">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-sky-400 uppercase tracking-wide">L3 &bull; Grammar Category Badge</span>
                    <span class="px-2 py-0.5 rounded font-mono font-bold text-xs bg-sky-500/20 text-sky-300 border border-sky-500/40">
                      ${card.pattern_code}
                    </span>
                    <span class="px-1.5 py-0.5 rounded font-mono text-xs bg-slate-800 text-slate-300 border border-slate-700">
                      CEFR ${meta.cefr}
                    </span>
                  </div>
                  <div class="text-sm font-medium text-white">${meta.name}</div>
                  <div class="text-xs text-slate-400">${meta.hint}</div>
                </div>
                <button onclick="revealRung(${idx}, 4)" id="btnRung4-${idx}" class="shrink-0 text-xs px-3 py-2 rounded-md bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 transition">
                  Still Stuck? &rarr; Reveal Rule Hint (L4)
                </button>
              </div>

              <!-- L4: Rule Hint (Hidden initially) -->
              <div id="rung4-${idx}" class="hidden-rung bg-amber-500/10 p-4 rounded-lg border border-amber-500/30 space-y-2">
                <div class="flex items-center justify-between gap-2 flex-wrap">
                  <span class="text-xs font-semibold text-amber-300 uppercase tracking-wide">L4 &bull; Pedagogical Rule Hint (Zero Answer Leaks)</span>
                  <button onclick="revealRung(${idx}, 5)" id="btnRung5-${idx}" class="text-xs px-3 py-1.5 rounded-md bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-200 border border-emerald-500/40 transition">
                    Give Up? &rarr; Reveal Target Rewrite (L5)
                  </button>
                </div>
                <p class="text-sm text-slate-200 leading-relaxed font-sans">${card.explanation}</p>
              </div>

              <!-- L5: Clean Rewrite (Hidden initially) -->
              <div id="rung5-${idx}" class="hidden-rung bg-emerald-500/10 p-4 rounded-lg border border-emerald-500/30 space-y-1.5">
                <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wide block">L5 &bull; Target Correction (Final Clean Rewrite)</span>
                <div class="text-lg font-mono font-bold text-emerald-300">${card.correction}</div>
              </div>
            </div>

            <!-- Initial Action Button (Reveal L3) -->
            <div id="initialBtnBox-${idx}" class="pt-1">
              <button onclick="revealRung(${idx}, 3)" class="text-xs px-3.5 py-2 rounded-md bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 font-medium transition flex items-center gap-1.5">
                <span>🏷️</span> Need a Clue? Reveal Category Badge (L3)
              </button>
            </div>
          `;

          cardsContainer.appendChild(cardEl);
        });

      } catch (err) {
        notice.className = "p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800/60 text-rose-300 block";
        notice.textContent = `Error: ${err.message}`;
      } finally {
        btn.disabled = false;
        updateAttemptUI();
        spinner.classList.add('hidden');
        statusIndicator.classList.add('hidden');
      }
    }

    function revealRung(cardIdx, rungNumber) {
      const rungEl = document.getElementById(`rung${rungNumber}-${cardIdx}`);
      if (rungEl) {
        rungEl.classList.remove('hidden-rung');
      }
      if (rungNumber === 3) {
        const initBox = document.getElementById(`initialBtnBox-${cardIdx}`);
        if (initBox) initBox.classList.add('hidden');
      } else if (rungNumber === 4) {
        const btn4 = document.getElementById(`btnRung4-${cardIdx}`);
        if (btn4) btn4.classList.add('hidden');
      } else if (rungNumber === 5) {
        const btn5 = document.getElementById(`btnRung5-${cardIdx}`);
        if (btn5) btn5.classList.add('hidden');
      }
    }
  </script>
</body>
</html>
"""
