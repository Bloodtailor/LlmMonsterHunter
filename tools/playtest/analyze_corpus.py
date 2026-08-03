# Corpus variety report - reads a generate_corpus.py JSONL and prints
# the numbers that answer "is it any good, or is it all the same
# monster?" No DB, no LLM, no network: the corpus is the input and
# counting is the method (see variety_metrics.py for why).
#
# Usage: ./venv/Scripts/python.exe tools/playtest/analyze_corpus.py \
#            playtest_results/corpus_<stamp>.jsonl [--report out.md]

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.playtest import variety_metrics as metrics


def load_corpus(path: Path) -> tuple:
    monsters, notices, failures = [], [], 0
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            kind = row.get('kind')
            if kind == 'monster':
                monsters.append(row)
            elif kind == 'notice':
                notices.append(row)
            else:
                failures += 1
    return monsters, notices, failures


def _distribution_lines(title: str, values: list, top: int = 12) -> list:
    lines = [f'### {title}']
    unique = len(set(values))
    lines.append(f'- unique values: {unique} across {len(values)} monsters')
    for value, count, fraction in metrics.value_distribution(values)[:top]:
        lines.append(f'  - {value}: {count} ({fraction:.0%})')
    return lines


def build_report(monsters: list, notices: list, failures: int, corpus_name: str) -> str:
    lines = [f'# Corpus variety report - {corpus_name}', '']
    lines.append(
        f'{len(monsters)} monsters, {len(notices)} notices, {failures} failed generations.'
    )
    if not monsters:
        lines.append('No monsters to analyze.')
        return '\n'.join(lines)

    full_texts = [metrics.monster_full_text(monster) for monster in monsters]
    token_lists = [metrics.tokenize(text) for text in full_texts]
    token_sets = [set(metrics.content_tokens(text)) for text in full_texts]

    # ===== distributions =====
    lines.append('\n## Distributions (what the enums produced)')
    lines.extend(_distribution_lines('Species', [m.get('species') for m in monsters]))
    lines.extend(_distribution_lines('Party role', [m.get('party_role') for m in monsters]))
    lines.extend(
        _distribution_lines('Kingdom', [(m.get('taxonomy') or {}).get('kingdom') for m in monsters])
    )
    element_values = []
    for monster in monsters:
        elements = (monster.get('ecology') or {}).get('elemental_affinities') or ['(none)']
        element_values.extend(elements)
    lines.extend(_distribution_lines('Elemental affinities (multi)', element_values))
    lines.extend(
        _distribution_lines(
            'Sapience', [(m.get('ecology') or {}).get('sapience') for m in monsters]
        )
    )

    # ===== names =====
    lines.append('\n## Names')
    names = [str(m.get('name') or '') for m in monsters]
    name_counts = metrics.value_distribution(names)
    duplicate_names = [(n, c) for n, c, _ in name_counts if c > 1]
    lines.append(f'- unique names: {len(set(names))}/{len(names)}')
    if duplicate_names:
        lines.append(
            '- exact name collisions: ' + ', '.join(f'{n} x{c}' for n, c in duplicate_names[:15])
        )
    name_tokens = [metrics.content_tokens(name) for name in names]
    lines.append('- most reused name words (document frequency):')
    for gram, count, fraction in metrics.document_frequency(name_tokens, 1, floor=0.02)[:12]:
        lines.append(f'  - "{gram}": {count} monsters ({fraction:.0%})')

    # ===== the silence rate =====
    lines.append('\n## The silence rate (the trope that started this)')
    rate, per_word = metrics.watchword_rate(full_texts)
    lines.append(
        f'- **{rate:.0%} of monsters** mention silence/quiet/hush/still-family words '
        f'somewhere in their text'
    )
    if per_word:
        top_words = ', '.join(f'{word} ({count})' for word, count in list(per_word.items())[:8])
        lines.append(f'- by word (documents containing it): {top_words}')
    for field, getter in (
        ('backstory', lambda m: m.get('backstory') or ''),
        ('description', lambda m: m.get('description') or ''),
        ('persona', lambda m: json.dumps(m.get('persona') or {})),
    ):
        field_rate, _ = metrics.watchword_rate([getter(m) for m in monsters])
        lines.append(f'  - in {field}: {field_rate:.0%}')

    # ===== recurring motifs =====
    lines.append('\n## Recurring motifs (document frequency across monsters)')
    for size, label, floor in ((1, 'words', 0.15), (2, 'bigrams', 0.05), (3, 'trigrams', 0.03)):
        rows = metrics.document_frequency(token_lists, size, floor=floor)[:15]
        if rows:
            lines.append(f'### Top {label}')
            for gram, count, fraction in rows:
                lines.append(f'  - "{gram}": {count} monsters ({fraction:.0%})')

    # ===== trope phrases =====
    lines.append('\n## Trope-phrase counts')
    for phrase, count, fraction in metrics.trope_phrase_rates(full_texts)[:20]:
        lines.append(f'  - "{phrase}": {count} monsters ({fraction:.0%})')

    # ===== within-combo sameness =====
    lines.append('\n## Within-enum-combination sameness')
    lines.append(
        '(mean pairwise Jaccard overlap of content words; ratio > 1 means monsters '
        'sharing that combination read more alike than the corpus at large)'
    )
    for key_fn, label in (
        (metrics.element_role_key, 'element + role'),
        (metrics.kingdom_role_key, 'kingdom + role'),
    ):
        global_mean, rows = metrics.combo_similarity(monsters, token_sets, key_fn)
        lines.append(f'### {label} (corpus-wide mean overlap: {global_mean:.3f})')
        for combo, size, combo_mean, ratio in rows[:10]:
            lines.append(f'  - {combo}: {size} monsters, overlap {combo_mean:.3f} ({ratio:.2f}x)')

    # ===== notices =====
    if notices:
        lines.append('\n## Expedition notices')
        titles = [str(n.get('title') or '') for n in notices]
        themes = [str(n.get('theme') or '') for n in notices]
        lines.append(f'- unique titles: {len(set(titles))}/{len(titles)}')
        lines.append(f'- unique themes: {len(set(themes))}/{len(themes)}')
        notice_texts = [
            ' '.join(
                (str(n.get('title') or ''), str(n.get('pitch') or ''), str(n.get('theme') or ''))
            )
            for n in notices
        ]
        notice_tokens = [metrics.tokenize(text) for text in notice_texts]
        lines.append('- most reused notice words:')
        for gram, count, fraction in metrics.document_frequency(notice_tokens, 1, floor=0.08)[:12]:
            lines.append(f'  - "{gram}": {count} notices ({fraction:.0%})')
        rate, per_word = metrics.watchword_rate(notice_texts)
        lines.append(f'- notice silence rate: {rate:.0%}')

    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Corpus variety report')
    parser.add_argument('corpus', help='JSONL from generate_corpus.py')
    parser.add_argument('--report', default=None, help='also write the report to this .md path')
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f'No such corpus: {corpus_path}')
        return 1

    monsters, notices, failures = load_corpus(corpus_path)
    report = build_report(monsters, notices, failures, corpus_path.name)
    print(report)

    if args.report:
        Path(args.report).write_text(report, encoding='utf-8')
        print(f'\n(written to {args.report})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
