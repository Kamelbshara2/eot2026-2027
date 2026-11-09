"""Lossless original crops for the confirmed four-outcome Advanced assessment."""
import fitz,json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
path=Path(sys.argv[1]);sha=hashlib.sha256(path.read_bytes()).hexdigest()
assert sha=='7ba96d714c63670cda31b98e4593ade9077c05a55e81d11fe0e3af1d7865a31a','Expected uploaded Advanced part 2'
doc=fitz.open(path);out=root/'public/data/exam-banks/10a1-four-outcomes-assessment';(out/'assets').mkdir(parents=True,exist_ok=True);assets={}
# Pixel coordinates refer to the reviewed 893 x 1263 page renders.
crops={
165:{1:[129,213,233,237],2:[365,207,481,240],3:[602,213,719,237],4:[129,245,250,267],5:[365,245,478,267],6:[602,245,719,267],11:[128,677,330,801],12:[448,677,685,803],13:[128,834,347,965],14:[448,832,685,966]},
171:{1:[132,211,358,338],2:[364,211,572,370],3:[606,211,855,324],4:[134,389,360,532],5:[362,389,607,525],6:[609,389,855,505],7:[132,600,323,737],8:[365,600,598,739],9:[608,600,855,702],10:[129,758,343,860],11:[364,757,555,901],12:[609,758,811,944]},
172:{20:[50,500,180,536],21:[280,500,397,536],22:[516,500,622,536]},
177:{13:[129,974,370,1007],14:[478,974,735,1007],15:[129,1028,345,1063],16:[477,1028,699,1063],17:[128,1082,343,1115],18:[477,1082,728,1115]},
178:{19:[50,189,304,218],20:[378,189,610,218],21:[50,230,269,272],22:[378,230,619,273],23:[50,287,355,314],24:[378,287,665,314]},
184:{19:[49,164,220,339],20:[279,164,478,283],21:[518,164,686,350],22:[49,350,225,487],23:[278,350,467,437],24:[518,350,701,458],25:[555,520,771,658]},
185:{33:[129,503,291,638],34:[361,503,595,637],35:[596,503,808,638],36:[129,651,341,773],37:[361,651,570,778],38:[596,648,798,804]}}
for page_no,items in crops.items():
 page=doc[page_no-57]
 for n,px in items.items():
  b=[v/(893 if i%2==0 else 1263) for i,v in enumerate(px)]
  key=f'p{page_no}-q{n}';clip=fitz.Rect(b[0]*page.rect.width,b[1]*page.rect.height,b[2]*page.rect.width,b[3]*page.rect.height)
  pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip)
  excluded=[]
  if page_no==171 and n==12:
   # The next exercise's 'dock' label overlaps the rectangular bounding box.
   # Exclude only that empty lower-left corner, retaining the complete triangle.
   pix.set_rect(fitz.IRect(pix.x,pix.y+pix.height-42,pix.x+260,pix.y+pix.height),(255,255,255))
   excluded=['Adjacent exercise 13 label, lower-left corner outside the question 12 triangle']
  dest=out/'assets'/f'{key}.png';pix.save(dest)
  assets[key]=dict(src=f'assets/{key}.png',width=pix.width,height=pix.height,book_sha256=sha,printed_page=page_no,pdf_page=page_no-56,exercise=n,crop_box=b,excluded_adjacent_content=excluded,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(out/'source-images.json').write_text(json.dumps(assets,indent=2)+'\n');print(len(assets),'original book crops')
