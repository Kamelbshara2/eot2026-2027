#!/usr/bin/env python3
"""Import the Grade 10 Advanced revision booklet (teacher-supplied PDF, 200 solved questions) into the study bank.

Stages (run with --stage):
  parse   PDF -> content-imports/g10a-revision/items.json (+ figure PNGs under content-imports/g10a-revision/figures/)
  report  duplicate analysis against the current 10A1 study bank
Provenance of every imported question: file name, sha256, PDF page and booklet question number.
Nothing from the booklet is trusted blindly: keys are verified separately (scripts/audit-study-questions.py).
"""
import json, re, sys, hashlib
from pathlib import Path
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent
PDF = Path(sys.argv[sys.argv.index('--pdf') + 1]) if '--pdf' in sys.argv else None
OUT = ROOT / 'content-imports/g10a-revision'

TOPICS = [  # (first pdf page, heading, learning outcome of the current bank)
    (2, 'Polynomials', 'LO01'), (6, 'Multiplying Binomials', 'LO02'), (8, 'Factoring by Grouping', 'LO03'), (12, 'Factoring Trinomials', 'LO04'),
    (14, 'Interior Angles', 'LO05'), (17, 'Parallelograms', 'LO06'), (19, 'Tests for Parallelograms', 'LO07'), (22, 'Kites', 'LO08'),
    (25, 'Dilations', 'LO09'), (27, 'Similar Polygons', 'LO10'), (29, 'Scale Factors', 'LO11'), (32, 'Similar Triangles', 'LO12'),
    (36, 'Proportional Parts', 'LO13'), (39, 'Similar Triangle Relationships', 'LO14'), (45, 'Geometric Mean', 'LO15'), (49, 'Pythagorean Theorem', 'LO16'),
    (53, 'Special Right Triangles', 'LO17'), (61, 'Trigonometry', 'LO18'), (68, 'Applying Trigonometry', 'LO19'), (72, 'Triangle Area', 'LO20'),
    (77, 'Factoring Special Products', 'LO21'), (81, 'Polygon Angles', 'LO22'), (85, 'Solving Similar Triangles', 'LO23'), (89, 'Coordinates in Space', 'LO24'),
    (94, 'Law of Sines', 'LO25')]

SUP = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-'))
FRAC = {'½': r'\frac{1}{2}', '⅓': r'\frac{1}{3}', '⅔': r'\frac{2}{3}', '¼': r'\frac{1}{4}', '¾': r'\frac{3}{4}', '⅕': r'\frac{1}{5}', '⅛': r'\frac{1}{8}'}
NOISE = re.compile(r'^(π|7|√|x²|∞|Σ|3\s+\+\s+5\s+=\s+8|\d+)$')

def u2tex(s):
    """Unicode maths text -> LaTeX (best effort; verified by rendering in tests)."""
    t = s.replace('−', '-').replace('–', '-').replace('\u2009', ' ').replace('\xa0', ' ')
    t = re.sub(r'([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)', lambda m: '^{' + ''.join(SUP[c] for c in m.group(1)) + '}', t)
    for k, v in FRAC.items(): t = t.replace(k, v + ' ')
    t = re.sub(r'√\(([^()]*)\)', r'\\sqrt{\1}', t)
    t = re.sub(r'√\s*([A-Za-z0-9.]+)', r'\\sqrt{\1}', t)
    rep = {'×': r'\times ', '·': r'\cdot ', '÷': r'\div ', '≈': r'\approx ', '≠': r'\ne ', '≤': r'\le ', '≥': r'\ge ', 'π': r'\pi ', '°': r'^\circ ', '△': r'\triangle ', '∼': r'\sim ', '~': r'\sim ',
           '∠': r'\angle ', '′': "'", '∥': r'\parallel ', '⊥': r'\perp ', '≅': r'\cong ', '∴': r'\therefore '}
    for k, v in rep.items(): t = t.replace(k, v)
    return re.sub(r'\s+', ' ', t).strip()

