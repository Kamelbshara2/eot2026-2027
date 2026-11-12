#!/usr/bin/env python3
"""Clear, labelled redraws of the 10A1 LO11 dilation figures (user request, 12 Nov 2026).

The original crops (Reveal p. 120 ex. 10, 11, 17, 18 and revision-booklet Q62) are low resolution:
small vertex labels and primes are hard to read. Each redraw keeps the original's coordinates, read
from the figure grid, and is stored as a separate asset that points back to the original
(`original_asset_id`). The booklet shows the redraw and keeps the original under a toggle.

Run: python3 scripts/redraw-g10a-lo11.py   (idempotent)
"""
import json, os
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'public/data/study/10A1.json')
OUT = 'data/study-assets/10a1'

BLUE, GREEN, INK, GRID, AXIS = '#1d4ed8', '#3f7d0b', '#111827', '#cbd5e1', '#111827'

# name, (xmin, xmax, ymin, ymax), tick step, original polygon, image polygon, label offsets (dx, dy) in units
FIGS = {
    'q11_10': dict(
        rng=(-1, 9, -1, 9), step=1, tick_labels=False,
        orig=[('J', 2, 4), ('K', 4, 4), ('P', 3, 2)],
        img=[('J', 4, 8), ('K', 8, 8), ('P', 6, 4)],
        off={'J': (-0.45, 0.35), 'K': (0.4, 0.35), 'P': (0, -0.55),
             "J'": (-0.5, 0.35), "K'": (0.45, 0.35), "P'": (0, -0.55)},
        k=F(2), q='G10A-BOOK-Q11-MCQ-01', ex='10'),
    'q11_11': dict(
        rng=(-5, 5, -5, 5), step=1, tick_labels=False,
        orig=[('D', -2, 0), ('G', 0, 2), ('F', 2, -2)],
        img=[('D', -3, 0), ('G', 0, 3), ('F', 3, -3)],
        off={'D': (0.1, -0.6), 'G': (0.55, 0.05), 'F': (-0.5, -0.45),
             "D'": (-0.45, 0.45), "G'": (-0.55, 0.4), "F'": (0.5, -0.45)},
        k=F(3, 2), q='G10A-BOOK-Q11-MCQ-02', ex='11'),
    'q11_17': dict(
        rng=(-7, 7, -7, 7), step=2, tick_labels=True,
        orig=[('A', -6, 6), ('B', 6, 3), ('C', 6, -6), ('D', -6, -6)],
        img=[('A', -4, 4), ('B', 4, 2), ('C', 4, -4), ('D', -4, -4)],
        off={'A': (-0.55, 0.5), 'B': (0.6, 0.35), 'C': (0.55, -0.5), 'D': (-0.55, -0.5),
             "A'": (0.55, 0.5), "B'": (-0.1, -0.7), "C'": (-0.55, 0.55), "D'": (0.6, 0.55)},
        k=F(2, 3), q='G10A-BOOK-Q11-MCQ-03', ex='17'),
    'q11_18': dict(
        rng=(-7, 7, -7, 7), step=2, tick_labels=True,
        orig=[('P', 2, 4), ('Q', 4, -4), ('R', -4, 2)],
        img=[('P', 3, 6), ('Q', 6, -6), ('R', -6, 3)],
        off={'P': (0.65, 0.05), 'Q': (-0.65, -0.3), 'R': (0.1, -0.7),
             "P'": (0.2, 0.6), "Q'": (0.55, -0.45), "R'": (-0.6, 0.45)},
        k=F(3, 2), q='G10A-BOOK-Q11-MCQ-04', ex='18'),
}

# Revision booklet Q62 logo: outer tips read from the grid; inner corners approximated (shape only).
LOGO = [(-2, 3), (0, 1.6), (2, 2), (0.6, 0.9), (2, -1), (0, 0.4), (-2, 0), (-0.6, 1.2)]


