"""Restore reviewed lossless crops from the original Grade 9/10 Advanced part-2 PDFs.
Usage: python scripts/extract-reviewed-crops.py /path/to/9-2.pdf /path/to/10-advanced-part2.pdf
"""
from pathlib import Path
import json,hashlib,sys
import fitz
root=Path(__file__).resolve().parent.parent
assert len(sys.argv)==3,__doc__
updates=json.loads((root/'content-imports/reviewed-source-crops.json').read_text())
for folder,path in zip(['9g3-term1','10a1-term1'],map(Path,sys.argv[1:])):
 digest=hashlib.sha256(path.read_bytes()).hexdigest();book=fitz.open(path)
 for a in updates[folder].values():
  assert digest==a['source']['book_sha256'],'Source PDF hash mismatch'
  page=book[a['source']['pdf_page']-1];box=a['crop_box'];clip=fitz.Rect(box[0]*page.rect.width,box[1]*page.rect.height,box[2]*page.rect.width,box[3]*page.rect.height);pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip)
  assert (pix.width,pix.height)==(a['width'],a['height'])
  pix.save(root/f'public/data/exam-banks/{folder}'/a['src'])
 print(folder, len(updates[folder]),'reviewed crops restored')
