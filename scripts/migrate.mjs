import { neon } from '@neondatabase/serverless';
import { readFile } from 'node:fs/promises';
if(!process.env.DATABASE_URL)throw Error('Set DATABASE_URL securely before running migration.');
const sql=neon(process.env.DATABASE_URL);
await sql`CREATE TABLE IF NOT EXISTS questions (id text PRIMARY KEY, data jsonb, revision integer NOT NULL DEFAULT 1 CHECK (revision>0), deleted boolean NOT NULL DEFAULT false, updated_at timestamptz NOT NULL DEFAULT now())`;
await sql`CREATE TABLE IF NOT EXISTS student_logins (id uuid PRIMARY KEY,name text NOT NULL CHECK (char_length(name) BETWEEN 2 AND 100),school text NOT NULL CHECK (char_length(school) BETWEEN 2 AND 150),grade smallint NOT NULL,classroom text NOT NULL,created_at timestamptz NOT NULL DEFAULT now(),CHECK ((classroom IN ('10A1','10G3') AND grade=10) OR (classroom='9G3' AND grade=9)))`;
await sql`CREATE INDEX IF NOT EXISTS student_logins_recent ON student_logins(created_at DESC)`;
await sql`CREATE TABLE IF NOT EXISTS admin_users (username text PRIMARY KEY,password_hash text NOT NULL,failed_attempts integer NOT NULL DEFAULT 0,locked_until timestamptz)`;
await sql`CREATE TABLE IF NOT EXISTS admin_sessions (token_hash text PRIMARY KEY,username text NOT NULL REFERENCES admin_users(username) ON DELETE CASCADE,expires_at timestamptz NOT NULL)`;
await sql`CREATE TABLE IF NOT EXISTS practice_responses (login_id uuid NOT NULL REFERENCES student_logins(id) ON DELETE CASCADE,question_id text NOT NULL REFERENCES questions(id),response jsonb NOT NULL,correct boolean,updated_at timestamptz NOT NULL DEFAULT now(),PRIMARY KEY(login_id,question_id))`;
await sql`CREATE TABLE IF NOT EXISTS learning_outcomes (id uuid PRIMARY KEY,classroom text NOT NULL CHECK(classroom IN ('10A1','10G3','9G3')),title text NOT NULL,title_ar text NOT NULL DEFAULT '',book_pages text NOT NULL DEFAULT '',target_count integer NOT NULL CHECK(target_count BETWEEN 1 AND 500),position integer NOT NULL CHECK(position BETWEEN 1 AND 1000),revision integer NOT NULL DEFAULT 1,deleted boolean NOT NULL DEFAULT false,last_operation uuid)`;
await sql`ALTER TABLE learning_outcomes ADD COLUMN IF NOT EXISTS exam_week integer NOT NULL DEFAULT 8 CHECK(exam_week BETWEEN 1 AND 52)`;
await sql`ALTER TABLE learning_outcomes ADD COLUMN IF NOT EXISTS assessment_item text NOT NULL DEFAULT ''`;
await sql`CREATE TABLE IF NOT EXISTS outcome_questions (question_id text PRIMARY KEY REFERENCES questions(id),outcome_id uuid NOT NULL REFERENCES learning_outcomes(id),position integer NOT NULL CHECK(position>0))`;
await sql`CREATE TABLE IF NOT EXISTS practice_uploads (login_id uuid NOT NULL,question_id text NOT NULL,name text NOT NULL,mime text NOT NULL,size integer NOT NULL CHECK(size BETWEEN 1 AND 2097152),content bytea NOT NULL,PRIMARY KEY(login_id,question_id),FOREIGN KEY(login_id,question_id) REFERENCES practice_responses(login_id,question_id) ON DELETE CASCADE)`;
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url),'utf8'));
await sql.transaction(bank.questions.map(q=>sql`INSERT INTO questions(id,data) VALUES(${q.id},${JSON.stringify(q)}::jsonb) ON CONFLICT(id) DO NOTHING`));
// Retire only the old 10G3 IDs; future questions added by outcome remain untouched.
const retired=JSON.parse(await readFile(new URL('../lib/retired-questions.json',import.meta.url),'utf8'));
await sql.transaction([
 sql`DELETE FROM outcome_questions WHERE question_id = ANY(${retired}::text[])`,
 sql`UPDATE questions SET data=NULL,deleted=true,revision=revision+1,updated_at=now() WHERE id = ANY(${retired}::text[]) AND NOT deleted`
]);
const updates=JSON.parse(await readFile(new URL('../lib/content-updates.json',import.meta.url),'utf8'));
await sql.transaction(updates.map(u=>sql`UPDATE questions SET data=${JSON.stringify(u.after)}::jsonb,revision=revision+1,updated_at=now() WHERE id=${u.before.id} AND NOT deleted AND data=${JSON.stringify(u.before)}::jsonb`));
const outcomeSeed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url),'utf8'));
for(const o of outcomeSeed.outcomes){const links=outcomeSeed.assignments.filter(a=>a.outcome_id===o.id);await sql.transaction([sql`SELECT pg_advisory_xact_lock(hashtext(${o.classroom}))`,sql`INSERT INTO learning_outcomes(id,classroom,exam_week,assessment_item,title,title_ar,book_pages,target_count,position,last_operation) VALUES(${o.id}::uuid,${o.classroom},${o.examWeek??8},${o.assessmentItem||''},${o.title},${o.titleAr},${o.bookPages},${o.targetCount},${o.position},${o.id}::uuid) ON CONFLICT(id) DO NOTHING`,...links.map(a=>sql`INSERT INTO outcome_questions(question_id,outcome_id,position) SELECT ${a.question_id},${o.id}::uuid,${a.position} WHERE EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${o.id}::uuid AND revision=1 AND NOT deleted AND last_operation=${o.id}::uuid) ON CONFLICT(question_id) DO NOTHING`)]);}
console.log('Schema ready; bundled questions seeded without overwriting existing questions.');
