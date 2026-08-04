# LLM-as-annotator - the SECONDARY variety label for the Pt-M4 bake-off.
# Never the primary metric (locked decision, playtest-harness.md): a
# model judging "is this varied?" shares the exact attractors it would
# be judging. What a model CAN do more honestly is a narrow pairwise
# question - "do these two creatures share their central concept?" -
# which this tool asks over sampled pairs, yielding a same-concept rate
# to compare against the counting metrics on the same corpus.
#
# Costs 1 real LLM call per pair (default 60 pairs). Requires the
# seeded provider row, like every paid tool here.
#
# Usage: ./venv/Scripts/python.exe tools/playtest/annotate_corpus.py \
#            playtest_results/corpus_<stamp>.jsonl --pairs 60

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.analyze_corpus import load_corpus
from tools.playtest.rig import build_rig

PAIR_PROMPT = """You are comparing two monster designs from the same game.

MONSTER A:
{monster_a}

MONSTER B:
{monster_b}

Question: strip away the surface details (names, colors, species labels).
Do these two monsters share the same CENTRAL CONCEPT - the same core
idea a designer would pitch in one sentence?

Answer with ONLY a JSON object: {{"same_concept": "yes" or "no",
"concept_a": "<A's one-sentence concept>", "concept_b": "<B's one-sentence concept>"}}"""


def monster_card(monster: dict) -> str:
    persona = monster.get('persona') or {}
    return (
        f"Species: {monster.get('species')}\n"
        f"Role: {monster.get('party_role')}\n"
        f"Description: {monster.get('description')}\n"
        f"Backstory: {monster.get('backstory')}\n"
        f"Core wish: {persona.get('core_wish')}\n"
        f"Secret: {persona.get('secret')}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Pairwise same-concept annotation')
    parser.add_argument('corpus')
    parser.add_argument('--pairs', type=int, default=60)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    monsters, _notices, _failures = load_corpus(corpus_path)
    if len(monsters) < 2:
        print('Not enough monsters to compare.')
        return 1

    rng = random.Random(args.seed)
    out_path = (
        Path(args.out) if args.out else corpus_path.with_name(corpus_path.stem + '_pairs.jsonl')
    )

    app, _workflow_queue = build_rig()
    with app.app_context():
        from backend.ai.gateway import text_generation_request
        from backend.ai.llm.provider_settings import resolve_llm_settings
        from backend.models.core import create_tables

        create_tables()
        if resolve_llm_settings()['provider'] != 'deepseek':
            print("❌ Provider resolves to 'local' - run tools/playtest/seed_provider.py first.")
            return 1

        same = 0
        answered = 0
        with out_path.open('a', encoding='utf-8') as out_file:
            for pair_index in range(args.pairs):
                monster_a, monster_b = rng.sample(monsters, 2)
                prompt = PAIR_PROMPT.format(
                    monster_a=monster_card(monster_a), monster_b=monster_card(monster_b)
                )
                try:
                    result = text_generation_request(
                        prompt=prompt,
                        prompt_type='playtest',
                        prompt_name='variety_pair_annotation',
                        parser_config={
                            'type': 'json',
                            'parser_name': 'basic_parser',
                            'required_fields': ['same_concept'],
                        },
                        max_tokens=300,
                        temperature=0.0,
                    )
                    if not result.get('parsing_success'):
                        raise Exception(result.get('parsing_error') or 'no parse')
                    answer = result['parsed_data']
                    verdict = str(answer.get('same_concept', '')).strip().lower()
                    answered += 1
                    same += 1 if verdict == 'yes' else 0
                    out_file.write(
                        json.dumps(
                            {
                                'a': monster_a.get('name'),
                                'b': monster_b.get('name'),
                                'same_concept': verdict,
                                'concept_a': answer.get('concept_a'),
                                'concept_b': answer.get('concept_b'),
                            }
                        )
                        + '\n'
                    )
                    out_file.flush()
                except Exception as pair_error:
                    print(f'  ⚠️ pair {pair_index + 1} failed: {pair_error}')
                if (pair_index + 1) % 10 == 0:
                    print(f'  {pair_index + 1}/{args.pairs} pairs')

        if answered:
            print('\n' + '=' * 50)
            print(
                f'same-concept rate: {same}/{answered} ({same / answered:.0%}) '
                f'over randomly sampled pairs'
            )
            print(f'annotations: {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
