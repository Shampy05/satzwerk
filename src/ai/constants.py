from enum import StrEnum
from typing import TypedDict


class PatternCode(StrEnum):
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


class CEFRLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class PatternMetadata(TypedDict):
    name: str
    group: str
    stage: int | None
    cefr: CEFRLevel
    treatable: bool
    hint: str


TAXONOMY: dict[PatternCode, PatternMetadata] = {
    PatternCode.WO_V2: {
        "name": "Verb-second in main clauses",
        "group": "Word order",
        "stage": 4,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'finite verb must be second constituent ("Gestern habe ich…")',
    },
    PatternCode.WO_SEP: {
        "name": "Separable-verb split",
        "group": "Word order",
        "stage": 3,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'separable prefix moves to clause end ("Ich rufe dich morgen an")',
    },
    PatternCode.WO_VF: {
        "name": "Verb-final in subordinate clauses",
        "group": "Word order",
        "stage": 5,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "finite verb at end after weil/dass/wenn/ob/relative clauses",
    },
    PatternCode.WO_KLAM: {
        "name": "Verbal bracket (Satzklammer)",
        "group": "Word order",
        "stage": 3,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "participle/infinitive at clause end with haben/sein/werden/modals",
    },
    PatternCode.WO_TMP: {
        "name": "Time–manner–place ordering",
        "group": "Word order",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "adverbial ordering: temporal before manner before place",
    },
    PatternCode.KAS_AKK: {
        "name": "Accusative for direct objects",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": 'direct object takes accusative ("Ich sehe den Mann")',
    },
    PatternCode.KAS_DAT: {
        "name": "Dative objects & dative verbs",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "indirect objects and verbs like helfen/danken/gefallen take dative",
    },
    PatternCode.KAS_GEN: {
        "name": "Genitive",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": True,
        "hint": "possession and genitive prepositions (wegen, trotz, während)",
    },
    PatternCode.KAS_PREP: {
        "name": "Case after fixed-case prepositions",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "mit/aus/bei/nach/von/zu → dative; für/ohne/gegen/durch/um → accusative",
    },
    PatternCode.KAS_2WEG: {
        "name": "Two-way prepositions",
        "group": "Case",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "an/auf/in/über/unter: accusative for motion, dative for location",
    },
    PatternCode.ADJ_END: {
        "name": "Adjective endings",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "declension after der-words, ein-words, and bare nouns",
    },
    PatternCode.ART_GEN: {
        "name": "Article–gender agreement",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "article/determiner must match noun's grammatical gender",
    },
    PatternCode.N_PL: {
        "name": "Plural formation",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "wrong or missing plural form",
    },
    PatternCode.PRO_REL: {
        "name": "Relative pronouns",
        "group": "Agreement",
        "stage": 5,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "relative pronoun agrees in gender/number with antecedent, case from clause",
    },
    PatternCode.PRO_KAS: {
        "name": "Personal-pronoun case/reference",
        "group": "Agreement",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "mir/mich, ihm/ihn confusion; unclear pronoun reference",
    },
    PatternCode.V_KONJ: {
        "name": "Subject–verb agreement / conjugation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "person/number endings, irregular present-tense stems (du fährst)",
    },
    PatternCode.V_TEMP: {
        "name": "Tense choice & formation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "Perfekt vs. Präteritum, haben vs. sein auxiliary, future with werden",
    },
    PatternCode.V_PART: {
        "name": "Participle formation",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "ge- placement, strong vs. weak participles (gegangen, gearbeitet)",
    },
    PatternCode.V_K2: {
        "name": "Konjunktiv II",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "hypotheticals and polite forms: würde + inf, hätte/wäre/könnte",
    },
    PatternCode.V_REFL: {
        "name": "Reflexive verbs",
        "group": "Verbs",
        "stage": None,
        "cefr": CEFRLevel.A2,
        "treatable": True,
        "hint": "missing/wrong reflexive pronoun (sich freuen auf)",
    },
    PatternCode.PREP_W: {
        "name": "Preposition choice",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B1,
        "treatable": True,
        "hint": "wrong preposition for verb/noun (warten auf, Angst vor)",
    },
    PatternCode.ORTH: {
        "name": "Spelling & capitalization",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.A1,
        "treatable": True,
        "hint": "noun capitalization, umlauts, ß/ss",
    },
    PatternCode.WORTW: {
        "name": "Word choice / idiomaticity",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "grammatical but unidiomatic German phrasing",
    },
    PatternCode.SONST: {
        "name": "Other",
        "group": "Other",
        "stage": None,
        "cefr": CEFRLevel.B2,
        "treatable": False,
        "hint": "anything not covered by another code",
    },
}


def taxonomy_prompt_block() -> str:
    """Formats the taxonomy list for inclusion in the system prompt."""
    return "\n".join(
        f"- {code.value} ({meta['name']}): {meta['hint']}"
        for code, meta in TAXONOMY.items()
    )