def parse(pdf):
    doc = fitz.open(pdf)
    items, cur = [], None
    topic_for = lambda pn: [t for t in TOPICS if t[0] <= pn][-1]
    (OUT / 'figures').mkdir(parents=True, exist_ok=True)
    for pn in range(2, len(doc) + 1):
        page = doc[pn - 1]; events = []
        for b in page.get_text('blocks'):
            txt = b[4].strip()
            if not txt or 'GRADE 10 ADVANCED' in txt or '2026-2027' in txt or NOISE.match(txt): continue
            events.append((b[1], 'T', txt))
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]): events.append((r.y0, 'I', (img[0], r)))
        events.sort(key=lambda e: e[0])
        head = topic_for(pn)
        for y, kind, payload in events:
            if kind == 'T':
                txt = payload
                if txt == head[1] or txt == 'Mathematics Exam Revision - Solutions': continue
                m = re.match(r'^(\d{1,3})\.\n(.*)$', txt, re.S)
                if m:
                    cur = {'number': int(m.group(1)), 'page': pn, 'topic': head[1], 'lo': head[2], 'stem_lines': m.group(2).split('\n'), 'options': {}, 'key': None, 'solution': [], 'figures': [], 'extra': [], 'part': 'frq' if int(m.group(1)) >= 147 else 'mcq'}
                    items.append(cur); continue
                if cur is None: continue
                if re.match(r'^[A-D]\. ', txt): cur['options'][txt[0]] = txt[3:].replace('\n', ' ').strip(); continue
                mk = re.match(r'^Correct answer: ([A-D])', txt)
                if mk: cur['key'] = mk.group(1); continue
                if txt.startswith('Solution'): cur['solution'] += txt.split('\n')[1:]; cur['in_solution'] = True; continue
                if cur.get('in_solution'): cur['solution'] += txt.split('\n')
                else: cur['extra'] += txt.split('\n')
            else:
                if cur is None: continue
                xref, rect = payload
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha >= 4: pix = fitz.Pixmap(fitz.csRGB, pix)
                fn = f'rev{cur["number"]:03d}_{len(cur["figures"]) + 1}.png'
                pix.save(str(OUT / 'figures' / fn))
                cur['figures'].append({'file': fn, 'page': pn, 'width': pix.width, 'height': pix.height})
        for it in items:
            if it['page'] != pn: it['in_solution'] = it.get('in_solution', False)
    for it in items: it.pop('in_solution', None)
    return items

def split_stem(lines):
    """instruction = first sentence(s) up to a terminal . ? ; the rest is the expression / givens."""
    ins, rest, done = [], [], False
    for ln in lines:
        if not done:
            ins.append(ln)
            if ln.rstrip().endswith(('.', '?', ':')): done = True
        else: rest.append(ln)
    return ' '.join(ins).strip(), rest

def main():
    stage = sys.argv[sys.argv.index('--stage') + 1] if '--stage' in sys.argv else 'parse'
    if stage == 'parse':
        items = parse(PDF)
        for it in items:
            ins, rest = split_stem(it['stem_lines'] + it['extra'])
            it['instruction'] = ins; it['math_lines'] = rest
        meta = {'file_name': 'G10A-revision-solutions-booklet.pdf', 'sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(), 'pages': 99,
                'title': 'Mathematics Exam Revision - Solutions · Grade 10 Advanced · Term 1 (teacher-supplied)', 'author_credit': 'Elsayed Abdelkader (as printed in the footer)'}
        (OUT / 'items.json').write_text(json.dumps({'source': meta, 'items': items}, ensure_ascii=False, indent=1))
        from collections import Counter
        print(len(items), 'items;', Counter(i['part'] for i in items), 'with figures:', sum(1 for i in items if i['figures']))
        bad = [i['number'] for i in items if (i['part'] == 'mcq' and (len(i['options']) != 4 or not i['key'])) or (i['part'] == 'frq' and not i['solution'])]
        print('malformed:', bad)

if __name__ == '__main__':
    main()
