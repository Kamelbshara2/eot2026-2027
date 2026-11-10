#!/usr/bin/env python3
"""Compare the official coverage sheet (exam structure) with the exercises that exist in the site data.

Structure encodings below are transcribed from content-imports/term1-coverage/*.pdf.
An item is (printed_page, [exercise labels]). Labels: '12' numbers, 'ex3' worked examples, 'Learn'.
Output: content-imports/coverage-gap.json and a console table. Only exercises present in the JSON data
(public/data/study/<class>.json, textbook_exercise questions) count as available; nothing is guessed.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def rng(a, b): return [str(i) for i in range(a, b + 1)]

S = {
 '9G3': {
  1: [(9, rng(11, 21))], 2: [(42, rng(23, 33))], 3: [(81, rng(1, 4) + ['7', '8'] + rng(13, 18))], 4: [(125, rng(11, 18))], 5: [(31, rng(1, 9))],
  6: [(97, rng(1, 6))], 7: [(37, ['ex2'])], 8: [(221, ['ex3', 'ex4'])], 9: [(113, rng(13, 18))], 10: [(89, rng(18, 26))], 11: [(248, rng(10, 15))],
  12: [(235, rng(9, 14))], 13: [(236, rng(37, 39))], 14: [(263, rng(7, 9))], 15: [(223, ['ex6', 'ex7', 'ex8'])],
  16: [(265, ['18a', '18b', '18c', '18d'])], 17: [(257, rng(28, 31))], 18: [(233, ['ex6']), (236, rng(23, 28))], 19: [(18, rng(1, 12))],
  20: [(89, rng(27, 35))], 21: [(19, rng(42, 50))], 22: [(125, rng(19, 22))], 23: [(97, rng(1, 16)), (99, ['ex6', 'ex7'] + rng(25, 39))],
  24: [(215, rng(5, 8))], 25: [(263, rng(1, 6))], 26: [(255, rng(9, 22))]},
 '10G3': {
  1: [(649, rng(1, 6))], 2: [(657, rng(1, 6))], 3: [(658, rng(15, 20))], 4: [(665, rng(1, 6))], 5: [(674, rng(73, 78))], 6: [(672, rng(21, 26))],
  7: [(679, rng(1, 6))], 8: [(583, rng(5, 9))], 9: [(591, rng(11, 14))], 10: [(599, rng(9, 16))], 11: [(609, rng(67, 70))], 12: [(607, rng(15, 18)), (608, ['55', '56'])],
  13: [(615, rng(1, 8))], 14: [(722, ['29', '30'])], 15: [(730, rng(37, 39))], 16: [(707, rng(3, 10))], 17: [(721, rng(5, 10))], 18: [(707, rng(23, 26)), (708, rng(27, 30))],
  19: [(713, rng(1, 6))], 20: [(729, rng(1, 6))], 21: [(636, rng(27, 34))], 22: [(650, rng(18, 23))], 23: [(576, rng(25, 30)), (578, rng(56, 58))],
  24: [(695, rng(1, 4))], 25: [(722, rng(31, 34))]},
}

def _g10a():
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/build-g10a-revision-questions.py'); m = importlib.util.module_from_spec(spec)
    argv = sys.argv; sys.argv = argv[:1]; spec.loader.exec_module(m); sys.argv = argv
    return {int(lo[2:]): v for lo, v in m.STRUCTURE.items()}
S['10A1'] = _g10a()   # official 10 Advanced coverage sheet (EoT1_Coverage_G10_Adv_Math_Rev_T1)

def norm(ex):
    e = ex.strip()
    m = re.match(r'^Example (\d)', e, re.I)
    if m: return 'ex' + m.group(1)
    if e.lower().startswith('match graph'): return 'ex6'   # the original Example 6 graph matches (p.233)
    m = re.match(r'^(\d+[a-d]?)', e)
    return m.group(1) if m else e

def main():
    out, lines = {}, []
    for c, spec in S.items():
        bank = json.loads((ROOT / f'public/data/study/{c}.json').read_text())
        have = {}
        for q in bank['questions']:
            if q.get('source_kind') != 'textbook_exercise': continue
            have.setdefault(q['learning_outcome_id'], set()).add((q['source']['printed_page'], norm(q['source']['exercise'])))
        out[c] = {}
        tot_s = tot_h = 0
        for n, items in spec.items():
            lo = f'LO{n:02d}'; need = [(p, e) for p, es in items for e in es]
            got = [x for x in need if x in have.get(lo, set())]
            miss = [x for x in need if x not in have.get(lo, set())]
            tot_s += len(need); tot_h += len(got)
            out[c][lo] = {'structure_items': len(need), 'in_site_data': len(got), 'missing': [f'p.{p} #{e}' for p, e in miss],
                          'pages_to_upload': sorted({p for p, _ in miss})}
        lines.append(f'{c}: structure items {tot_s}, present in site data {tot_h} ({round(100 * tot_h / tot_s)}%), missing {tot_s - tot_h}')
    (ROOT / 'content-imports/coverage-gap.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print('\n'.join(lines))
    for c in out:
        print('==', c)
        for lo, v in out[c].items():
            if v['missing']: print(f"  {lo}: {v['in_site_data']}/{v['structure_items']} present; missing {len(v['missing'])} -> pages {v['pages_to_upload']}")

if __name__ == '__main__':
    main()
