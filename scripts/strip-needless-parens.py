#!/usr/bin/env python3
"""Remove grouping parentheses that carry no meaning (they only hint at how the answer was built).
(a+b)-c -> a+b-c ; k(-5b+(2ab+a)) -> k(-5b+2ab+a). Factor parentheses and parentheses after '-' or before a product/power are kept.
Applied to every option of a question together, so the correct answer is never distinguishable by its formatting."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def toks(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith('\\left(', i): out.append(('(', '\\left(')); i += 6
        elif s.startswith('\\right)', i): out.append((')', '\\right)')); i += 7
        elif s[i] == '(': out.append(('(', '(')); i += 1
        elif s[i] == ')': out.append((')', ')')); i += 1
        else: out.append(('c', s[i])); i += 1
    return out

def strip(s):
    changed = True
    while changed:
        changed = False
        t = toks(s); stack = []
        pairs = []
        for i, (k, _) in enumerate(t):
            if k == '(': stack.append(i)
            elif k == ')' and stack: pairs.append((stack.pop(), i))
        for a, b in sorted(pairs):
            inner = ''.join(x[1] for x in t[a + 1:b])
            # top-level +/- inside (outside nested groups) -> it's a sum
            d, has_op = 0, False
            for k, c in t[a + 1:b]:
                if k == '(': d += 1
                elif k == ')': d -= 1
                elif d == 0 and c in '+-': has_op = True
            if not has_op: continue
            before = ''.join(x[1] for x in t[:a]).rstrip()
            after = ''.join(x[1] for x in t[b + 1:]).lstrip()
            ok_before = before == '' or before.endswith('+') or before.endswith('\\left(') or before.endswith('(')
            ok_after = after == '' or after[0] in '+-' or after.startswith('\\right)') or after.startswith(')') or after.startswith('=')
            if before.endswith(('\\left(', '(')) and not ok_after: ok_before = False
            if not (ok_before and ok_after): continue
            if before != '' and inner.lstrip().startswith('-') and before.endswith('+'): continue
            if before.endswith(('\\left(', '(')) and not (after == '' or after.startswith(('\\right)', ')', '+', '-'))): continue
            if before.endswith(('\\left(', '(')) and inner.lstrip().startswith(('+', '-')) is False and False: pass
            new = ''.join(x[1] for x in t[:a]) + inner + ''.join(x[1] for x in t[b + 1:])
            # restore a space-insensitive but valid string
            if new != s:
                s = new; changed = True; break
    return s

def fix_question(q):
    n = 0
    if q.get('type') != 'mcq' and q.get('type') != 'MCQ': return 0
    for o in q.get('options', []):
        for k in ('text', 'math_latex'):
            if o.get(k) and ('(' in o[k]):
                new = strip(o[k])
                if new != o[k]: o[k] = new; n += 1
    a = q.get('answer', {})
    if a.get('correct_option_text') and '(' in a['correct_option_text']:
        new = strip(a['correct_option_text'])
        if new != a['correct_option_text']: a['correct_option_text'] = new; n += 1
    return n

if __name__ == '__main__':
    tot = 0
    for c in ['9G3', '10G3', '10A1']:
        p = ROOT / f'public/data/study/{c}.json'; d = json.loads(p.read_text())
        for q in d['questions']:
            n = fix_question(q); tot += n
            if n: print(c, q['id'], '|', q['answer'].get('correct_option_text'))
        if '--write' in sys.argv: p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    # calculator-support: the displayed worked answer must match the (now un-parenthesised) option text
    p = ROOT / 'public/data/study/calculator-support.json'; d = json.loads(p.read_text()); n = 0
    def walk(o):
        global n
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'math' and isinstance(v, str) and '(' in v:
                    new = strip(v)
                    if new != v: o[k] = new; n += 1
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d); tot += n
    if '--write' in sys.argv: p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print('changed fields:', tot)
