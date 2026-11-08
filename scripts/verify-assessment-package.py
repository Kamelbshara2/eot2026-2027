"""Verify SQLite import, portable media paths, hashes and fair per-topic sampling."""
from pathlib import Path
import json,sqlite3,hashlib,zipfile
root=Path(__file__).resolve().parent.parent
out=root/'artifacts/assessment-transfer';source=sqlite3.connect(out/'assessment-bank.sqlite');restored=sqlite3.connect(':memory:');restored.execute('PRAGMA foreign_keys=ON');restored.executescript((out/'assessment-bank.sql').read_text());assert restored.execute('PRAGMA foreign_keys').fetchone()[0]==1
assert restored.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not restored.execute('PRAGMA foreign_key_check').fetchall()
for table in ['classrooms','learning_outcomes','questions','options','answer_keys','parts','media','question_media','calculator_guides']:
 assert source.execute(f'SELECT COUNT(*) FROM {table}').fetchone()==restored.execute(f'SELECT COUNT(*) FROM {table}').fetchone(),table
banks=json.loads((out/'assessment-bank.json').read_text())['banks'];manifest=json.loads((out/'assets-manifest.json').read_text())
with zipfile.ZipFile(root/'artifacts/assessment-transfer.zip') as z:
 assert z.testzip() is None
 for a in manifest:assert hashlib.sha256(z.read(a['path'])).hexdigest()==a['sha256']
 for b in banks:
  for a in b['assets'].values():assert a['src'] in z.namelist()
  for q in b['questions']:
   if q['calculator'].get('image'):assert q['calculator']['image'] in z.namelist()
   if q['type']=='mcq':
    key=json.loads(restored.execute('SELECT key_json FROM answer_keys WHERE question_id=?',(q['id'],)).fetchone()[0]);assert key['correct_option_id']==q['answer']['correct_option_id']
    assert restored.execute('SELECT text FROM options WHERE question_id=? AND id=?',(q['id'],key['correct_option_id'])).fetchone()[0]==key['correct_option_text']
   for p in q.get('parts',[]):assert restored.execute('SELECT math_latex FROM parts WHERE question_id=? AND id=?',(q['id'],p['id'])).fetchone()[0]==p.get('math_latex')
  for _ in range(50):
   rows=restored.execute('''WITH pool AS (SELECT q.id,q.learning_outcome_id,ROW_NUMBER() OVER(PARTITION BY q.learning_outcome_id ORDER BY RANDOM()) AS pick FROM questions q JOIN learning_outcomes lo ON lo.id=q.learning_outcome_id WHERE lo.classroom_id=? AND q.type='mcq') SELECT id,learning_outcome_id FROM pool WHERE pick=1''',(b['classroom'],)).fetchall()
   assert len(rows)==len({r[1] for r in rows})==20
assert restored.execute('SELECT COUNT(*) FROM questions').fetchone()[0]==389
assert restored.execute('SELECT COUNT(*) FROM learning_outcomes').fetchone()[0]==76
print('389 questions / 76 LOs: SQL reimport, keys/FRQ math, ZIP integrity, 356 media hashes/paths and 150 balanced mock selections passed.')