def frame(rng, step, tick_labels, size=440, pad=34):
    x0, x1, y0, y1 = rng
    u = (size - 2 * pad) / max(x1 - x0, y1 - y0)
    W, H = 2 * pad + (x1 - x0) * u, 2 * pad + (y1 - y0) * u
    X = lambda x: pad + (x - x0) * u
    Y = lambda y: pad + (y1 - y) * u
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H + 34:.0f}" width="{W:.0f}" height="{H + 34:.0f}" font-family="Arial, Helvetica, sans-serif">',
         f'<rect width="100%" height="100%" fill="#ffffff"/>']
    for x in range(x0, x1 + 1):
        s.append(f'<line x1="{X(x):.1f}" y1="{Y(y0):.1f}" x2="{X(x):.1f}" y2="{Y(y1):.1f}" stroke="{GRID}" stroke-width="1"/>')
    for y in range(y0, y1 + 1):
        s.append(f'<line x1="{X(x0):.1f}" y1="{Y(y):.1f}" x2="{X(x1):.1f}" y2="{Y(y):.1f}" stroke="{GRID}" stroke-width="1"/>')
    # axes with arrows
    s.append(f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{AXIS}"/></marker></defs>')
    s.append(f'<line x1="{X(x0) - 10:.1f}" y1="{Y(0):.1f}" x2="{X(x1) + 12:.1f}" y2="{Y(0):.1f}" stroke="{AXIS}" stroke-width="1.6" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(y0) + 10:.1f}" x2="{X(0):.1f}" y2="{Y(y1) - 12:.1f}" stroke="{AXIS}" stroke-width="1.6" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    s.append(f'<text x="{X(x1) + 8:.1f}" y="{Y(0) + 20:.1f}" font-size="17" font-style="italic" fill="{INK}">x</text>')
    s.append(f'<text x="{X(0) + 8:.1f}" y="{Y(y1) - 6:.1f}" font-size="17" font-style="italic" fill="{INK}">y</text>')
    s.append(f'<text x="{X(0) - 16:.1f}" y="{Y(0) + 18:.1f}" font-size="16" font-style="italic" fill="{INK}">O</text>')
    if tick_labels:
        for v in range(x0 - x0 % step, x1 + 1, step):
            if v and x0 < v < x1:
                s.append(f'<text x="{X(v):.1f}" y="{Y(0) + 17:.1f}" font-size="13" text-anchor="middle" fill="#334155" paint-order="stroke" stroke="#fff" stroke-width="3">{str(v).replace("-", "−")}</text>')
        for v in range(y0 - y0 % step, y1 + 1, step):
            if v and y0 < v < y1:
                s.append(f'<text x="{X(0) - 6:.1f}" y="{Y(v) + 5:.1f}" font-size="13" text-anchor="end" fill="#334155" paint-order="stroke" stroke="#fff" stroke-width="3">{str(v).replace("-", "−")}</text>')
    else:
        for v in range(x0, x1 + 1):
            if v > 0:
                s.append(f'<text x="{X(v):.1f}" y="{Y(0) + 17:.1f}" font-size="12" text-anchor="middle" fill="#64748b">{v}</text>')
        for v in range(y0, y1 + 1):
            if v > 0:
                s.append(f'<text x="{X(0) - 6:.1f}" y="{Y(v) + 4:.1f}" font-size="12" text-anchor="end" fill="#64748b">{v}</text>')
    return s, X, Y, W, H


def poly(s, X, Y, pts, colour, fill_op):
    d = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
    s.append(f'<polygon points="{d}" fill="{colour}" fill-opacity="{fill_op}" stroke="{colour}" stroke-width="3" stroke-linejoin="round"/>')


def dots(s, X, Y, pts, colour):
    for x, y in pts:
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4.2" fill="{colour}" stroke="#fff" stroke-width="1.5"/>')


def label(s, X, Y, x, y, name, colour, off):
    dx, dy = off
    letter, prime = name[0], "′" if name.endswith("'") else ''
    s.append(f'<text x="{X(x + dx):.1f}" y="{Y(y + dy) + 7:.1f}" font-size="21" font-weight="700" font-style="italic" text-anchor="middle" fill="{colour}" paint-order="stroke" stroke="#ffffff" stroke-width="4" stroke-linejoin="round">{letter}{prime}</text>')


def legend(s, W, H):
    y = H + 14
    for x, colour, en, ar in [(W / 2 - 190, BLUE, 'Original', 'الأصل'), (W / 2 + 10, GREEN, 'Image (′)', 'الصورة')]:
        s.append(f'<line x1="{x:.0f}" y1="{y}" x2="{x + 28:.0f}" y2="{y}" stroke="{colour}" stroke-width="4"/>')
        s.append(f'<text x="{x + 34:.0f}" y="{y + 5}" font-size="14" fill="{INK}">{en}</text>')
        s.append(f'<text x="{x + 40 + 7.6 * len(en):.0f}" y="{y + 5}" font-size="14" font-weight="700" fill="{colour}">{ar}</text>')


def draw(fig):
    s, X, Y, W, H = frame(fig['rng'], fig['step'], fig['tick_labels'])
    o = [(x, y) for _, x, y in fig['orig']]; i = [(x, y) for _, x, y in fig['img']]
    poly(s, X, Y, i, GREEN, 0.10); poly(s, X, Y, o, BLUE, 0.12)
    dots(s, X, Y, i, GREEN); dots(s, X, Y, o, BLUE)
    for n, x, y in fig['orig']:
        label(s, X, Y, x, y, n, BLUE, fig['off'][n])
    for n, x, y in fig['img']:
        label(s, X, Y, x, y, n + "'", GREEN, fig['off'][n + "'"])
    legend(s, W, H)
    s.append('</svg>')
    return '\n'.join(s)


def draw_logo():
    s, X, Y, W, H = frame((-7, 7, -4, 9), 1, False, size=460)
    big = [(x * 2.5, y * 2.5) for x, y in LOGO]
    poly(s, X, Y, big, GREEN, 0.10); poly(s, X, Y, LOGO, BLUE, 0.15)
    for (x, y), n in [((-2, 3), 'A'), ((2, 2), 'B'), ((2, -1), 'C'), ((-2, 0), 'D')]:
        dots(s, X, Y, [(x, y)], BLUE); dots(s, X, Y, [(x * 2.5, y * 2.5)], GREEN)
    # tips written as coordinates so the scale factor can be read without guessing
    for (x, y), (dx, dy) in [((2, 2), (0.9, -0.35)), ((-2, 0), (0, -0.75))]:
        s.append(f'<text x="{X(x + dx):.1f}" y="{Y(y + dy):.1f}" font-size="14" font-weight="700" text-anchor="middle" fill="{BLUE}" paint-order="stroke" stroke="#fff" stroke-width="4">({x}, {y})</text>')
    for (x, y), (dx, dy) in [((5, 5), (0.4, 0.6)), ((-5, 0), (-0.6, -0.75))]:
        s.append(f'<text x="{X(x + dx):.1f}" y="{Y(y + dy):.1f}" font-size="14" font-weight="700" text-anchor="middle" fill="{GREEN}" paint-order="stroke" stroke="#fff" stroke-width="4">({x}, {y})</text>')
    legend(s, W, H)
    s.append('</svg>')
    return '\n'.join(s)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    qs = {q['id']: q for q in bank['questions']}
    os.makedirs(os.path.join(ROOT, 'public', OUT), exist_ok=True)
    jobs = [(k, draw(f), f['q'], f'Reveal p. 120, exercise {f["ex"]}') for k, f in FIGS.items()]
    jobs.append(('rev062', draw_logo(), 'G10A-REV-Q11-MCQ-01', 'revision booklet Q62 (Reveal p. 120, exercise 12)'))
    for orig_id, svg, qid, where in jobs:
        # every image vertex must be k × the original vertex (dilation centred at the origin)
        if orig_id in FIGS:
            f = FIGS[orig_id]
            for (_, x, y), (_, x2, y2) in zip(f['orig'], f['img']):
                assert F(x2) == f['k'] * x and F(y2) == f['k'] * y, (orig_id, x, y, x2, y2)
        rid = orig_id + '_redraw'
        path = f'{OUT}/{rid}.svg'
        open(os.path.join(ROOT, 'public', path), 'w', encoding='utf-8').write(svg + '\n')
        bank['assets'][rid] = {
            'src': path, 'width': 440, 'height': 474,
            'alt_text': f'Clear redraw of the textbook diagram ({where}): original in blue, primed image in green, labels with primes.',
            'alt_text_ar': 'رسم واضح للشكل: الأصل بالأزرق والصورة (بالشرطة ′) بالأخضر.',
            'original_asset_id': orig_id,
            'source': {**bank['assets'][orig_id]['source'], 'adaptation': 'redrawn_for_clarity'},
        }
        q = qs[qid]
        q['diagram_asset_ids'] = [rid]
    # Step corrections found while reading the grids
    q = qs['G10A-BOOK-Q11-MCQ-04']
    q['answer']['steps'][0].update({
        'text': 'Compare matching points: R(−4, 2) → R′(−6, 3). Check with another point: Q(4, −4) → Q′(6, −6).',
        'ar': 'قارن النقاط المتناظرة: R(−4, 2) ← R′(−6, 3). تحقّق بنقطة أخرى: Q(4, −4) ← Q′(6, −6).',
        'latex': 'k=\\tfrac{-6}{-4}=\\tfrac{6}{4}=\\tfrac32',
        'why': 'For a dilation centred at the origin, every image coordinate = k × original coordinate, so divide image by original.',
        'why_ar': 'في التمدد حول نقطة الأصل: كل إحداثي في الصورة = k × الإحداثي الأصلي، لذا نقسم الصورة على الأصل.'})
    q['answer']['explanation'] = 'The primed image is larger: R(−4, 2) → R′(−6, 3), so each coordinate is multiplied by 3/2.'
    q = qs['G10A-BOOK-Q11-MCQ-01']
    q['answer']['steps'][1].update({'text': 'k = 2 > 1, so the image is an enlargement. Check: P(3, 2) → P′(6, 4).',
        'ar': 'k = 2 > 1 إذن الصورة تكبير. تحقّق: P(3, 2) ← P′(6, 4).',
        'why': 'Checking a second pair of matching points confirms the same k works for the whole figure.',
        'why_ar': 'التحقق بزوج آخر من النقاط المتناظرة يؤكد أن k نفسه يصلح للشكل كله.'})
    q = qs['G10A-REV-Q11-MCQ-01']
    q['answer']['steps'][0].update({'text': 'Compare matching tips of the logo: (2, 2) → (5, 5) and (−2, 0) → (−5, 0).',
        'ar': 'قارن الأطراف المتناظرة للشعار: (2, 2) ← (5, 5) و (−2, 0) ← (−5, 0).',
        'latex': 'k=\\tfrac{5}{2}=2.5',
        'why': 'Image coordinate ÷ original coordinate gives k; both tips give the same value, so k is confirmed.',
        'why_ar': 'إحداثي الصورة ÷ الإحداثي الأصلي = k؛ والطرفان يعطيان القيمة نفسها فيتأكد k.'})
    open(BANK, 'w', encoding='utf-8').write(json.dumps(bank, ensure_ascii=False, separators=(',', ':')))
    print('redrawn', len(jobs))


if __name__ == '__main__':
    main()
