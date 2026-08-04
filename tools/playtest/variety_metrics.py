# Variety metrics - the counting machinery behind the corpus report.
# Pure Python on purpose: Problem B ("everything sounds the same") is a
# property of the corpus, measured by counting across it - never by
# asking a model "is this varied?", because models share the exact
# attractors they would be judging (locked decision, playtest-harness.md).
#
# Two genuinely different measurement families live here:
#   - occurrence counting: document frequency of tokens / n-grams /
#     watchwords / trope phrases across monsters
#   - similarity clustering: pairwise Jaccard overlap of content-token
#     sets, globally and within enum combinations ("are all
#     fire-beast-strikers the same monster?") - embedding-free
# Pt-M4 compares what each catches and misses.

import itertools
import random
import re
from collections import Counter
from typing import Any

WORD_PATTERN = re.compile(r"[a-z][a-z'-]+")

# Small standard stopword list - deliberately no fantasy words, so
# genre-generic vocabulary ('ancient', 'shadow') stays measurable
STOPWORDS = frozenset(
    [
        'a',
        'an',
        'and',
        'are',
        'as',
        'at',
        'be',
        'but',
        'by',
        'for',
        'from',
        'has',
        'have',
        'if',
        'in',
        'into',
        'is',
        'it',
        'its',
        'of',
        'on',
        'or',
        'that',
        'the',
        'their',
        'them',
        'then',
        'there',
        'these',
        'they',
        'this',
        'to',
        'was',
        'were',
        'will',
        'with',
        'your',
        'you',
        'not',
        'no',
        'nor',
        'so',
        'than',
        'too',
        'very',
        'can',
        'just',
        'do',
        'does',
        'did',
        'done',
        'being',
        'been',
        'am',
        'what',
        'when',
        'where',
        'who',
        'whom',
        'which',
        'while',
        'about',
        'after',
        'before',
        'during',
        'under',
        'over',
        'between',
        'through',
        'out',
        'up',
        'down',
        'off',
        'above',
        'below',
        'again',
        'once',
        'here',
        'all',
        'any',
        'both',
        'each',
        'few',
        'more',
        'most',
        'other',
        'some',
        'such',
        'only',
        'own',
        'same',
        's',
        't',
        'don',
        'should',
        'now',
        'he',
        'she',
        'his',
        'her',
        'him',
        'hers',
        'we',
        'our',
        'ours',
        'us',
        'i',
        'me',
        'my',
        'mine',
    ]
)

# The watchwords behind the "silence rate" - the observed trope this
# harness exists to measure (monsters weirdly obsessed with silence)
SILENCE_WORDS = (
    'silence',
    'silent',
    'silently',
    'quiet',
    'quietly',
    'hush',
    'hushed',
    'still',
    'stillness',
    'soundless',
    'mute',
    'muted',
    'wordless',
)

# Known centroid phrases (01-why-generic-happens.md's diagnosis: "a wolf
# with crystals", "guardian of the ancient something", "gentle despite")
TROPE_PHRASES = (
    'despite its',
    'despite their',
    'guardian of',
    'protector of',
    'keeper of',
    'watches over',
    'long forgotten',
    'long-forgotten',
    'ancient',
    'crystalline',
    'crystal',
    'ethereal',
    'shimmering',
    'iridescent',
    'echoes of',
    'echoing',
    'gentle giant',
    'misunderstood',
    'secretly',
    'lonely',
    'loneliness',
    'forgotten memories',
    'whispers',
    'whispering',
    'luminous',
    'glowing',
    'bioluminescent',
    'obsidian',
    'opalescent',
    'time itself',
    'balance of',
    'harmony',
)


