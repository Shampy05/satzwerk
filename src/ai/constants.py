from enum import StrEnum
from typing import TypedDict


class Language(StrEnum):
    DE = "de"
    FR = "fr"


LANGUAGE_NAMES: dict[Language, str] = {
    Language.DE: "German",
    Language.FR: "French",
}


class PatternCode(StrEnum):
    # =========================================================================
    # GERMAN (DE) — 24-Code SLA Taxonomy
    # =========================================================================
    # --- Word order (Processability-anchored) ---
    WO_V2 = "WO-V2"  # Verb-second in main clauses
    WO_SEP = "WO-SEP"  # Separable-verb split
    WO_VF = "WO-VF"  # Verb-final in subordinate clauses
    WO_KLAM = "WO-KLAM"  # Verbal bracket (Satzklammer)
    WO_TMP = "WO-TMP"  # Time–manner–place ordering

    # --- Case ---
    KAS_AKK = "KAS-AKK"  # Accusative for direct objects
    KAS_DAT = "KAS-DAT"  # Dative objects & dative verbs
    KAS_GEN = "KAS-GEN"  # Genitive
    KAS_PREP = "KAS-PREP"  # Case after fixed-case prepositions
    KAS_2WEG = "KAS-2WEG"  # Two-way prepositions

    # --- Agreement & morphology ---
    ADJ_END = "ADJ-END"  # Adjective endings
    ART_GEN = "ART-GEN"  # Article–gender agreement
    N_PL = "N-PL"  # Plural formation
    PRO_REL = "PRO-REL"  # Relative pronouns
    PRO_KAS = "PRO-KAS"  # Personal-pronoun case/reference

    # --- Verbs ---
    V_KONJ = "V-KONJ"  # Subject–verb agreement / conjugation
    V_TEMP = "V-TEMP"  # Tense choice & formation
    V_PART = "V-PART"  # Participle formation
    V_K2 = "V-K2"  # Konjunktiv II
    V_REFL = "V-REFL"  # Reflexive verbs

    # --- Other ---
    PREP_W = "PREP-W"  # Preposition choice
    ORTH = "ORTH"  # Spelling & capitalization
    WORTW = "WORTW"  # Word choice / idiomaticity
    SONST = "SONST"  # Other

    # =========================================================================
    # FRENCH (FR) — 18-Code SLA Taxonomy (Bartning & Schlyter / CEFR)
    # =========================================================================
    # --- Nominal & Agreement ---
    FR_GEN = "FR-GEN"  # Noun gender & determiner agreement (le/la, un/une, ce/cette)
    FR_ADJ = "FR-ADJ"  # Adjective agreement & placement (BAGS vs post-nominal)
    FR_ART = "FR-ART"  # Article & partitive selection (du/de la/des vs le/la vs de after negation)

    # --- Verbs, Tense, Aspect & Mood ---
    FR_CONJ = "FR-CONJ"  # Present-tense subject–verb conjugation & irregular stems
    FR_AUX = "FR-AUX"  # Auxiliary selection (être vs avoir in compound tenses)
    FR_PP = "FR-PP"  # Past participle formation & agreement (être / preceding direct object)
    FR_IMP = "FR-IMP"  # Passé composé vs Imparfait aspectual choice
    FR_SUBJ = "FR-SUBJ"  # Subjonctif mood after triggers (il faut que, bien que, vouloir que)
    FR_COND = "FR-COND"  # Conditionnel & si-clause sequence of tenses (concordance des temps)
    FR_REFL = "FR-REFL"  # Pronominal / reflexive verbs (se souvenir, s'appeler)

    # --- Syntax & Pronouns ---
    FR_CLIT = "FR-CLIT"  # Clitic object pronouns & pre-verbal ordering (le/la/lui/leur/y/en)
    FR_NEG = "FR-NEG"  # Two-part negation placement (ne ... pas/jamais/rien/plus)
    FR_REL = "FR-REL"  # Relative pronouns (qui / que / dont / où / lequel)
    FR_PREP = "FR-PREP"  # Prepositions & contractions (à/au/aux, de/du/des, en/dans/chez)
    FR_INF = "FR-INF"  # Verb + infinitive government (à vs de vs bare infinitive)

    # --- Orthography & Register ---
    FR_ORTH = "FR-ORTH"  # Diacritics (é/è/ê/ç), elision (l'/qu'/j'), & homophones (a/à, ou/où)
    FR_LEX = "FR-LEX"  # Word choice / idiomaticity (untreatable lexical register)
    FR_AUTRE = "FR-AUTRE"  # Other French syntax/morphology


class CEFRLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


CEFR_RANK: dict[CEFRLevel, int] = {
    CEFRLevel.A1: 1,
    CEFRLevel.A2: 2,
    CEFRLevel.B1: 3,
    CEFRLevel.B2: 4,
}


