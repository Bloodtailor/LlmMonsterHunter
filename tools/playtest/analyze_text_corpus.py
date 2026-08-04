# Variety report for the OTHER generated text: abilities, items, and
# chronicles. Same method as the monster report (counting, never a model
# judging its own attractors), aimed at three surfaces that have never
# been measured:
#
#   ABILITIES  - read from a monster corpus (generate_corpus.py), since
#                every monster already carries its abilities. Counts the
#                PSEUDO-MECHANICS leak the first corpus revealed: text
#                promising "next three turns" that the referee never
#                honors (the game's rule is power lives in words).
#   ITEMS      - from a text corpus (generate_text_corpus.py --items)
#   CHRONICLES - from a text corpus (--chronicles): the run's story beat,
#                the most player-facing prose the game writes
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/analyze_text_corpus.py \
#       playtest_results/text_corpus_<stamp>.jsonl \
#       --abilities-from playtest_results/corpus_<stamp>.jsonl \
#       --report playtest_results/text_variety_report.md

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.playtest import variety_metrics as metrics


def load_rows(path: Path) -> list:
    rows = []
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def abilities_from_monster_corpus(path: Path) -> list:
    """Every ability the monster corpus already carries - free to analyze"""
    abilities = []
    for row in load_rows(path):
        if row.get('kind') != 'monster':
            continue
        for ability in row.get('abilities') or []:
            if isinstance(ability, dict) and ability.get('name'):
                abilities.append(ability)
    return abilities


def text_block(section_title: str, texts: list, names: list, unit: str) -> list:
    """The shared counting battery for any body of generated text"""
    lines = [f'\n## {section_title} ({len(texts)} {unit})']
    if not texts:
        lines.append('- none in this corpus')
        return lines

    unique_names = len(set(names))
    lines.append(f'- unique names: {unique_names}/{len(names)}')
    duplicates = [(n, c) for n, c, _ in metrics.value_distribution(names) if c > 1]
    if duplicates:
        lines.append('- name collisions: ' + ', '.join(f'"{n}" x{c}' for n, c in duplicates[:10]))

    token_lists = [metrics.tokenize(text) for text in texts]
    lines.append(f'- most reused words (document frequency across {unit}):')
    for gram, count, fraction in metrics.document_frequency(token_lists, 1, floor=0.10)[:12]:
        lines.append(f'  - "{gram}": {count} ({fraction:.0%})')
    bigrams = metrics.document_frequency(token_lists, 2, floor=0.05)[:8]
    if bigrams:
        lines.append('- most reused phrases:')
        for gram, count, fraction in bigrams:
            lines.append(f'  - "{gram}": {count} ({fraction:.0%})')

    rate, per_word = metrics.watchword_rate(texts)
    dense = metrics.watchword_density_rate(texts)
    lines.append(f'- silence-family mentions: {rate:.0%} (silence-DENSE, 3+ distinct: {dense:.0%})')

    tropes = metrics.trope_phrase_rates(texts)[:8]
    if tropes:
        lines.append('- trope phrases:')
        for phrase, count, fraction in tropes:
            lines.append(f'  - "{phrase}": {count} ({fraction:.0%})')

    token_sets = [set(metrics.content_tokens(text)) for text in texts]
    import random as random_module

    overlap = metrics.mean_pairwise_jaccard(token_sets, random_module.Random(0))
    lines.append(f'- mean pairwise overlap (sameness): {overlap:.3f}')
    return lines


def build_report(abilities: list, items: list, chronicles: list, source: str) -> str:
    lines = [f'# Text variety report - {source}', '']

    # ===== ABILITIES: the counting battery PLUS the mechanics leak =====
    ability_texts = [f"{a.get('name', '')} {a.get('description', '')}".strip() for a in abilities]
    lines.extend(
        text_block('Abilities', ability_texts, [a.get('name', '') for a in abilities], 'abilities')
    )
    if ability_texts:
        descriptions = [a.get('description', '') for a in abilities]
        leak_rate, rows = metrics.mechanics_leak_rates(descriptions)
        lines.append('')
        lines.append(
            f'### Pseudo-mechanics leak: **{leak_rate:.0%} of ability descriptions** promise '
            'an effect the engine does not implement'
        )
        lines.append('(the game\'s rule is that power lives in WORDS - code owns every number)')
        for label, pattern, count, fraction in rows:
            lines.append(f'  - {label} (`{pattern}`): {count} abilities ({fraction:.0%})')

    # ===== ITEMS =====
    item_texts = [f"{i.get('name', '')} {i.get('description', '')}".strip() for i in items]
    lines.extend(text_block('Items', item_texts, [i.get('name', '') for i in items], 'items'))
    if item_texts:
        leak_rate, rows = metrics.mechanics_leak_rates([i.get('description', '') for i in items])
        lines.append(f'- pseudo-mechanics leak: {leak_rate:.0%} of item descriptions')

    # ===== CHRONICLES =====
    chronicle_texts = [c.get('text', '') for c in chronicles if c.get('text')]
    lines.extend(
        text_block(
            'Chronicles',
            chronicle_texts,
            [t[:40] for t in chronicle_texts],
            'chronicles',
        )
    )
    if chronicle_texts:
        lengths = sorted(len(t.split()) for t in chronicle_texts)
        median = lengths[len(lengths) // 2]
        lines.append(f'- length in words: min {lengths[0]}, median {median}, max {lengths[-1]}')
        openers = [' '.join(t.split()[:4]).lower() for t in chronicle_texts]
        repeated_openers = [(o, c) for o, c, _ in metrics.value_distribution(openers) if c > 1]
        lines.append(f'- distinct four-word openings: {len(set(openers))}/{len(openers)}')
        if repeated_openers:
            lines.append(
                '- repeated openings: ' + ', '.join(f'"{o}" x{c}' for o, c in repeated_openers[:6])
            )

    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'corpus', nargs='?', default=None, help='text corpus JSONL (items/chronicles)'
    )
    parser.add_argument('--abilities-from', default=None, help='monster corpus JSONL')
    parser.add_argument('--report', default=None)
    args = parser.parse_args()

    items, chronicles, sources = [], [], []
    if args.corpus:
        corpus_path = Path(args.corpus)
        if not corpus_path.exists():
            print(f'No such corpus: {corpus_path}')
            return 1
        sources.append(corpus_path.name)
        for row in load_rows(corpus_path):
            if row.get('kind') == 'item':
                items.append(row)
            elif row.get('kind') == 'chronicle':
                chronicles.append(row)

    abilities = []
    if args.abilities_from:
        ability_path = Path(args.abilities_from)
        if not ability_path.exists():
            print(f'No such monster corpus: {ability_path}')
            return 1
        sources.append(ability_path.name)
        abilities = abilities_from_monster_corpus(ability_path)

    if not (abilities or items or chronicles):
        print('Nothing to analyze - pass a text corpus and/or --abilities-from')
        return 1

    report = build_report(abilities, items, chronicles, ' + '.join(sources))
    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding='utf-8')
        print(f'(written to {args.report})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
