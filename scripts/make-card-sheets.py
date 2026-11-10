import json,os,sys,glob
from PIL import Image, ImageDraw, ImageChops
cls=sys.argv[1]; out=sys.argv[2]
done=set()
for f in glob.glob(f'content-imports/upper-grades/solutions/{cls}-*.json'): done|=set(json.load(open(f))['items'])
d=json.load(open(f'public/data/study/{cls}.json'))
cards=[]
for lo in d['learning_outcomes']:
    for i in lo['question_ids']:
        q=next(x for x in d['questions'] if x['id']==i)
        if q['type']=='mcq' and q.get('figure_in_image') and i not in done:
            cards.append((q['id'],q['answer']['correct_option_id'],'public/'+d['assets'][q['diagram_asset_ids'][0]]['src']))
def crop(im):
    bg=Image.new('RGB',im.size,'white'); diff=ImageChops.difference(im,bg).convert('L').point(lambda p:255 if p>110 else 0)
    bb=diff.getbbox()
    return im.crop((max(0,bb[0]-6),max(0,bb[1]-6),min(im.width,bb[2]+6),min(im.height,bb[3]+6))) if bb else im
W=700; items=[]
for i,k,s in cards:
    im=crop(Image.open(s).convert('RGB'))
    if im.width>W: im=im.resize((W,int(im.height*W/im.width)))
    items.append((i,k,im))
sheets=[];cur=[];h=0
for it in items:
    hh=it[2].height+22
    if cur and (h+hh>2100 or len(cur)>=12): sheets.append(cur);cur=[];h=0
    cur.append(it);h+=hh
if cur: sheets.append(cur)
os.system(f'rm -rf {out}'); os.makedirs(out)
for n,sh in enumerate(sheets):
    H=sum(im.height+22 for _,_,im in sh); o=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(o); y=0
    for i,k,im in sh:
        dr.rectangle([0,y,W,y+20],fill='#222'); dr.text((6,y+4),f'{i}   KEY={k}',fill='white'); y+=22; o.paste(im,(0,y)); y+=im.height
    o.save(f'{out}/s{n:02d}.png')
print(len(cards),'cards',len(sheets),'sheets')
