import {readFile,writeFile} from 'node:fs/promises';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
const qs=bank.questions.filter(q=>q.classroom==='9G3'&&q.examWeek===9),ids=new Set(qs.map(q=>q.id)),links=seed.assignments.filter(a=>ids.has(a.question_id)),outcomes=seed.outcomes.filter(o=>o.classroom==='9G3'&&o.examWeek===9);
if(qs.length!==19||links.length!==19||outcomes.length!==3)throw Error('Incomplete Week 9 data');
const str=s=>`'${String(s).replaceAll("'","''")}'`,json=q=>{const s=JSON.stringify(q);if(s.includes('$question_json$'))throw Error('Unsafe delimiter');return `$question_json$${s}$question_json$::jsonb`};
const updates=JSON.parse(await readFile(new URL('../lib/content-updates.json',import.meta.url))).filter(u=>ids.has(u.before.id)&&u.before.type==='FRQ'&&u.after.type==='MCQ');
const upgrades=updates.map(u=>`UPDATE questions SET data=${json(u.after)},revision=revision+1,updated_at=now() WHERE id=${str(u.before.id)} AND NOT deleted AND data=${json(u.before)};`).join('\n');
const tuples=links.map(a=>`(${str(a.question_id)},${str(a.outcome_id)}::uuid,${a.position})`).join(',\n');
const sql=`-- Grade 9 General / Week 9: 19 MCQs, routed 8 + 9 + 2.
-- Run this complete script in the connected Neon SQL Editor.
-- Existing question edits, deletions, assignments, and all Week 8 data are preserved.
BEGIN;
CREATE TABLE IF NOT EXISTS questions(id text PRIMARY KEY,data jsonb,revision integer NOT NULL DEFAULT 1 CHECK(revision>0),deleted boolean NOT NULL DEFAULT false,updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS learning_outcomes(id uuid PRIMARY KEY,classroom text NOT NULL,title text NOT NULL,title_ar text NOT NULL DEFAULT '',book_pages text NOT NULL DEFAULT '',target_count integer NOT NULL CHECK(target_count BETWEEN 1 AND 500),position integer NOT NULL CHECK(position BETWEEN 1 AND 1000),revision integer NOT NULL DEFAULT 1,deleted boolean NOT NULL DEFAULT false,last_operation uuid);
ALTER TABLE learning_outcomes ADD COLUMN IF NOT EXISTS exam_week integer NOT NULL DEFAULT 8 CHECK(exam_week BETWEEN 1 AND 52);
ALTER TABLE learning_outcomes ADD COLUMN IF NOT EXISTS assessment_item text NOT NULL DEFAULT '';
CREATE TABLE IF NOT EXISTS outcome_questions(question_id text PRIMARY KEY REFERENCES questions(id),outcome_id uuid NOT NULL REFERENCES learning_outcomes(id),position integer NOT NULL CHECK(position>0));
INSERT INTO learning_outcomes(id,classroom,exam_week,assessment_item,title,title_ar,book_pages,target_count,position,last_operation) VALUES
${outcomes.map(o=>`(${str(o.id)}::uuid,'9G3',9,${str(o.assessmentItem)},${str(o.title)},${str(o.titleAr)},${str(o.bookPages)},${o.targetCount},${o.position},${str(o.id)}::uuid)`).join(',\n')}
ON CONFLICT(id) DO NOTHING;
UPDATE learning_outcomes SET target_count=9,revision=revision+1 WHERE id='770b7721-da86-40cd-95ba-930cc84aa47c'::uuid AND revision=1 AND last_operation=id AND target_count=3 AND NOT deleted;
UPDATE learning_outcomes SET target_count=2,revision=revision+1 WHERE id='4976444a-a131-47e4-8dfd-3a9aee82b2d8'::uuid AND revision=1 AND last_operation=id AND target_count=1 AND NOT deleted;
${upgrades}
INSERT INTO questions(id,data) VALUES
${qs.map(q=>`(${str(q.id)},${json(q)})`).join(',\n')}
ON CONFLICT(id) DO NOTHING;
INSERT INTO outcome_questions(question_id,outcome_id,position)
SELECT v.question_id,v.outcome_id,v.position FROM (VALUES
${tuples}
) AS v(question_id,outcome_id,position)
JOIN questions q ON q.id=v.question_id AND NOT q.deleted AND q.data->>'classroom'='9G3' AND q.data->>'examWeek'='9'
JOIN learning_outcomes o ON o.id=v.outcome_id AND NOT o.deleted AND o.classroom='9G3' AND o.exam_week=9
ON CONFLICT(question_id) DO NOTHING;
DO $verify$
BEGIN
 IF (SELECT count(*) FROM (VALUES
${tuples}
 ) AS expected(question_id,outcome_id,position)
 JOIN questions q ON q.id=expected.question_id AND NOT q.deleted AND q.data->>'classroom'='9G3' AND q.data->>'examWeek'='9'
 JOIN outcome_questions a ON a.question_id=expected.question_id AND a.outcome_id=expected.outcome_id
 JOIN learning_outcomes o ON o.id=a.outcome_id AND NOT o.deleted AND o.classroom='9G3' AND o.exam_week=9) <> 19 THEN
  RAISE EXCEPTION 'Import stopped: a question or outcome is deleted, belongs elsewhere, or has a conflicting assignment. No existing data has been overwritten; review the conflicts.';
 END IF;
END $verify$;
SELECT o.assessment_item,o.book_pages,count(a.question_id)::integer AS saved_questions
FROM learning_outcomes o JOIN outcome_questions a ON a.outcome_id=o.id
JOIN questions q ON q.id=a.question_id AND NOT q.deleted
WHERE o.id IN (${outcomes.map(o=>str(o.id)+'::uuid').join(',')})
GROUP BY o.assessment_item,o.book_pages,o.position ORDER BY o.position;
COMMIT;
`;
await writeFile(new URL('../public/data/week9-9g3-neon-import.sql',import.meta.url),sql);
console.log('Prepared transaction-safe Neon import: 19 questions with exact outcome routing; conflicts cause rollback.');
