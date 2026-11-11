#!/usr/bin/env python3
"""Whole-platform question audit (teacher request 2026-11-11: "check all questions to be 100% correct without missing elements").

Structural / completeness checks for every question of every class. Prints each finding; exit code 1 if any.
  MCQ   : 2-4 options, ids A-D unique, key is one of the options, key text matches, no empty or duplicate options,
          every option has text, LaTeX or an image; "Graph X" options carry an image
  FRQ   : parts present, each with a prompt and a model answer; blanks parse; plots/number lines are well formed
  all   : instruction present; a question that refers to a figure/graph/table/image has one attached
          (figure, option images, LaTeX table, or the question card image); data the instruction points to
          ("the given line/relation/values/expression") is present; no placeholder text (undefined, NaN, TODO, ??)
  LOs   : every question belongs to an outcome list and every listed id exists
usage: python3 scripts/audit-all-questions.py [--json out.json]
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CLASSES = ['9G3', '9A', '10G3', '10A1', '11G', '11A', '12G', '12A']
REFERS_FIG = re.compile(r'\b(graph(?:ed)? (?:shown|below|above)|the graph\b|shown|figure|diagram|picture|image|the table|table below|the map|the plot|the box plot|histogram|spinner|scatter ?plot|the circle below|the triangle below)', re.I)
REFERS_DATA = re.compile(r'\b(the given (?:line|relation|expression|equation|function|point|values|sequence|data)|the values given|the following)\b', re.I)
SELF_CONTAINED = re.compile(r'describ|description|belongs to the graph|zeros of the graph|image of|dilation|spinner (?:numbered|simulat)|equal-sector spinner|sketch', re.I)
BAD_TEXT = re.compile(r'\b(undefined|NaN|None|TODO|FIXME|\[object|lorem)\b|\?\?')
norm = lambda s: re.sub(r'\s|\\[,;!: ]|\\left|\\right|\\displaystyle', '', str(s or '')).lower()


def has_visual(q):
    return bool(q.get('diagram_asset_ids')) or any(o.get('image') for o in q.get('options', [])) or q.get('figure_in_image') \
        or 'array' in (q.get('math_latex') or '') or 'tabular' in (q.get('math_latex') or '')


def audit():
    out = []
    add = lambda c, q, msg: out.append({'class': c, 'id': q['id'] if isinstance(q, dict) else q, 'issue': msg})
    for c in CLASSES:
        b = json.loads((ROOT / f'public/data/study/{c}.json').read_text())
        ids = {q['id'] for q in b['questions']}
        listed = [i for lo in b['learning_outcomes'] for i in lo['question_ids']]
        for i in set(listed) - ids: add(c, i, 'listed in an outcome but missing from questions')
        for i in ids - set(listed): add(c, i, 'question not listed in any outcome')
        if len(listed) != len(set(listed)): add(c, '-', 'a question is listed twice in outcomes')
        lo_ids = {lo['id'] for lo in b['learning_outcomes']}
        for q in b['questions']:
            if q.get('learning_outcome_id') not in lo_ids: add(c, q, 'unknown outcome ' + str(q.get('learning_outcome_id')))
            ins = q.get('instruction') or ''
            if len(ins.strip()) < 8: add(c, q, 'instruction missing/too short')
            if q.get('presentation') == 'source_card' and not q.get('diagram_asset_ids'): add(c, q, 'card question without its card image')
            txt = ' '.join([ins, q.get('math_latex') or ''] + [(o.get('text') or '') for o in q.get('options', [])] + [p.get('prompt', '') for p in q.get('parts', [])])
            if BAD_TEXT.search(txt) and not re.search(r'Undefined|undefined', txt): add(c, q, 'placeholder text: ' + BAD_TEXT.search(txt).group(0))
            if REFERS_FIG.search(ins) and not has_visual(q) and not SELF_CONTAINED.search(ins):
                if not re.search(r'graph (?:the|each|it|both)|then graph|and graph|graph the', ins, re.I): add(c, q, f'refers to "{REFERS_FIG.search(ins).group(0)}" but nothing is attached')
            if REFERS_DATA.search(ins) and not (q.get('math_latex') or has_visual(q)): add(c, q, f'refers to "{REFERS_DATA.search(ins).group(0)}" but no data is shown')
            if q['type'] == 'mcq':
                opts = q.get('options') or []
                if not 2 <= len(opts) <= 4: add(c, q, f'{len(opts)} options')
                oid = [o['id'] for o in opts]
                if len(set(oid)) != len(oid) or any(i not in 'ABCD' for i in oid): add(c, q, 'option ids not unique A-D')
                key = (q.get('answer') or {}).get('correct_option_id')
                if key not in oid: add(c, q, f'answer key {key} is not an option'); continue
                for o in opts:
                    if not (str(o.get('text') or '').strip() or o.get('math_latex') or o.get('image')): add(c, q, f'option {o["id"]} empty')
                    if re.match(r'^(\\text\{)?Graph [A-D]', str(o.get('text') or '')) and not o.get('image') and not q.get('figure_in_image'): add(c, q, f'option {o["id"]} says "Graph" but has no picture')
                    if o.get('image') and o['image'] not in b['assets']: add(c, q, f'option {o["id"]} image asset missing')
                content = [norm(o.get('math_latex') or o.get('text')) + (o.get('image') or '') for o in opts]
                if not q.get('embedded_options') and len(set(content)) != len(content): add(c, q, 'two options are identical')
                co = next(o for o in opts if o['id'] == key); ct = (q['answer'].get('correct_option_text') or '')
                if ct and norm(ct) not in (norm(co.get('math_latex')), norm(co.get('text'))): add(c, q, f'correct_option_text "{ct[:40]}" differs from option {key}')
                if not (q['answer'].get('explanation') or q['answer'].get('steps')): add(c, q, 'no explanation or steps')
            else:
                parts = q.get('parts') or []
                if not parts: add(c, q, 'written question without parts')
                for p in parts:
                    if not (p.get('prompt') or '').strip(): add(c, q, f'part {p.get("id")} has no prompt')
                    a = p.get('answer') or {}
                    if not (a.get('model_answer_and_marking') or a.get('math_latex') or a.get('steps')): add(c, q, f'part {p.get("id")} has no model answer')
                    if p.get('plot'):
                        pl = p['plot']
                        if pl.get('kind') == 'line' and not ('line' in pl and len(pl.get('bounds', [])) == 4): add(c, q, 'line plot incomplete')
                        if pl.get('kind') == 'piecewise' and not pl.get('pieces'): add(c, q, 'piecewise plot without pieces')
                    if p.get('numberline') and not ('bounds' in p['numberline'] and 'answer' in p['numberline']): add(c, q, 'number line incomplete')
                    bl = p.get('blanks')
                    if bl is not None and not (bl.get('lines') or bl.get('table') or bl.get('tables')): add(c, q, f'part {p.get("id")} blanks empty')
            for a in q.get('diagram_asset_ids', []):
                if a not in b['assets'] or not (ROOT / 'public' / b['assets'][a]['src']).exists(): add(c, q, 'figure file missing: ' + a)
    return out


if __name__ == '__main__':
    res = audit()
    for r in res: print(f"{r['class']:5} {r['id']:42} {r['issue']}")
    print(len(res), 'findings')
    if '--json' in sys.argv: Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(1 if res else 0)