# PSEUDO-MECHANICS: ability text promising effects the engine does not
# implement ("for the next three turns", "20% more damage"). The referee
# never honors them, so every hit is a promise the game breaks - found
# while reading the first corpus, now counted on every one.
MECHANICS_PATTERNS = (
    (r'\bnext\s+(?:\w+\s+)?turns?\b', 'turn-duration promise'),
    (r'\b\d+\s*%', 'percentage'),
    (r'\b(?:one|two|three|four|five|\d+)\s+turns?\b', 'turn count'),
    (r'\b(?:doubl|tripl)(?:e|es|ed|ing)\b', 'multiplier'),
    (r'\bamount of (?:health|damage|stamina|mana)\b', 'quantified pool'),
    (r'\b(?:fire|water|earth|air|nature|shadow|light|ice)\s+damage\b', 'damage type'),
    (r'\b(?:restores?|heals?|deals?)\s+\d+', 'numeric effect'),
    (r'\b(?:hp|mp|hit points|mana points)\b', 'stat abbreviation'),
    (r'\bcooldown\b', 'cooldown'),
    (r'\bstacks?\b', 'stacking'),
)


def tokenize(text: str) -> list:
    return WORD_PATTERN.findall((text or '').lower())


def mechanics_leak_rates(texts: list) -> tuple:
    """(overall fraction of texts promising a mechanic, per-pattern rows).
    The game's own rule is that power lives in WORDS - code owns numbers -
    so any numeric or duration promise in generated text is a leak."""
    total = len(texts)
    if not total:
        return 0.0, []
    lowered = [(text or '').lower() for text in texts]
    rows = []
    leaking = set()
    for pattern, label in MECHANICS_PATTERNS:
        compiled = re.compile(pattern)
        hits = [index for index, text in enumerate(lowered) if compiled.search(text)]
        if hits:
            rows.append((label, pattern, len(hits), len(hits) / total))
            leaking.update(hits)
    return len(leaking) / total, sorted(rows, key=lambda row: -row[2])


# 'still' and 'mute' carry innocent senses ("still empty", "the point is
# moot") that have nothing to do with the trope. They stay in
# SILENCE_WORDS so the founding baseline's numbers remain comparable,
# but a STRICT rate that drops them separates a real silence obsession
# from ordinary English: on a chronicle corpus the two differ by 19
# points (88% vs 69%), and the strict number is the honest one.
AMBIGUOUS_SILENCE_WORDS = ('still', 'mute')
SILENCE_WORDS_STRICT = tuple(w for w in SILENCE_WORDS if w not in AMBIGUOUS_SILENCE_WORDS)


def watchword_density_rate(texts: list, words=SILENCE_WORDS, minimum: int = 3) -> float:
    """Fraction of documents using at least `minimum` DISTINCT watchwords.
    The binary silence rate counts a monster that merely 'dislikes noisy
    places' the same as one built entirely around silence; this separates
    a glancing mention from an obsession (REPORT.md's requested
    refinement after the register-rule fix)."""
    total = len(texts)
    if not total:
        return 0.0
    pattern = re.compile(r'\b(' + '|'.join(words) + r')\b', re.IGNORECASE)
    dense = 0
    for text in texts:
        found = {word.lower() for word in pattern.findall(text or '')}
        if len(found) >= minimum:
            dense += 1
    return dense / total


def content_tokens(text: str) -> list:
    return [token for token in tokenize(text) if token not in STOPWORDS]


def monster_full_text(monster: dict[str, Any]) -> str:
    """Every player-visible or persona word the generator chose"""
    persona = monster.get('persona') or {}
    appearance = monster.get('appearance') or {}
    pieces = [
        monster.get('name', ''),
        monster.get('species', ''),
        monster.get('description', ''),
        monster.get('backstory', ''),
        appearance.get('visual_description', ''),
        ' '.join(appearance.get('distinguishing_features') or []),
        ' '.join(monster.get('personality_traits') or []),
    ]
    for value in persona.values():
        if isinstance(value, str):
            pieces.append(value)
        elif isinstance(value, list):
            pieces.extend(str(item) for item in value)
        elif isinstance(value, dict):
            pieces.extend(str(item) for item in value.values())
    for ability in monster.get('abilities') or []:
        if isinstance(ability, dict):
            pieces.append(ability.get('name', ''))
            pieces.append(ability.get('description', ''))
    return ' '.join(piece for piece in pieces if piece)


