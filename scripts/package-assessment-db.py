"""Produce a self-contained SQLite/JSON/SQL assessment transfer package."""
from pathlib import Path
import json,sqlite3,hashlib,zipfile,shutil
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'artifacts/assessment-transfer';OUT.mkdir(parents=True,exist_ok=True)
path=OUT/'assessment-bank.sqlite'
if path.exists():path.unlink()
db=sqlite3.connect(path);db.executescript('''PRAGMA foreign_keys=ON;
CREATE TABLE classrooms(id TEXT PRIMARY KEY,grade INTEGER NOT NULL,track TEXT NOT NULL CHECK(track IN ('general','advanced')));
CREATE TABLE learning_outcomes(id TEXT PRIMARY KEY,classroom_id TEXT NOT NULL REFERENCES classrooms(id),code TEXT NOT NULL,title TEXT NOT NULL,title_ar TEXT NOT NULL,metadata_json TEXT NOT NULL,UNIQUE(classroom_id,code));
CREATE TABLE questions(id TEXT PRIMARY KEY,learning_outcome_id TEXT NOT NULL REFERENCES learning_outcomes(id),type TEXT NOT NULL CHECK(type IN ('mcq','frq')),source_kind TEXT NOT NULL,difficulty TEXT NOT NULL,stem TEXT NOT NULL,math_latex TEXT,render_metadata_json TEXT NOT NULL,source_json TEXT NOT NULL,skill_tags_json TEXT NOT NULL,marks REAL);
CREATE TABLE options(question_id TEXT NOT NULL REFERENCES questions(id),id TEXT NOT NULL,text TEXT NOT NULL,math_latex TEXT,PRIMARY KEY(question_id,id));
CREATE TABLE answer_keys(question_id TEXT PRIMARY KEY REFERENCES questions(id),key_json TEXT NOT NULL);
CREATE TABLE parts(question_id TEXT NOT NULL REFERENCES questions(id),id TEXT NOT NULL,prompt TEXT NOT NULL,math_latex TEXT,marks REAL NOT NULL,workspace_json TEXT NOT NULL,PRIMARY KEY(question_id,id));
CREATE TABLE calculator_guides(question_id TEXT PRIMARY KEY REFERENCES questions(id),model TEXT,guide_json TEXT NOT NULL);
CREATE TABLE media(id TEXT PRIMARY KEY,path TEXT NOT NULL,sha256 TEXT NOT NULL,metadata_json TEXT NOT NULL);
CREATE TABLE question_media(question_id TEXT NOT NULL REFERENCES questions(id),media_id TEXT NOT NULL REFERENCES media(id),role TEXT NOT NULL,PRIMARY KEY(question_id,media_id));
CREATE INDEX questions_pool ON questions(learning_outcome_id,type,difficulty);
CREATE VIEW student_questions AS SELECT q.id,q.learning_outcome_id,q.type,q.stem,q.math_latex,q.marks FROM questions q;
''')
manifest=[];banks=[];j=lambda x:json.dumps(x,ensure_ascii=False)
for folder in ['9g3-term1','10g3-term1','10a1-term1']:
 base=ROOT/'public/data/exam-banks'/folder;bk=json.loads((base/'index.json').read_text());banks.append(bk);c=bk['classroom'];db.execute('INSERT INTO classrooms VALUES(?,?,?)',(c,9 if c=='9G3' else 10,'advanced' if c=='10A1' else 'general'))
 for o in bk['learning_outcomes']:db.execute('INSERT INTO learning_outcomes VALUES(?,?,?,?,?,?)',(c+':'+o['id'],c,o['id'],o['title'],o['title_ar'],j(o)))
 for aid,a in bk['assets'].items():
  rel=f'assets/{folder}/{a["src"]}';dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/a['src'],dst);sha=hashlib.sha256(dst.read_bytes()).hexdigest();db.execute('INSERT INTO media VALUES(?,?,?,?)',(c+':'+aid,rel,sha,j(a)));manifest.append(dict(path=rel,sha256=sha))
 for q in bk['questions']:
  db.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?,?,?)',(q['id'],c+':'+q['learning_outcome_id'],q['type'],q['source_kind'],q['difficulty'],q['instruction'],q.get('math_latex'),j({k:q[k] for k in ['display_number','graph_workspace','coordinate_workspace','table_after_solving','wide','parent_question_id','reference_kind'] if k in q}),j(q['source']),j(q['skill_tags']),q['marks']))
  for o in q.get('options',[]):db.execute('INSERT INTO options VALUES(?,?,?,?)',(q['id'],o['id'],o['text'],o.get('math_latex')))
  db.execute('INSERT INTO answer_keys VALUES(?,?)',(q['id'],j(q.get('answer') or {p['id']:p['answer'] for p in q['parts']})))
  for p in q.get('parts',[]):db.execute('INSERT INTO parts VALUES(?,?,?,?,?,?)',(q['id'],p['id'],p['prompt'],p.get('math_latex'),p['marks'],j(p['workspace'])))
  g={**q['calculator']}
  if g.get('image'):g['image']=f'assets/{folder}/'+g['image']
  db.execute('INSERT INTO calculator_guides VALUES(?,?,?)',(q['id'],g.get('model'),j(g)))
  for aid in q['diagram_asset_ids']:db.execute('INSERT INTO question_media VALUES(?,?,?)',(q['id'],c+':'+aid,'given'))
  if g.get('image'):
   rel=g['image'];dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/q['calculator']['image'],dst);sha=hashlib.sha256(dst.read_bytes()).hexdigest();mid=q['id']+':calculator';db.execute('INSERT INTO media VALUES(?,?,?,?)',(mid,rel,sha,j(dict(kind='instructional_key_guide',model=g['model']))));db.execute('INSERT INTO question_media VALUES(?,?,?)',(q['id'],mid,'solution_guide'));manifest.append(dict(path=rel,sha256=sha))
