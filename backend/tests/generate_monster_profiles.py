# Monster Quality Eval - generate N monsters and dump their full profiles
# For judging coherence by eye: does the backstory agree with the taxonomy?
# Does the voice match the persona? Do habitat and diet fit the biome?
#
# Requires the backend running (with the LLM loaded): python -m backend.run
# Usage: python -m backend.tests.generate_monster_profiles [count]

import sys
import time

import requests

BASE_URL = "http://localhost:5000/api"
POLL_SECONDS = 5
TIMEOUT_SECONDS = 600  # staged generation is ~5 LLM calls + abilities + art


def api_call(method, endpoint, data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def newest_monsters(count):
    result = api_call('GET', f'/monsters?limit={count}&sort=newest')
    if not result.get('success'):
        return []
    return result.get('monsters', [])


def wait_for_complete(count, known_ids):
    """Poll until `count` NEW monsters reach generation_stage complete with abilities"""
    started = time.time()
    while time.time() - started < TIMEOUT_SECONDS:
        fresh = [m for m in newest_monsters(count + len(known_ids)) if m['id'] not in known_ids]
        complete = [
            m
            for m in fresh
            if m.get('generation_stage') == 'complete' and m.get('ability_count', 0) >= 2
        ]
        stages = ', '.join(f"{m['name']}:{m.get('generation_stage')}" for m in fresh) or 'none yet'
        print(f'   waiting... ({stages})')
        if len(complete) >= count:
            return complete[:count]
        time.sleep(POLL_SECONDS)
    print(f'⚠️ Timed out after {TIMEOUT_SECONDS}s - showing whatever finished')
    return [m for m in newest_monsters(count + len(known_ids)) if m['id'] not in known_ids]


def show(label, value):
    if value in (None, '', [], {}):
        return
    if isinstance(value, list):
        value = ', '.join(str(v) for v in value)
    print(f'   {label}: {value}')


def print_profile(monster):
    taxonomy = monster.get('taxonomy') or {}
    ecology = monster.get('ecology') or {}
    persona = monster.get('persona') or {}
    habitat = ecology.get('habitat') or {}
    diet = ecology.get('diet') or {}
    social = ecology.get('social_structure') or {}
    bonds = persona.get('social_bonds') or {}
    stats = monster.get('stats') or {}

    print('\n' + '=' * 70)
    print(
        f"🐉 {monster['name']} — {monster.get('rarity')} {monster.get('party_role')}"
        f" ({monster.get('generation_stage')})"
    )
    print('=' * 70)

    lineage = ' > '.join(
        str(taxonomy.get(r))
        for r in ('domain', 'kingdom', 'family', 'genus', 'species')
        if taxonomy.get(r)
    )
    show('Lineage', lineage)
    show('Labels', f"{taxonomy.get('type_label')} / {taxonomy.get('race_label')}")
    show(
        'Stats',
        f"HP {stats.get('max_health')}, ATK {stats.get('attack')}, "
        f"DEF {stats.get('defense')}, SPD {stats.get('speed')}",
    )

    print('\n-- Ecology --')
    show(
        'Size / lifecycle / origin',
        f"{ecology.get('size_class')} / {ecology.get('lifecycle_stage')} / {ecology.get('creation_mechanism')}",
    )
    show('Habitat', f"{habitat.get('primary')} (biomes: {', '.join(habitat.get('biomes') or [])})")
    show(
        'Diet',
        f"{diet.get('feeding_style')} - {diet.get('notes')} (sustained by {', '.join(diet.get('sustenance') or [])})",
    )
    show('Social', f"{social.get('primary')} - {social.get('notes')}")
    show(
        'Mind',
        f"{ecology.get('sapience')}, communicates by {', '.join(ecology.get('communication') or [])}",
    )
    show('Elements', ecology.get('elemental_affinities'))
    show(
        'Class',
        '; '.join(
            ' > '.join(
                p for p in (c.get('domain'), c.get('discipline'), c.get('specialization')) if p
            )
            for c in (monster.get('class_taxonomy') or [])
        ),
    )

    print('\n-- Persona --')
    for label, key in (
        ('Wish', 'core_wish'),
        ('Motivations', 'motivations'),
        ('Goals', 'goals'),
        ('Beliefs', 'beliefs'),
        ('Moral character', 'moral_character'),
        ('Fears', 'fears'),
        ('Secret', 'secret'),
        ('Profession', 'profession'),
        ('Likes', 'likes'),
        ('Dislikes', 'dislikes'),
        ('Hobbies', 'hobbies'),
        ('Toward strangers', 'attitude_toward_strangers'),
        ('Responds well to', 'responds_well_to'),
        ('Responds poorly to', 'responds_poorly_to'),
        ('Recruitment lever', 'recruitment_lever'),
        ('Voice', 'speech_style'),
        ('Battle line', 'battle_line'),
    ):
        show(label, persona.get(key))
    show('Drawn to', bonds.get('drawn_to'))
    show('Clashes with', bonds.get('clashes_with'))

    print('\n-- Prose --')
    show('Description', monster.get('description'))
    show('Backstory', monster.get('backstory'))
    appearance = monster.get('appearance') or {}
    show('Visual', appearance.get('visual_description'))
    show('Colors', appearance.get('primary_colors'))
    show('Features', appearance.get('distinguishing_features'))

    print('\n-- Abilities --')
    for ability in monster.get('abilities') or []:
        print(f"   ⚡ {ability['name']} ({ability.get('ability_type')}): {ability['description']}")


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    print(f'🧪 MONSTER QUALITY EVAL — generating {count} monster(s)')
    print('=' * 70)

    health = api_call('GET', '/health')
    if health.get('status') != 'healthy':
        print('❌ Backend not reachable at localhost:5000 - start it first')
        return

    known_ids = {m['id'] for m in newest_monsters(50)}

    for i in range(count):
        result = api_call('GET', '/monsters/generate')
        if result.get('success'):
            print(f'   queued generation {i + 1}/{count} (workflow {result.get("workflow_id")})')
        else:
            print(f'   ❌ failed to queue generation: {result.get("error")}')

    monsters = wait_for_complete(count, known_ids)

    for monster in monsters:
        print_profile(monster)

    print('\n🎉 Done. Judge the profiles above for coherence:')
    print('   lineage <-> backstory, habitat <-> biomes, voice <-> battle line, wish <-> secret')


main()