def document_frequency(documents: list, ngram_size: int = 1, floor: float = 0.05) -> list:
    """(ngram, doc_count, fraction) sorted by how many documents carry it.
    N-grams run over the raw token sequence and are dropped only when
    every word is a stopword, so 'ancient guardian' survives while
    'of the' does not."""
    total = len(documents)
    if not total:
        return []
    counts = Counter()
    for tokens in documents:
        grams = set()
        for gram in zip(*(tokens[i:] for i in range(ngram_size))):
            if all(word in STOPWORDS for word in gram):
                continue
            if gram[0] in STOPWORDS or gram[-1] in STOPWORDS:
                continue
            grams.add(' '.join(gram))
        counts.update(grams)
    threshold = max(2, int(total * floor))
    return sorted(
        ((gram, count, count / total) for gram, count in counts.items() if count >= threshold),
        key=lambda row: -row[1],
    )


def watchword_rate(texts: list, words=SILENCE_WORDS) -> tuple:
    """(fraction of documents containing any watchword, per-word counts)"""
    total = len(texts)
    if not total:
        return 0.0, {}
    pattern = re.compile(r'\b(' + '|'.join(words) + r')\b', re.IGNORECASE)
    per_word = Counter()
    hits = 0
    for text in texts:
        found = pattern.findall(text or '')
        if found:
            hits += 1
            # Lowercase BEFORE deduping - 'Stillness' and 'stillness' in
            # one document must count that document once, not twice
            per_word.update({word.lower() for word in found})
    return hits / total, dict(per_word.most_common())


def trope_phrase_rates(texts: list, phrases=TROPE_PHRASES) -> list:
    """(phrase, doc_count, fraction) for every phrase that appears at all"""
    total = len(texts)
    if not total:
        return []
    lowered = [(text or '').lower() for text in texts]
    rows = []
    for phrase in phrases:
        count = sum(1 for text in lowered if phrase in text)
        if count:
            rows.append((phrase, count, count / total))
    return sorted(rows, key=lambda row: -row[1])


def jaccard(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def mean_pairwise_jaccard(token_sets: list, rng: random.Random, max_pairs: int = 500) -> float:
    """Mean Jaccard over all pairs (sampled beyond max_pairs)"""
    pairs = list(itertools.combinations(range(len(token_sets)), 2))
    if not pairs:
        return 0.0
    if len(pairs) > max_pairs:
        pairs = rng.sample(pairs, max_pairs)
    return sum(jaccard(token_sets[i], token_sets[j]) for i, j in pairs) / len(pairs)


def combo_similarity(
    monsters: list, token_sets: list, combo_key, min_size: int = 3, seed: int = 0
) -> tuple:
    """How much more alike monsters in the same enum combination are
    than the corpus at large. Returns (global_mean, rows) with rows =
    (combo_name, size, combo_mean, ratio_to_global) sorted worst-first."""
    rng = random.Random(seed)
    global_mean = mean_pairwise_jaccard(token_sets, rng)

    groups: dict[str, list] = {}
    for index, monster in enumerate(monsters):
        key = combo_key(monster)
        if key:
            groups.setdefault(key, []).append(index)

    rows = []
    for key, indexes in groups.items():
        if len(indexes) < min_size:
            continue
        combo_mean = mean_pairwise_jaccard([token_sets[i] for i in indexes], rng)
        ratio = combo_mean / global_mean if global_mean else 0.0
        rows.append((key, len(indexes), combo_mean, ratio))
    return global_mean, sorted(rows, key=lambda row: -row[3])


def element_role_key(monster: dict) -> str:
    ecology = monster.get('ecology') or {}
    elements = ecology.get('elemental_affinities') or []
    role = monster.get('party_role') or 'unknown'
    if not elements:
        return f'no-element+{role}'
    return f'{elements[0]}+{role}'


def kingdom_role_key(monster: dict) -> str:
    taxonomy = monster.get('taxonomy') or {}
    kingdom = taxonomy.get('kingdom') or 'unknown'
    role = monster.get('party_role') or 'unknown'
    return f'{kingdom}+{role}'


def value_distribution(values: list) -> list:
    """(value, count, fraction) sorted by count"""
    total = len(values) or 1
    return [(value, count, count / total) for value, count in Counter(values).most_common()]
