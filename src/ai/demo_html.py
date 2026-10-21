DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Satzwerk — 5-Rung SLA Feedback Ladder</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .hidden-rung { display: none !important; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen py-10 px-4 font-sans">
  <div class="max-w-3xl mx-auto space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <span>⚡</span> Satzwerk
        </h1>
        <span class="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
          5-Rung SLA Prototype
        </span>
      </div>
      <p class="text-sm text-slate-400 mt-1">
        Active German morphosyntactic feedback ladder: 
        <span class="text-indigo-400 font-medium">L1 Locate</span> &rarr; 
        <span class="text-amber-400 font-medium">L2 Underline</span> &rarr; 
        <span class="text-sky-400 font-medium">L3 Category Badge</span> &rarr; 
        <span class="text-amber-300 font-medium">L4 Rule Hint</span> &rarr; 
        <span class="text-emerald-400 font-medium">L5 Rewrite</span>.
      </p>
    </header>

    <!-- Input Section -->
    <div class="bg-slate-800/60 rounded-xl p-5 border border-slate-700/60 space-y-4 shadow-xl">
      <div class="flex items-center justify-between">
        <label class="text-sm font-semibold text-slate-300">Your German Draft</label>
        <span class="text-xs text-slate-400">Wrap uncertain words with <code class="text-indigo-300 bg-slate-900 px-1 py-0.5 rounded border border-slate-700">?words?</code></span>
      </div>
      <textarea id="draftInput" rows="4" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-200 placeholder-slate-600 font-mono" placeholder="e.g. Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.">Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.</textarea>
      
      <div class="flex items-center justify-between pt-2">
        <div class="flex gap-2">
          <button onclick="setExample(1)" class="text-xs px-2.5 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition">Example 1 (Case & WO)</button>
          <button onclick="setExample(2)" class="text-xs px-2.5 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition">Example 2 (Hypothesis ?)</button>
        </div>
        <button id="analyzeBtn" onclick="analyzeDraft()" class="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition shadow-lg shadow-indigo-600/30 flex items-center gap-2">
          <span id="btnSpinner" class="hidden animate-spin">&#9696;</span>
          <span id="btnText">Analyze Draft</span>
        </button>
      </div>

      <!-- Live Pipeline Status Progress -->
      <div id="statusIndicator" class="hidden text-xs text-indigo-300 bg-indigo-950/40 border border-indigo-800/40 p-2.5 rounded-lg flex items-center gap-2 animate-pulse">
        <span>🔄</span> <span id="statusText">Running 2-stage verification (Generator &rarr; Deterministic Gate &rarr; Critic LLM)...</span>
      </div>
    </div>

    <!-- Error/Notice Banner -->
    <div id="noticeBanner" class="hidden p-4 rounded-xl text-sm border"></div>

    <!-- Results Section -->
    <div id="resultsSection" class="space-y-4 hidden">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">Detected Feedback Cards</h2>
        <span id="cardCount" class="text-xs text-slate-500"></span>
      </div>
      <div id="cardsContainer" class="space-y-4"></div>
    </div>
  </div>

  <script>
    // Taxonomy metadata for informative L3 badges with CEFR alignment
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

    function setExample(num) {
      const input = document.getElementById('draftInput');
      if (num === 1) {
        input.value = "Ich gehe zu den Bahnhof, weil ich habe keine Zeit.";
      } else {
        input.value = "Ich habe gestern ?ein Buch? auf der Tisch gelegt.";
      }
    }

    async function analyzeDraft() {
      const text = document.getElementById('draftInput').value.trim();
      if (!text) return;

      const btn = document.getElementById('analyzeBtn');
      const btnText = document.getElementById('btnText');
      const spinner = document.getElementById('btnSpinner');
      const notice = document.getElementById('noticeBanner');
      const resultsSection = document.getElementById('resultsSection');
      const cardsContainer = document.getElementById('cardsContainer');
      const cardCount = document.getElementById('cardCount');
      const statusIndicator = document.getElementById('statusIndicator');

      btn.disabled = true;
      btnText.textContent = "Analyzing...";
      spinner.classList.remove('hidden');
      statusIndicator.classList.remove('hidden');
      notice.classList.add('hidden');
      resultsSection.classList.add('hidden');
      cardsContainer.innerHTML = '';

      try {
        const response = await fetch('/ai/analyze-draft', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sentence: text })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || data.detail || 'Analysis failed.');
        }

        const hasErrors = data.cards && data.cards.length > 0;
        const hasConfirmed = data.confirmed_hypotheses && data.confirmed_hypotheses.length > 0;

        if (!hasErrors && !hasConfirmed) {
          notice.className = "p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-800/60 text-emerald-300 block";
          notice.textContent = "🎉 Clean draft! Zero grammatical errors detected.";
          return;
        }

        if (hasConfirmed) {
          data.confirmed_hypotheses.forEach(h => {
            const confEl = document.createElement('div');
            confEl.className = "p-3.5 bg-emerald-950/50 border border-emerald-500/40 rounded-xl text-emerald-300 text-sm flex items-center gap-2 shadow-lg";
            confEl.innerHTML = `<span>✨</span><span><strong>Hypothesis Confirmed:</strong> Your marked phrase <code class="bg-emerald-900/60 px-1.5 py-0.5 rounded text-white font-mono font-bold">"${h}"</code> is 100% grammatically correct!</span>`;
            cardsContainer.appendChild(confEl);
          });
        }

        if (!hasErrors) {
          cardCount.textContent = "0 errors (hypotheses verified)";
          resultsSection.classList.remove('hidden');
          return;
        }

        cardCount.textContent = `${data.cards.length} error card(s) identified`;
        resultsSection.classList.remove('hidden');

        data.cards.forEach((card, idx) => {
          const meta = TAXONOMY_DESCRIPTIONS[card.pattern_code] || { name: card.pattern_code, hint: "Grammar category" };
          const cardEl = document.createElement('div');
          cardEl.className = "bg-slate-800/70 border border-slate-700/80 rounded-xl p-5 space-y-4 shadow-lg";

          cardEl.innerHTML = `
            <!-- Top Section: L1 & L2 (Underline) -->
            <div class="flex items-start justify-between gap-4">
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
            </div>

            <!-- Graduated Ladder Rungs -->
            <div class="space-y-3 pt-2 border-t border-slate-700/40">
              
              <!-- L3: Category Badge (Hidden initially) -->
              <div id="rung3-${idx}" class="hidden-rung bg-slate-900/80 p-3.5 rounded-lg border border-sky-500/30 flex items-center justify-between gap-4">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-sky-400 uppercase tracking-wide">L3 &bull; Grammar Category Badge</span>
                    <span class="px-2 py-0.5 rounded font-mono font-bold text-xs bg-sky-500/20 text-sky-300 border border-sky-500/40">
                      ${card.pattern_code}
                    </span>
                    ${meta.cefr ? `<span class="px-2 py-0.5 rounded font-mono font-bold text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">${meta.cefr}</span>` : ''}
                  </div>
                  <div class="text-sm font-medium text-white">${meta.name}</div>
                  <div class="text-xs text-slate-400">${meta.hint}</div>
                </div>
                <button onclick="revealRung(${idx}, 4)" id="btnRung4-${idx}" class="shrink-0 text-xs px-3 py-2 rounded-md bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 transition">
                  Need Help? &rarr; Reveal Hint (L4)
                </button>
              </div>

              <!-- L4: Rule Hint (Hidden initially) -->
              <div id="rung4-${idx}" class="hidden-rung bg-amber-500/10 p-4 rounded-lg border border-amber-500/30 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold text-amber-300 uppercase tracking-wide">L4 &bull; Pedagogical Rule Hint (Zero Answer Leaks)</span>
                  <button onclick="revealRung(${idx}, 5)" id="btnRung5-${idx}" class="text-xs px-3 py-1.5 rounded-md bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-200 border border-emerald-500/40 transition">
                    Stuck? &rarr; Reveal Answer (L5)
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
                <span>🏷️</span> Step 1: Reveal Category Badge (L3)
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
        btnText.textContent = "Analyze Draft";
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