for bk in banks:
 folder={'9G3':'9g3-term1','10G3':'10g3-term1','10A1':'10a1-term1'}[bk['classroom']]
 for a in bk['assets'].values():a['src']=f'assets/{folder}/'+a['src']
 for q in bk['questions']:
  if q['calculator'].get('image'):q['calculator']['image']=f'assets/{folder}/'+q['calculator']['image']
assert not db.execute('PRAGMA foreign_key_check').fetchall()
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
db.commit();(OUT/'assessment-bank.sql').write_text('PRAGMA foreign_keys=OFF;\n'+'\n'.join(db.iterdump())+'\nPRAGMA foreign_keys=ON;\n');db.close()
(OUT/'assessment-bank.json').write_text(j(dict(schema_version=2,banks=banks))+'\n');(OUT/'assets-manifest.json').write_text(j(manifest)+'\n')
(OUT/'README.md').write_text('''# Assessment transfer package

SQLite: assessment-bank.sqlite. Equivalent SQL dump and JSON are included. Assets use relative paths with SHA-256 hashes in assets-manifest.json. IDs and LO links are stable. Grade and track are in classrooms; each question belongs to one scoped LO. `source_kind` distinguishes textbook exercises, concept applications and example variants. FRQ keys are multipart rubrics. Calculator diagrams belong to solutions, not given information.

Import SQLite directly, or `sqlite3 imported.sqlite < assessment-bank.sql`. JSON is suitable for other database engines; the SQL dump uses SQLite syntax. Preserve media paths or remap them during upload. Validate foreign keys and hashes after transfer.

For a real exam, keep this package and answer_keys private. Serve student_questions and options during the attempt; grade on the server and release solutions only when permitted. The website's existing hour-long mock is local practice.

Example: one MCQ from each of the 20 MCQ LOs for 9G3:

```sql
WITH pool AS (
 SELECT q.*, ROW_NUMBER() OVER (PARTITION BY q.learning_outcome_id ORDER BY RANDOM()) AS pick
 FROM questions q JOIN learning_outcomes lo ON lo.id=q.learning_outcome_id
 WHERE lo.classroom_id='9G3' AND q.type='mcq'
)
SELECT id,learning_outcome_id,stem,math_latex FROM pool WHERE pick=1;
```

Retrieve option IDs/text separately and shuffle display order while retaining their canonical IDs. Check that exactly 20 different LOs were selected. Timer, attempts and LMS submission are application responsibilities; this package contains question data, not student records.
''')
zip_path=ROOT/'artifacts/assessment-transfer.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(OUT))
print(f'{sum(len(b["questions"]) for b in banks)} questions, {sum(len(b["learning_outcomes"]) for b in banks)} outcomes; SQLite integrity/foreign keys OK; {len(manifest)} media files; {zip_path.stat().st_size/1e6:.1f} MB ZIP')
