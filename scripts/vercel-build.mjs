// Vercel build: migrate the database, then build the site.
// The study booklets are static files, so a database outage (for example a Neon quota limit,
// HTTP 402) must not stop the site from deploying. The migration is idempotent and runs again
// on the next deployment. Set MIGRATE_STRICT=1 to make a failed migration fail the build.
import {spawnSync} from 'node:child_process';

const run = (script) => spawnSync('npm', ['run', script], {stdio: 'inherit', shell: process.platform === 'win32'}).status;

if (run('db:migrate') !== 0) {
  if (process.env.MIGRATE_STRICT === '1') process.exit(1);
  console.warn('\nWARNING: database migration did not complete (see the error above).');
  console.warn('The site is still built and deployed; sign-in sync, saved answers and the teacher');
  console.warn('dashboard stay unavailable until the database is reachable. Redeploy afterwards.\n');
}
process.exit(run('build') ?? 1);
