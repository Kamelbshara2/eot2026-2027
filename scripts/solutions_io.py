"""Tiny writer for hand-authored worked solutions. items: {id: (verified, [(text, latex), ...]) | (verified, note, steps)}"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def save(cls, name, items):
    out = {}
    for qid, v in items.items():
        ver, *rest = v; steps = rest[-1]; note = rest[0] if len(rest) == 2 else ''
        out[qid] = {'steps': [{'text': t, 'latex': l} for t, l in steps], 'verified': bool(ver), **({'note': note} if note else {})}
    (ROOT / f'content-imports/upper-grades/solutions/{cls}-{name}.json').write_text(json.dumps({'class': cls, 'items': out}, ensure_ascii=False, indent=1))
    print(cls, name, len(out))