class PatternMetadata(TypedDict):
    language: Language
    name: str
    group: str
    stage: int | None
    cefr: CEFRLevel
    treatable: bool
    hint: str


TAXONOMY: dict[PatternCode, PatternMetadata] = {
    # -------------------------------------------------------------------------
    # GERMAN (DE)
    # -------------------------------------------------------------------------
    PatternCode.WO_V2: {
        "language": Language.DE,
        "name": "Verb-second in main clauses",
        "group": "Word order",
        "stage": 4,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'finite verb must be second constituent ("Gestern habe ich…")',
    },
    PatternCode.WO_SEP: {
        "language": Language.DE,
        "name": "Separable-verb split",
        "group": "Word order",
        "stage": 3,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'separable prefix moves to clause end ("Ich rufe dich morgen an")',
    },
    PatternCode.WO_VF: {
        "language": Language.DE,
        "name": "Verb-final in subordinate clauses",
        "group": "Word order",
        "stage": 5,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "finite verb at end after weil/dass/wenn/ob/relative clauses",
    },
    PatternCode.WO_KLAM: {
        "language": Language.DE,
        "name": "Verbal bracket (Satzklammer)",
        "group": "Word order",
        "stage": 3,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "participle/infinitive at clause end with haben/sein/werden/modals",
    },
    PatternCode.WO_TMP: {
        "language": Language.DE,
        "name": "Time–manner–place ordering",
        "group": "Word order",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "adverbial ordering: temporal before manner before place",
    },
    PatternCode.KAS_AKK: {
        "language": Language.DE,
        "name": "Accusative for direct objects",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'direct object takes accusative ("Ich sehe den Mann")',
    },
    PatternCode.KAS_DAT: {
        "language": Language.DE,
        "name": "Dative objects & dative verbs",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "indirect objects and verbs like helfen/danken/gefallen take dative",
    },
    PatternCode.KAS_GEN: {
        "language": Language.DE,
        "name": "Genitive",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": True,
        "hint": "possession and genitive prepositions (wegen, trotz, während)",
    },
    PatternCode.KAS_PREP: {
        "language": Language.DE,
        "name": "Case after fixed-case prepositions",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "mit/aus/bei/nach/von/zu → dative; für/ohne/gegen/durch/um → accusative",
    },
    PatternCode.KAS_2WEG: {
        "language": Language.DE,
        "name": "Two-way prepositions",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "an/auf/in/über/unter: accusative for motion, dative for location",
    },
    PatternCode.ADJ_END: {
        "language": Language.DE,
        "name": "Adjective endings",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "declension after der-words, ein-words, and bare nouns",
    },
    PatternCode.ART_GEN: {
        "language": Language.DE,
        "name": "Article–gender agreement",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "article/determiner must match noun's grammatical gender",
    },
    PatternCode.N_PL: {
        "language": Language.DE,
        "name": "Plural formation",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "wrong or missing plural form",
    },
    PatternCode.PRO_REL: {
        "language": Language.DE,
        "name": "Relative pronouns",
        "group": "Agreement",
        "stage": 5,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "relative pronoun agrees in gender/number with antecedent, case from clause",
    },
    PatternCode.PRO_KAS: {
        "language": Language.DE,
        "name": "Personal-pronoun case/reference",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "mir/mich, ihm/ihn confusion; unclear pronoun reference",
    },
    PatternCode.V_KONJ: {
        "language": Language.DE,
        "name": "Subject–verb agreement / conjugation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "person/number endings, irregular present-tense stems (du fährst)",
    },
    PatternCode.V_TEMP: {
        "language": Language.DE,
        "name": "Tense choice & formation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "Perfekt vs. Präteritum, haben vs. sein auxiliary, future with werden",
    },
    PatternCode.V_PART: {
        "language": Language.DE,
        "name": "Participle formation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "ge- placement, strong vs. weak participles (gegangen, gearbeitet)",
    },
    PatternCode.V_K2: {
        "language": Language.DE,
        "name": "Konjunktiv II",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "hypotheticals and polite forms: würde + inf, hätte/wäre/könnte",
    },
    PatternCode.V_REFL: {
        "language": Language.DE,
        "name": "Reflexive verbs",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "missing/wrong reflexive pronoun (sich freuen auf)",
    },
    PatternCode.PREP_W: {
        "language": Language.DE,
        "name": "Preposition choice",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "wrong preposition for verb/noun (warten auf, Angst vor)",
    },
    PatternCode.ORTH: {
        "language": Language.DE,
        "name": "Spelling & capitalization",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "noun capitalization, umlauts, ß/ss",
    },
    PatternCode.WORTW: {
        "language": Language.DE,
        "name": "Word choice / idiomaticity",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "grammatical but unidiomatic German phrasing",
    },
    PatternCode.SONST: {
        "language": Language.DE,
        "name": "Other",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "anything not covered by another code",
    },
    # -------------------------------------------------------------------------
    # FRENCH (FR)
    # -------------------------------------------------------------------------
    PatternCode.FR_GEN: {
        "language": Language.FR,
        "name": "Noun gender & determiner agreement",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "determiner (le/la, un/une, mon/ma, ce/cet/cette) must match noun gender",
    },
    PatternCode.FR_ADJ: {
        "language": Language.FR,
        "name": "Adjective agreement & placement",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "gender/number agreement on adjectives and pre- vs post-nominal placement (BAGS)",
    },
    PatternCode.FR_ART: {
        "language": Language.FR,
        "name": "Article & partitive selection",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "partitive (du/de la/des) vs definite (le/la/les) vs reduction to 'de' after negation or quantity",
    },
    PatternCode.FR_CONJ: {
        "language": Language.FR,
        "name": "Subject–verb conjugation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "person/number verb endings and irregular stems in present/future",
    },
    PatternCode.FR_AUX: {
        "language": Language.FR,
        "name": "Auxiliary selection (être vs avoir)",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "DR & MRS VANDERTRAMP motion/state verbs and all reflexive verbs require être in compound tenses",
    },
    PatternCode.FR_PP: {
        "language": Language.FR,
        "name": "Past participle formation & agreement",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "participle form (-é/-i/-u/irregular) and agreement with subject (être) or preceding COD (avoir)",
    },
    PatternCode.FR_IMP: {
        "language": Language.FR,
        "name": "Passé composé vs Imparfait aspect",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "completed foreground event (passé composé) vs ongoing background/habitual state (imparfait)",
    },
    PatternCode.FR_SUBJ: {
        "language": Language.FR,
        "name": "Subjonctif mood",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "subjunctive required after necessity, emotion, doubt, or conjunctions like bien que / pour que",
    },
    PatternCode.FR_COND: {
        "language": Language.FR,
        "name": "Conditionnel & si-clause tense sequence",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "si + imparfait → conditionnel présent; never put conditionnel or futur directly after 'si'",
    },
    PatternCode.FR_REFL: {
        "language": Language.FR,
        "name": "Pronominal & reflexive verbs",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "missing or mismatched reflexive pronoun (me/te/se/nous/vous) in pronominal verbs",
    },
    PatternCode.FR_CLIT: {
        "language": Language.FR,
        "name": "Clitic object pronouns & ordering",
        "group": "Syntax",
        "stage": 4,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "direct (le/la/les) vs indirect (lui/leur) vs adverbial (y/en) choice and pre-verbal placement",
    },
    PatternCode.FR_NEG: {
        "language": Language.FR,
        "name": "Negation structure & placement",
        "group": "Syntax",
        "stage": 3,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "two-part negation (ne ... pas/jamais/rien/plus) brackets the finite verb or auxiliary",
    },
    PatternCode.FR_REL: {
        "language": Language.FR,
        "name": "Relative pronouns (qui/que/dont/où)",
        "group": "Syntax",
        "stage": 5,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "qui (subject), que (direct object), dont (de-complement), où (place/time)",
    },
    PatternCode.FR_PREP: {
        "language": Language.FR,
        "name": "Prepositions & mandatory contractions",
        "group": "Syntax",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "mandatory contractions (à+le→au, à+les→aux, de+le→du, de+les→des) and place prepositions (à/en/dans/chez)",
    },
    PatternCode.FR_INF: {
        "language": Language.FR,
        "name": "Verb + infinitive government (à / de / Ø)",
        "group": "Syntax",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "correct linking preposition before an infinitive (décider de, réussir à, vouloir + Ø)",
    },
    PatternCode.FR_ORTH: {
        "language": Language.FR,
        "name": "Accents, elision & orthography",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "accents (é/è/ê/ç), mandatory elision before vowel/mute h (j'/l'/qu'/n'), a vs à",
    },
    PatternCode.FR_LEX: {
        "language": Language.FR,
        "name": "Word choice / idiomaticity",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "grammatical but unidiomatic French phrasing",
    },
    PatternCode.FR_AUTRE: {
        "language": Language.FR,
        "name": "Other French morphosyntax",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "French grammar issue not covered by another specific code",
    },
}


def taxonomy_prompt_block(language: Language = Language.DE) -> str:
    """Formats the taxonomy list for the given language for inclusion in prompts."""
    return "\n".join(
        f"- {code.value} ({meta['name']}): {meta['hint']}"
        for code, meta in TAXONOMY.items()
        if meta["language"] == language
    )
