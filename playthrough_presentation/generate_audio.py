# Turn script.md into the narration track the player uses.
#
# Each "## NN — Title" section becomes audio/NN.mp3 via ElevenLabs.
# The API key is read from the ELEVENLABS_API_KEY environment variable
# and never stored in the repo:
#
#   ELEVENLABS_API_KEY=... ./venv/Scripts/python.exe playtest_presentation/generate_audio.py
#   ... --only 10,11        # regenerate just those sections
#   ... --dry-run           # show what would be spoken, spend nothing
#
# Re-running is cheap to control: unchanged sections are skipped unless
# --force, because ElevenLabs bills per character.

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT_PATH = HERE / 'script.md'
AUDIO_DIR = HERE / 'audio'
STAMP_PATH = AUDIO_DIR / '.hashes.json'

# George - warm, captivating storyteller: this is a story about an
# expedition, not a product demo
VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb'
MODEL_ID = 'eleven_multilingual_v2'
SECTION_PATTERN = re.compile(r'^##\s+(\d+)\s+—\s+(.*)$')


def parse_sections(text: str) -> list:
    """[(number, title, spoken_text)] - markdown emphasis stripped, since
    the narrator should not pronounce asterisks"""
    sections, current = [], None
    for line in text.splitlines():
        match = SECTION_PATTERN.match(line.strip())
        if match:
            if current:
                sections.append(current)
            current = {'number': match.group(1), 'title': match.group(2), 'lines': []}
        elif current is not None:
            current['lines'].append(line)
    if current:
        sections.append(current)

    for section in sections:
        body = '\n'.join(section['lines'])
        body = re.sub(r'\*\*(.+?)\*\*', r'\1', body)
        body = re.sub(r'[*_`]', '', body)
        body = re.sub(r'^---$', '', body, flags=re.MULTILINE)
        section['text'] = re.sub(r'\n{2,}', '\n\n', body).strip()
    return [s for s in sections if s['text']]


def speak(text: str, key: str) -> bytes:
    request = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}',
        data=json.dumps(
            {
                'text': text,
                'model_id': MODEL_ID,
                # Stability high enough to keep a documentary register
                # across fifteen separate files
                'voice_settings': {
                    'stability': 0.45,
                    'similarity_boost': 0.75,
                    'style': 0.15,
                    'use_speaker_boost': True,
                },
            }
        ).encode('utf-8'),
        headers={'xi-api-key': key, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', default=None, help='comma-separated section numbers')
    parser.add_argument('--force', action='store_true', help='regenerate even if unchanged')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    sections = parse_sections(SCRIPT_PATH.read_text(encoding='utf-8'))
    wanted = set((args.only or '').split(',')) if args.only else None
    if wanted:
        sections = [s for s in sections if s['number'] in wanted]

    total_chars = sum(len(s['text']) for s in sections)
    print(f'{len(sections)} sections, {total_chars:,} characters')
    if args.dry_run:
        for section in sections:
            words = len(section['text'].split())
            print(f"  {section['number']} {section['title']}: {words} words (~{words / 150:.1f} min)")
        return 0

    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        print('Set ELEVENLABS_API_KEY in the environment first (never commit it).')
        return 1

    AUDIO_DIR.mkdir(exist_ok=True)
    stamps = json.loads(STAMP_PATH.read_text()) if STAMP_PATH.exists() else {}

    for section in sections:
        out_path = AUDIO_DIR / f"{section['number']}.mp3"
        digest = hashlib.sha256(section['text'].encode('utf-8')).hexdigest()[:16]
        if not args.force and out_path.exists() and stamps.get(section['number']) == digest:
            print(f"  = {out_path.name} unchanged")
            continue
        try:
            audio = speak(section['text'], key)
        except urllib.error.HTTPError as error:
            print(f"  ! {out_path.name} failed: {error.code} {error.read()[:200]}")
            return 1
        out_path.write_bytes(audio)
        stamps[section['number']] = digest
        print(f"  + {out_path.name} ({len(audio) / 1024:.0f} KB)")

    STAMP_PATH.write_text(json.dumps(stamps, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
