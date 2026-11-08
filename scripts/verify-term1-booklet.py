"""Verify the actual printed PDF against its question bank and original source images.
Usage: python scripts/verify-term1-booklet.py 10G3 [path/to/original-book.pdf]
Requires PyMuPDF, already used by the textbook-selection builder.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import fitz

root = Path(__file__).resolve().parent.parent
classroom = sys.argv[1] if len(sys.argv) > 1 else '10G3'
if classroom not in ['10G3','10A1','9G3']:
    raise SystemExit('No verified textbook booklet is published for this classroom yet.')
bank_id={'9G3':'9g3-term1','10G3':'10g3-term1','10A1':'10a1-term1'}[classroom]
slug={'9G3':'grade-9-general','10G3':'grade-10-general','10A1':'grade-10-advanced'}[classroom]
folder = root / 'public/data/exam-banks' / bank_id
bank = json.loads((folder / 'index.json').read_text())
manifest = json.loads((root / f'public/worksheets/{slug}-term1-study-booklet-manifest.json').read_text())
pdf = fitz.open(root / 'public' / bank['study_booklet'])
assert len(pdf) == manifest['pages'] <= 30
assert json.loads((folder / 'bank.json').read_text()) == bank
for outcome in bank['learning_outcomes']:
    packet = json.loads((folder / outcome['download']).read_text())
    assert packet['questions'] == [q for q in bank['questions'] if q['id'] in outcome['question_ids']]
selected = [q for q in bank['questions'] if q['id'] in manifest['selected_question_ids']]
mcqs = [q for q in selected if q['type'] == 'mcq']
key_text = '\n'.join(p.get_text() for p in pdf if 'MCQ answer key' in p.get_text() and 'Check after solving' in p.get_text())
printed = dict(re.findall(r'(\d+\.\d+):\s*([ABCD])', key_text))
assert len(printed) == len(mcqs) == 80
for q in mcqs:
    assert printed[q['display_number']] == q['answer']['correct_option_id'], q['id']
    correct = [o for o in q['options'] if o['id'] == printed[q['display_number']]]
    assert len(correct) == 1 and correct[0]['text'] == q['answer']['correct_option_text'], q['id']

def pixels(pixmap):
    return pixmap.width, pixmap.height, pixmap.n, hashlib.sha256(pixmap.samples).hexdigest()

pdf_images = {pixels(fitz.Pixmap(pdf, image[0])) for page in pdf for image in page.get_images()}
used = {asset for q in selected for asset in q['diagram_asset_ids']}
book = None
books = {}
if len(sys.argv) > 2:
    path = Path(sys.argv[2])
    if bank.get('source_parts'):
        assert len(sys.argv)==4, 'Provide both textbook parts'
        for i in [1,2]:
            part_path=Path(sys.argv[i+1])
            assert hashlib.sha256(part_path.read_bytes()).hexdigest()==bank['source_parts'][str(i)]['sha256'], 'Wrong source part'
            books[i]=fitz.open(part_path)
    else:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == bank['source_sha256'], 'Wrong source book'
        book = fitz.open(path)
for asset_id in used:
    asset = bank['assets'][asset_id]
    original = fitz.Pixmap(folder / asset['src'])
    assert pixels(original) in pdf_images, f'PDF image changed or missing: {asset_id}'
    if book or books:
        document=books[asset['source']['book_part']] if books else book
        page = document[asset['source']['pdf_page'] - 1]
        box = asset['crop_box']
        clip = fitz.Rect(box[0]*page.rect.width, box[1]*page.rect.height, box[2]*page.rect.width, box[3]*page.rect.height)
        extracted = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip)
        assert pixels(extracted) == pixels(original), f'Image differs from original book crop: {asset_id}'
print(f'{classroom}: {len(pdf)} PDF pages; all {len(mcqs)} printed MCQ keys match the bank and LO downloads; all {len(used)} diagrams preserve exact image pixels.' + (' Original textbook crops also verified.' if book or books else ''))
