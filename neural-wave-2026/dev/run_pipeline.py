#!/usr/bin/env python3
"""Generate front.png for all 15 test garments (g01–g15) with the Sartiq pipeline."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

DEV = Path(__file__).resolve().parent
BACKEND = DEV / 'btc-sartiq/backend'


def load_inputs(dataset):
    manifest = dataset / 'test/inputs.jsonl'
    rows = [json.loads(line) for line in manifest.read_text(encoding='utf-8-sig').splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    expected = {f'g{i:02}' for i in range(1, 16)}
    ids = [row.get('garment_id') for row in rows]
    if len(ids) != 15 or set(ids) != expected:
        raise ValueError('The test manifest must contain exactly g01–g15, with no duplicates.')
    selected = []
    for row in sorted(rows, key=lambda row: row['garment_id']):
        inputs = row.get('inputs')
        if row.get('view', 'front') != 'front':
            raise ValueError(f"{row['garment_id']}: the front view is required.")
        if not isinstance(inputs, list) or not 1 <= len(inputs) <= 5:
            raise ValueError(f"{row['garment_id']}: inputs must contain 1 to 5 photos.")
        paths = [(dataset / path).resolve() for path in inputs]
        for path in paths:
            if not path.is_file():
                raise ValueError(f'Missing photo: {path}')
        selected.append((row['garment_id'], paths))
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True,
                        help='Dataset folder containing test/inputs.jsonl')
    parser.add_argument('--team', default='btc', help='Team name (default: btc)')
    parser.add_argument('--out', type=Path, default=DEV / 'submissions',
                        help='Output folder (default: dev/submissions)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Check manifest and paths without API calls or file writes')
    args = parser.parse_args(argv)
    if (not re.fullmatch(r'[a-z0-9_-]+', args.team)
            or re.fullmatch(r'con|prn|aux|nul|com[0-9]|lpt[0-9]', args.team)):
        parser.error('--team must be a valid folder name using lowercase letters, digits, - or _.')
    try:
        selected = load_inputs(args.dataset.resolve())
        for identity, paths in selected:
            destination = args.out / args.team / identity / 'front.png'
            if destination.parent.is_symlink() or destination.parent.parent.is_symlink():
                raise ValueError(f'Submission folders must not be symlinks: {destination.parent}')
            for suffix in ('.png', '.jpg', '.jpeg', '.webp'):
                candidate = destination.with_suffix(suffix)
                if candidate.exists() or candidate.is_symlink():
                    raise ValueError(f'Output already exists: {candidate}. Use --out with a new folder.')
            print(f'{identity}: {len(paths)} photos -> {destination}', flush=True)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    if args.dry_run:
        print('Check complete: 15 garments, no API calls.')
        return 0

    # Use the backend environment even when launched with the system Python.
    python = BACKEND / '.venv/bin/python'
    if python.is_file() and os.path.abspath(sys.executable) != str(python):
        os.execv(str(python), [str(python), str(Path(__file__).resolve()),
                             *(sys.argv[1:] if argv is None else argv)])
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv
    load_dotenv(BACKEND / '.env')
    from pipeline import build_pipeline, normalize_photo, generation_settings
    from vision import analysis_settings
    generation_settings()
    analysis_settings()

    failures = []
    for identity, paths in selected:
        destination = args.out / args.team / identity / 'front.png'
        temporary = destination.with_name('.front.tmp.png')
        try:
            photos = [normalize_photo(path.read_bytes()) for path in paths]
            state = build_pipeline(
                lambda **event: print(identity, event['status'], flush=True)
            ).invoke({'image': photos[0], 'garment': 'clothing',
                      'additional_images': photos[1:]})
            destination.parent.mkdir(parents=True, exist_ok=True)
            state['result'].convert('RGB').save(temporary, format='PNG')
            temporary.replace(destination)
            print(f"OK {identity}: {state.get('quality', {}).get('status', 'complete')}", flush=True)
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            failures.append(identity)
            print(f'ERROR {identity}: {type(exc).__name__}', file=sys.stderr, flush=True)
    print(f'Completed {15 - len(failures)}/15 garments: {args.out / args.team}')
    if failures:
        print('Missing garments: ' + ', '.join(failures), file=sys.stderr)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
