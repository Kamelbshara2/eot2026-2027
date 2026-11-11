"""Calculator + written-solution support for Grade 9 questions that have none yet (all of 9A; questions added to 9G3).
Existing 9G3 entries (emulator-verified key sequences) are kept untouched."""
import json, sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('up', ROOT / 'scripts/calculator-guides/build-upper-support.py'); up = importlib.util.module_from_spec(spec); spec.loader.exec_module(up)
sup_path = ROOT / 'public/data/study/calculator-support.json'; sup = json.loads(sup_path.read_text())
for cls in ['9A', '9G3']:
    bank = json.loads((ROOT / f'public/data/study/{cls}.json').read_text())
    entry = sup['classes'].setdefault(cls, {'outcomes': {}, 'questions': {}})
    for lo in bank['learning_outcomes']:
        if lo['id'] not in entry['outcomes']:
            r = up.route_for(lo['title']); entry['outcomes'][lo['id']] = {'title': lo['title'], 'prepare': f"{lo['rule_summary']} {up.ROUTES[r][0]}", 'route': r}
    n = 0
    for q in bank['questions']:
        if q['id'] in entry['questions']: continue
        lo = entry['outcomes'][q['learning_outcome_id']]; route = lo.get('route') or up.route_for(lo['title'])
        steps = up.ROUTES[route][1] or up.ROUTES['geo'][1]
        if q['type'] == 'mcq':
            a = q['answer']; o = next(o for o in q['options'] if o['id'] == a['correct_option_id'])
            sols = [{'part': 'Answer', 'math': o.get('math_latex') or '', 'text': a['explanation'], 'answer_text': '' if o.get('math_latex') else o.get('text', '')}]
        else:
            sols = [{'part': p['id'], 'math': p['answer'].get('math_latex', ''), 'text': p['answer'].get('model_answer_and_marking', ''), 'answer_text': ''} for p in q['parts']]
        entry['questions'][q['id']] = {'outcome': q['learning_outcome_id'], 'outcome_title': lo['title'], 'role': 'reasoning', 'prepare': lo['prepare'], 'operations': [], 'tables': [], 'solutions': sols,
                                       'source_ids': ['reviewed-bank', 'upstream-modes'], 'setup': steps, 'interpret': 'Write the method, the substitution and the final answer. Calculator output alone does not justify the answer.'}
        n += 1
    print(cls, 'added', n, 'total', len(entry['questions']))
sup_path.write_text(json.dumps(sup, ensure_ascii=False, indent=2) + '\n')
