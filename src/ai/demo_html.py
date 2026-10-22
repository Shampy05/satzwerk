DEMO_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Satzwerk</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }
        }
      }
    }
  </script>
  <style>
    body {
      background-color: #F8FAFC;
      color: #0F172A;
      -webkit-font-smoothing: antialiased;
    }
    .hidden-rung {
      display: none !important;
    }
    .error-underline {
      text-decoration: underline;
      text-decoration-color: #E11D48;
      text-decoration-style: wavy;
      text-decoration-thickness: 1.5px;
      text-underline-offset: 4px;
    }
  </style>
</head>
<body class="min-h-screen font-sans">

  <!-- Minimal Top Navigation -->
  <header class="max-w-2xl mx-auto px-4 pt-8 pb-4 flex items-center justify-between gap-3">
    <div class="flex items-center gap-2.5">
      <div class="w-2.5 h-2.5 rounded-full bg-zinc-900"></div>
      <span class="font-semibold text-lg tracking-tight text-zinc-900">Satzwerk</span>
    </div>

    <div class="flex items-center gap-2">
      <!-- Language Pill -->
      <div class="inline-flex bg-zinc-200/70 p-0.5 rounded-lg text-xs font-medium">
        <button type="button" onclick="selectLanguage('de')" data-lang="de" class="lang-btn px-2.5 py-1 rounded-md transition bg-white text-zinc-900 shadow-sm">German</button>
        <button type="button" onclick="selectLanguage('fr')" data-lang="fr" class="lang-btn px-2.5 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900">French</button>
      </div>
      <select id="languageSelect" onchange="onLanguageChange()" class="sr-only" aria-hidden="true">
        <option value="de" selected>de</option>
        <option value="fr">fr</option>
      </select>

      <!-- CEFR Level Pill -->
      <div class="inline-flex bg-zinc-200/70 p-0.5 rounded-lg text-xs font-medium">
        <button type="button" onclick="selectCefr('A1')" data-cefr="A1" class="cefr-btn px-2 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900">A1</button>
        <button type="button" onclick="selectCefr('A2')" data-cefr="A2" class="cefr-btn px-2 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900">A2</button>
        <button type="button" onclick="selectCefr('B1')" data-cefr="B1" class="cefr-btn px-2 py-1 rounded-md transition bg-white text-zinc-900 shadow-sm">B1</button>
        <button type="button" onclick="selectCefr('B2')" data-cefr="B2" class="cefr-btn px-2 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900">B2</button>
      </div>
      <select id="cefrSelect" onchange="onLevelChange()" class="sr-only" aria-hidden="true">
        <option value="A1">A1</option>
        <option value="A2">A2</option>
        <option value="B1" selected>B1</option>
        <option value="B2">B2</option>
      </select>

      <!-- Subtle Ledger / Auth Toggle -->
      <button
        type="button"
        onclick="toggleLedgerDrawer()"
        title="Personal Error Ledger"
        class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/60 transition"
      >
        <span id="authStatusDot" class="w-1.5 h-1.5 rounded-full bg-zinc-400"></span>
        <span>Ledger</span>
      </button>
    </div>
  </header>

  <main class="max-w-2xl mx-auto px-4 pb-16 space-y-5">

    <!-- Collapsible Personal Error Ledger Drawer (Hidden by default) -->
    <div id="ledgerDrawer" class="hidden bg-white rounded-xl border border-zinc-200/80 p-4 shadow-sm space-y-3">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <span class="text-xs font-medium text-zinc-700">Personal Error Ledger</span>
        <div id="ledgerBadges" class="flex items-center gap-1.5 flex-wrap text-xs text-zinc-500">
          <span>Guest mode — add token to track recurring grammar gaps</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <input
          id="jwtInput"
          type="password"
          oninput="onTokenChange()"
          placeholder="Paste Bearer access_token (optional)..."
          class="flex-1 bg-zinc-50 border border-zinc-200 rounded-lg px-3 py-1.5 text-xs font-mono text-zinc-800 placeholder-zinc-400 focus:outline-none focus:border-zinc-400"
        />
        <button
          type="button"
          onclick="fetchWeaknesses()"
          class="px-3 py-1.5 rounded-lg text-xs font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition"
        >
          Sync
        </button>
      </div>
    </div>

    <!-- Unified Writing Studio Card -->
    <div class="bg-white rounded-2xl border border-zinc-200/90 shadow-sm overflow-hidden">

      <!-- Top Prompt Bar inside the Card -->
      <div class="px-5 py-3.5 bg-zinc-50/70 border-b border-zinc-100 flex items-center justify-between gap-3 flex-wrap">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-xs font-medium text-zinc-500">Writing Prompt</span>
          <div id="promptTargets" class="flex items-center gap-1"></div>
        </div>
        <button
          id="promptBtn"
          type="button"
          onclick="generatePrompt()"
          class="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-700 hover:text-zinc-950 bg-white hover:bg-zinc-50 border border-zinc-200/90 rounded-lg px-2.5 py-1 shadow-2xs transition"
        >
          <svg id="promptSpinner" class="hidden animate-spin w-3 h-3 text-zinc-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9" stroke-opacity="0.25"></circle>
            <path d="M21 12a9 9 0 0 1-9 9"></path>
          </svg>
          <span id="promptBtnText">Generate Topic</span>
        </button>
      </div>

      <!-- Generated Prompt Text (Only shown when a topic is generated) -->
      <div id="promptBox" class="hidden px-5 py-3.5 bg-zinc-50/40 border-b border-zinc-100">
        <p id="promptText" class="text-sm text-zinc-700 leading-relaxed"></p>
      </div>

      <!-- Revision Mode Banner (Only shown on Attempt 2+) -->
      <div id="revisionBanner" class="hidden px-5 py-2.5 bg-amber-50/80 border-b border-amber-200/60 flex items-center justify-between gap-3 text-xs text-amber-900">
        <span>
          <strong class="font-medium">Revision mode:</strong> Use the hints below to fix your sentence and check again.
        </span>
        <button
          type="button"
          onclick="resetDraftAttempt()"
          class="text-xs font-medium text-amber-800 hover:text-amber-950 underline underline-offset-2 shrink-0"
        >
          Start over
        </button>
      </div>

      <!-- Main Textarea -->
      <div class="p-5">
        <textarea
          id="draftInput"
          rows="4"
          onkeydown="handleEditorKeydown(event)"
          class="w-full bg-transparent text-base sm:text-[17px] text-zinc-900 leading-relaxed placeholder-zinc-400 focus:outline-none resize-y"
          placeholder="Write a sentence or short paragraph..."
        >Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.</textarea>
      </div>

      <!-- Confirmed Hypotheses Banner -->
      <div id="confirmedBanner" class="hidden mx-5 mb-4 px-3.5 py-2.5 rounded-xl bg-emerald-50 border border-emerald-200/70 text-xs text-emerald-900"></div>

      <!-- Card Footer Toolbar -->
      <div class="px-5 py-3 bg-zinc-50/50 border-t border-zinc-100 flex items-center justify-between flex-wrap gap-3">
        <!-- Quick Examples & ? Tip -->
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-xs text-zinc-400 mr-1">Try:</span>
          <button type="button" onclick="setExample(1)" class="text-xs px-2 py-1 rounded-md text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/50 transition">Example 1</button>
          <button type="button" onclick="setExample(2)" class="text-xs px-2 py-1 rounded-md text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/50 transition">?Unsure? words</button>
          <button type="button" onclick="setExample(3)" class="text-xs px-2 py-1 rounded-md text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/50 transition">Clean sentence</button>
        </div>

        <!-- Primary Action Button -->
        <div class="flex items-center gap-2.5 ml-auto">
          <span id="attemptBadge" class="hidden text-xs font-medium text-amber-700 bg-amber-100/80 px-2 py-0.5 rounded-md"></span>
          <button
            id="analyzeBtn"
            type="button"
            onclick="analyzeDraft()"
            class="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white text-xs font-medium transition shadow-xs inline-flex items-center gap-2"
          >
            <svg id="btnSpinner" class="hidden animate-spin w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9" stroke-opacity="0.25"></circle>
              <path d="M21 12a9 9 0 0 1-9 9"></path>
            </svg>
            <span id="btnText">Check Writing</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Subtle Loading Status -->
    <div id="statusIndicator" class="hidden text-center py-2 text-xs text-zinc-500 animate-pulse">
      <span id="statusText">Checking grammar...</span>
    </div>

    <!-- Clean / Notice Banner -->
    <div id="noticeBanner" class="hidden p-4 rounded-2xl text-sm border"></div>

    <!-- Feedback Cards Section (Hidden until analysis finds errors) -->
    <div id="resultsSection" class="hidden space-y-3">
      <div class="flex items-center justify-between px-1">
        <span class="text-xs font-medium text-zinc-500">Feedback</span>
        <span id="cardCount" class="text-xs text-zinc-400"></span>
      </div>
      <div id="cardsContainer" class="space-y-3"></div>
    </div>

  </main>

  <script>
    const TAXONOMY_DESCRIPTIONS = {
      // German (DE)
      "WO-V2": { name: "Verb-Second Word Order", cefr: "A1", hint: "The conjugated verb must be the second element in a main clause." },
      "WO-SEP": { name: "Separable Verb", cefr: "A1", hint: "The separable prefix moves to the end of the clause." },
      "WO-VF": { name: "Subordinate Clause Word Order", cefr: "A2", hint: "The conjugated verb goes to the very end after words like weil, dass, or wenn." },
      "WO-KLAM": { name: "Sentence Bracket", cefr: "A1", hint: "Participles and infinitives go to the end of the clause." },
      "WO-TMP": { name: "Time–Manner–Place Order", cefr: "B1", hint: "Order expressions as: Time before Manner before Place." },
      "KAS-AKK": { name: "Accusative Case", cefr: "A1", hint: "Direct objects take the accusative case." },
      "KAS-DAT": { name: "Dative Case", cefr: "A2", hint: "Indirect objects and dative verbs (like helfen or danken) take dative." },
      "KAS-GEN": { name: "Genitive Case", cefr: "B2", hint: "Used for possession and after prepositions like wegen, trotz, während." },
      "KAS-PREP": { name: "Preposition Case", cefr: "A2", hint: "mit/zu/aus/bei/nach/von require Dative; für/ohne/gegen require Accusative." },
      "KAS-2WEG": { name: "Two-Way Preposition", cefr: "A2", hint: "Use accusative for movement/direction and dative for static location." },
      "ADJ-END": { name: "Adjective Ending", cefr: "B1", hint: "Adjective ending must match the article, gender, and case." },
      "ART-GEN": { name: "Noun Gender & Article", cefr: "A1", hint: "The article must match the grammatical gender of the noun." },
      "N-PL": { name: "Plural Form", cefr: "A1", hint: "Check the plural ending of the noun." },
      "PRO-REL": { name: "Relative Pronoun", cefr: "B1", hint: "Matches the gender/number of the noun it refers to, and case from its role." },
      "PRO-KAS": { name: "Pronoun Case", cefr: "A2", hint: "Check personal pronoun case (e.g., mir vs. mich, ihm vs. ihn)." },
      "V-KONJ": { name: "Verb Conjugation", cefr: "A1", hint: "Verb ending or stem must match the subject." },
      "V-TEMP": { name: "Tense & Auxiliary", cefr: "A2", hint: "Check past auxiliary (haben vs. sein) or tense choice." },
      "V-PART": { name: "Past Participle", cefr: "A2", hint: "Check Partizip II spelling (ge- prefix and -t/-en ending)." },
      "V-K2": { name: "Konjunktiv II", cefr: "B1", hint: "Used for hypothetical or polite statements (würde, hätte, wäre, könnte)." },
      "V-REFL": { name: "Reflexive Pronoun", cefr: "A2", hint: "Missing or incorrect reflexive pronoun (mich/dich/sich)." },
      "PREP-W": { name: "Preposition Choice", cefr: "B1", hint: "Check which preposition pairs with this verb or expression." },
      "ORTH": { name: "Spelling & Capitalization", cefr: "A1", hint: "Check noun capitalization, umlauts, or ß/ss." },
      "WORTW": { name: "Word Choice", cefr: "B2", hint: "Grammatically valid, but another word sounds more natural." },
      "SONST": { name: "General Grammar", cefr: "B2", hint: "General sentence structure issue." },

      // French (FR)
      "FR-GEN": { name: "Noun Gender & Article", cefr: "A1", hint: "The article (le/la, un/une, ce/cette) must match the noun's gender." },
      "FR-ADJ": { name: "Adjective Agreement & Position", cefr: "A1", hint: "Adjectives agree in gender/number and usually follow the noun (except BAGS)." },
      "FR-ART": { name: "Partitive & Article Choice", cefr: "A2", hint: "Use du/de la/des for unspecified quantities, or 'de' after negation." },
      "FR-CONJ": { name: "Verb Conjugation", cefr: "A1", hint: "Verb ending must match the subject." },
      "FR-AUX": { name: "Auxiliary (être vs. avoir)", cefr: "A2", hint: "Motion verbs (aller, venir, partir...) and reflexive verbs use être in the past." },
      "FR-PP": { name: "Past Participle Agreement", cefr: "B1", hint: "Check participle ending (-é/-i/-u) and agreement with être or preceding object." },
      "FR-IMP": { name: "Passé Composé vs. Imparfait", cefr: "A2", hint: "Use passé composé for completed actions and imparfait for ongoing background." },
      "FR-SUBJ": { name: "Subjunctive Mood", cefr: "B1", hint: "Use the subjunctive after expressions of necessity, emotion, doubt, or bien que." },
      "FR-COND": { name: "Conditional & Si-Clauses", cefr: "B1", hint: "Use imparfait after 'si' and conditional in the result clause." },
      "FR-REFL": { name: "Reflexive Verb", cefr: "A2", hint: "Missing or incorrect reflexive pronoun (me/te/se/nous/vous)." },
      "FR-CLIT": { name: "Object Pronoun Order", cefr: "B1", hint: "Check pronoun choice (le/la/lui/leur/y/en) and place it before the verb." },
      "FR-NEG": { name: "Negation Placement", cefr: "A1", hint: "Place ne ... pas around the conjugated verb or auxiliary." },
      "FR-REL": { name: "Relative Pronoun (qui/que/dont/où)", cefr: "B1", hint: "Use qui for subject, que for direct object, dont for 'de', où for place/time." },
      "FR-PREP": { name: "Prepositions & Contractions", cefr: "A1", hint: "Contract à+le → au, à+les → aux, de+le → du, de+les → des." },
      "FR-INF": { name: "Verb + Infinitive Preposition", cefr: "B1", hint: "Check whether the verb takes à, de, or nothing before an infinitive." },
      "FR-ORTH": { name: "Accents & Elision", cefr: "A1", hint: "Check accents (é/è/ê/ç) and elision before a vowel (j'/l'/qu'/n')." },
      "FR-LEX": { name: "Word Choice", cefr: "B2", hint: "Grammatically valid, but another phrasing is more natural in French." },
      "FR-AUTRE": { name: "General Grammar", cefr: "B2", hint: "General French sentence structure issue." }
    };

    const EXAMPLES = {
      de: {
        1: "Ich gehe ?zu den? Bahnhof, weil ich habe keine Zeit.",
        2: "Ich helfe ?dem Mann?, weil ich heute Zeit habe.",
        3: "Gestern bin ich mit meiner Schwester ins Kino gegangen."
      },
      fr: {
        1: "Hier je ?ai allé? ?à le? cinéma avec mes amis.",
        2: "Je parle ?au professeur? parce que j'ai une question.",
        3: "Hier soir, je suis allé au théâtre avec ma sœur."
      }
    };

    let attemptNumber = 1;
    let isRevision = false;

    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function selectLanguage(lang) {
      document.getElementById('languageSelect').value = lang;
      document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.getAttribute('data-lang') === lang) {
          btn.className = "lang-btn px-2.5 py-1 rounded-md transition bg-white text-zinc-900 shadow-sm";
        } else {
          btn.className = "lang-btn px-2.5 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900";
        }
      });
      onLanguageChange();
    }

    function onLanguageChange() {
      document.getElementById('promptTargets').innerHTML = '';
      document.getElementById('promptBox').classList.add('hidden');
      setExample(1);
      if (document.getElementById('jwtInput').value.trim()) {
        fetchWeaknesses();
      }
    }

    function selectCefr(level) {
      document.getElementById('cefrSelect').value = level;
      document.querySelectorAll('.cefr-btn').forEach(btn => {
        if (btn.getAttribute('data-cefr') === level) {
          btn.className = "cefr-btn px-2 py-1 rounded-md transition bg-white text-zinc-900 shadow-sm";
        } else {
          btn.className = "cefr-btn px-2 py-1 rounded-md transition text-zinc-600 hover:text-zinc-900";
        }
      });
      onLevelChange();
    }

    function toggleLedgerDrawer() {
      document.getElementById('ledgerDrawer').classList.toggle('hidden');
    }

    function handleEditorKeydown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        analyzeDraft();
      }
    }

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
        badge.textContent = `Attempt #${attemptNumber}`;
        badge.classList.remove('hidden');
        btnText.textContent = "Check Revision";
        revBanner.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
        btnText.textContent = "Check Writing";
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
      const dot = document.getElementById('authStatusDot');
      if (token) {
        dot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500";
        fetchWeaknesses();
      } else {
        dot.className = "w-1.5 h-1.5 rounded-full bg-zinc-400";
        document.getElementById('ledgerBadges').innerHTML =
          '<span>Guest mode — add token to track recurring grammar gaps</span>';
      }
    }

    async function fetchWeaknesses() {
      const token = document.getElementById('jwtInput').value.trim();
      const lang = document.getElementById('languageSelect').value;
      const ledgerBadges = document.getElementById('ledgerBadges');
      const dot = document.getElementById('authStatusDot');
      if (!token) return;

      try {
        const res = await fetch(`/ai/weaknesses?language=${encodeURIComponent(lang)}`, { headers: getHeaders() });
        if (!res.ok) throw new Error('Invalid token');
        const codes = await res.json();
        dot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500";
        if (!codes.length) {
          ledgerBadges.innerHTML = `<span class="text-emerald-600">No recorded ${lang.toUpperCase()} errors yet</span>`;
          return;
        }
        ledgerBadges.innerHTML = codes.map(code => {
          const meta = TAXONOMY_DESCRIPTIONS[code] || { name: code };
          return `<span class="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-200 font-mono text-xs" title="${escapeHtml(meta.name)}">${escapeHtml(code)}</span>`;
        }).join('');
      } catch (err) {
        dot.className = "w-1.5 h-1.5 rounded-full bg-rose-500";
        ledgerBadges.innerHTML = `<span class="text-rose-600">${escapeHtml(err.message)}</span>`;
      }
    }

    async function generatePrompt() {
      const btn = document.getElementById('promptBtn');
      const spinner = document.getElementById('promptSpinner');
      const btnText = document.getElementById('promptBtnText');
      const promptBox = document.getElementById('promptBox');
      const promptText = document.getElementById('promptText');
      const promptTargets = document.getElementById('promptTargets');
      const level = document.getElementById('cefrSelect').value;
      const lang = document.getElementById('languageSelect').value;

      btn.disabled = true;
      spinner.classList.remove('hidden');
      btnText.textContent = "Generating...";

      try {
        const res = await fetch(`/ai/writing_prompt?target_level=${encodeURIComponent(level)}&language=${encodeURIComponent(lang)}`, {
          headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || data.detail || 'Failed to generate prompt');

        promptText.textContent = data.prompt;
        promptBox.classList.remove('hidden');
        promptTargets.innerHTML = (data.target_patterns || []).map(code => {
          const meta = TAXONOMY_DESCRIPTIONS[code] || { name: code };
          return `<span class="text-[11px] px-2 py-0.5 rounded-md bg-zinc-200/70 text-zinc-700 font-mono" title="${escapeHtml(meta.name)}">${escapeHtml(code)}</span>`;
        }).join('');

        resetDraftAttempt();
      } catch (err) {
        promptText.innerHTML = `<span class="text-rose-600">${escapeHtml(err.message)}</span>`;
        promptBox.classList.remove('hidden');
      } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
        btnText.textContent = "New Topic";
      }
    }

    function setExample(num) {
      const lang = document.getElementById('languageSelect').value;
      const set = EXAMPLES[lang] || EXAMPLES.de;
      document.getElementById('draftInput').value = set[num] || set[1];
      resetDraftAttempt();
    }

    function focusCardQuote(idx) {
      if (window._lastCards && window._lastCards[idx]) {
        focusQuoteInDraft(window._lastCards[idx].quote);
      }
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
      const lang = document.getElementById('languageSelect').value;
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
      btnText.textContent = "Checking...";
      spinner.classList.remove('hidden');
      statusIndicator.classList.remove('hidden');
      notice.classList.add('hidden');
      confirmedBanner.classList.add('hidden');
      resultsSection.classList.add('hidden');
      cardsContainer.innerHTML = '';

      try {
        const repairedPatterns = (isRevision && window._lastCards)
          ? window._lastCards
              .filter((_, idx) => !(window._revealedRung5 && window._revealedRung5.has(idx)))
              .map(c => c.pattern_code)
          : [];

        const response = await fetch('/ai/analyze-draft', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            sentence: text,
            target_level: level,
            language: lang,
            is_revision: isRevision,
            repaired_patterns: repairedPatterns
          })
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.message || data.detail || 'Analysis failed.');
        }

        if (document.getElementById('jwtInput').value.trim()) {
          fetchWeaknesses();
        }

        if (data.confirmed_hypotheses && data.confirmed_hypotheses.length > 0) {
          const pills = data.confirmed_hypotheses.map(
            h => `<code class="px-1.5 py-0.5 rounded bg-white border border-emerald-200 text-emerald-800 font-mono text-xs">&#10003; ${escapeHtml(h)}</code>`
          ).join(' ');
          confirmedBanner.innerHTML = `Confirmed correct: ${pills}`;
          confirmedBanner.classList.remove('hidden');
        }

        if (!data.cards || data.cards.length === 0) {
          notice.className = "p-4 rounded-2xl text-sm border bg-emerald-50 border-emerald-200/80 text-emerald-900 block";
          notice.innerHTML = isRevision
            ? `<strong>All fixed on Attempt #${attemptNumber}!</strong> Great job correcting your sentence.`
            : `<strong>Looks great!</strong> No grammar errors found.`;
          attemptNumber = 1;
          isRevision = false;
          window._lastCards = [];
          window._revealedRung5 = new Set();
          updateAttemptUI();
          return;
        }

        attemptNumber += 1;
        isRevision = true;
        updateAttemptUI();

        cardCount.textContent = `${data.cards.length} ${data.cards.length === 1 ? 'issue' : 'issues'} found`;
        resultsSection.classList.remove('hidden');

        window._lastCards = data.cards;
        window._revealedRung5 = new Set();

        data.cards.forEach((card, idx) => {
          const meta = TAXONOMY_DESCRIPTIONS[card.pattern_code] || { name: card.pattern_code, cefr: "?", hint: "" };
          const cardEl = document.createElement('div');
          cardEl.className = "bg-white rounded-2xl border border-zinc-200/90 p-5 shadow-xs space-y-3.5";

          cardEl.innerHTML = `
            <!-- L1 & L2 -->
            <div class="flex items-start justify-between gap-3">
              <div class="space-y-1">
                <span class="text-[11px] font-medium text-zinc-400">Sentence ${card.sentence_index + 1}</span>
                <div class="text-base font-medium text-zinc-900">
                  &ldquo;<span class="error-underline">${escapeHtml(card.quote)}</span>&rdquo;
                </div>
              </div>
              <button
                type="button"
                onclick="focusCardQuote(${idx})"
                class="text-xs font-medium text-zinc-500 hover:text-zinc-900 px-2.5 py-1 rounded-lg hover:bg-zinc-100 transition shrink-0"
              >
                Highlight in text
              </button>
            </div>

            <!-- L3: Category (Hidden initially) -->
            <div id="rung3-${idx}" class="hidden-rung pt-3 border-t border-zinc-100 space-y-2">
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded-md font-mono text-xs font-medium bg-zinc-100 text-zinc-800">${escapeHtml(card.pattern_code)}</span>
                  <span class="text-sm font-medium text-zinc-900">${escapeHtml(meta.name)}</span>
                </div>
                <button
                  type="button"
                  id="btnRung4-${idx}"
                  onclick="revealRung(${idx}, 4)"
                  class="text-xs font-medium text-zinc-600 hover:text-zinc-900 px-2.5 py-1 rounded-lg bg-zinc-100 hover:bg-zinc-200/70 transition"
                >
                  Show Hint &rarr;
                </button>
              </div>
              <p class="text-xs text-zinc-500">${escapeHtml(meta.hint)}</p>
            </div>

            <!-- L4: Rule Hint (Hidden initially) -->
            <div id="rung4-${idx}" class="hidden-rung p-3.5 rounded-xl bg-amber-50/70 border border-amber-200/60 space-y-2">
              <div class="flex items-center justify-between gap-2">
                <span class="text-xs font-medium text-amber-800">Grammar Hint</span>
                <button
                  type="button"
                  id="btnRung5-${idx}"
                  onclick="revealRung(${idx}, 5)"
                  class="text-xs font-medium text-amber-900 hover:underline"
                >
                  Show Answer &rarr;
                </button>
              </div>
              <p class="text-sm text-zinc-800 leading-relaxed">${escapeHtml(card.explanation)}</p>
            </div>

            <!-- L5: Correction (Hidden initially) -->
            <div id="rung5-${idx}" class="hidden-rung p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200/60 flex items-center justify-between gap-2">
              <span class="text-xs font-medium text-emerald-800">Correction</span>
              <span class="font-mono text-sm font-medium text-emerald-900">${escapeHtml(card.correction)}</span>
            </div>

            <!-- Initial Step Button -->
            <div id="initialBtnBox-${idx}" class="pt-1">
              <button
                type="button"
                onclick="revealRung(${idx}, 3)"
                class="text-xs font-medium text-zinc-600 hover:text-zinc-900 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200/70 transition"
              >
                Show Grammar Category &rarr;
              </button>
            </div>
          `;

          cardsContainer.appendChild(cardEl);
        });

      } catch (err) {
        notice.className = "p-4 rounded-2xl text-sm border bg-rose-50 border-rose-200 text-rose-800 block";
        notice.textContent = err.message;
      } finally {
        btn.disabled = false;
        updateAttemptUI();
        spinner.classList.add('hidden');
        statusIndicator.classList.add('hidden');
      }
    }

    function revealRung(cardIdx, rungNumber) {
      const rungEl = document.getElementById(`rung${rungNumber}-${cardIdx}`);
      if (rungEl) rungEl.classList.remove('hidden-rung');
      if (rungNumber === 3) {
        const initBox = document.getElementById(`initialBtnBox-${cardIdx}`);
        if (initBox) initBox.classList.add('hidden');
      } else if (rungNumber === 4) {
        const btn4 = document.getElementById(`btnRung4-${cardIdx}`);
        if (btn4) btn4.classList.add('hidden');
      } else if (rungNumber === 5) {
        if (!window._revealedRung5) window._revealedRung5 = new Set();
        window._revealedRung5.add(cardIdx);
        const btn5 = document.getElementById(`btnRung5-${cardIdx}`);
        if (btn5) btn5.classList.add('hidden');
      }
    }
  </script>
</body>
</html>
"""
