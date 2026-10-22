# Forma — EOT Grade 10 General, Week 8 Exam

HTML/CSS/JavaScript + Vite, KaTeX, Vercel Functions and Neon Postgres. Six graphing FRQs include tables, scaled drawing planes and hidden solutions. Four additional graph-reading FRQs include vector graphs, axis/vertex/intercept/domain/range fields and end-behavior selections. Graphs are transcribed assuming one grid square is one unit. Supports image uploads, FRQ/MCQ editing, search and JSON backups.

## Local development

Node.js 22+. Run `npm ci`, `npm run dev`, `npm test`, and `npm run build`. The Vite development server includes the API; `npm run preview` serves only static build files and cannot test the API.

## Connect Neon and deploy to Vercel

1. Create or select a Neon Postgres database (or add Neon through Vercel's Marketplace integration).
2. Set server environment variables in Vercel: `DATABASE_URL` = the Neon connection string with TLS enabled; `ADMIN_TOKEN` = a long random editing key. Never prefix either with `VITE_` or commit their values. For local development, copy `.env.example` to `.env` and enter the values privately. Restart the dev server after configuring.
3. Run `npm run db:migrate` with the database connection configured. This creates `questions` and seeds the 35 bundled questions without overwriting existing data. Run it again safely after schema initialization. It also adds domain and range to exact original graph-reading exercises, preserving custom edits and deleted questions. The browser queues the same upgrade for existing cached originals. Vercel runs the migration automatically before its production build through `npm run build:vercel`; `DATABASE_URL` must be configured for the Production and Preview environments being deployed. Local `npm run build` remains database-independent. It also upgrades exact original questions to bilingual content without replacing teacher edits.
4. Import the Git repository into Vercel using the repository’s `vercel.json` (Vite, build command `npm run build:vercel`, output directory `dist`). The `api/questions.js` function runs on Vercel; redeploy after setting environment variables.
5. Open the app and click **Admin sign-in**, then use the administrator username and password. The opaque session remains in sessionStorage for that tab; sign out on shared devices. Everyone can read the public question bank, including answers. Only signed-in administrators can write; use Admin sign-in with the configured username and password.
6. Confirm **Cloud synced**, then open a second browser/device to verify the question appears. Test create, edit and delete. Live migration and cross-device verification require database credentials in the deployment environment.

## Offline sync and conflicts

Questions save immediately to a versioned localStorage envelope, including pending writes. The app pulls on startup, every 15 seconds while visible, and when connectivity returns; edits trigger a push. Existing local questions migrate into the pending queue. Cloud rows use server revisions and atomic compare-and-swap writes. Deleted rows remain as tombstones to prevent old devices from resurrecting them. Device clocks do not decide which write wins.

Conflicting edits remain local and queued; the cloud record is preserved. Export a JSON backup, then choose **Use cloud version** to discard local pending edits and load server data. You can reapply your intended edits afterward. This reset requires confirmation and a successful cloud read. Imports merge by ID and queue changes. Sync covers the question bank and images, not student responses or temporary drawings. Local storage quota errors retain the previous bank; export backups regularly. Cloud editing requires an active admin session. If the API or connection is unavailable the app stays local and retries, with status shown in the header.

Image uploads: PNG/JPEG/WebP, up to 3 MB, embedded as data URLs. An API question payload is limited to 4 MB; large image collections can exhaust browser storage or make full-bank polling expensive. For a large bank, move images to object storage and paginate reads before scaling.

## Content and backups

`public/data/questions.json` is the bundled starter bank. Once sync initializes, persisted deletions are authoritative and seeds are not re-added. Export/import JSON for portable backups. Question text is escaped safely, with `$...$`, `$$...$$` and `\(...\)` rendered by KaTeX; raw HTML is not executed. Graphing metadata survives question edits and exports.

No live database has been created or verified by this repository alone. `DATABASE_URL` and `ADMIN_TOKEN` must be supplied securely in environment settings, not in chat. In restricted cloud environments, allow HTTPS egress to the exact Neon endpoint hostname from your connection settings; do not publish the connection string.

## Bilingual transformation MCQs

The current bank has 35 questions in 10A1: 7 FRQs and 28 MCQs. 10G3 is empty pending replacement by learning outcome. The following quadratic question descriptions document the retired bank. The eight functions from source items 3–10 each appear twice: four SVG graph options, and four bilingual transformation descriptions. Every MCQ has a validated `correctIndex`; radio selection and Check answer give practice feedback. All eight targets are translations with no reflection or stretch. Distractors include sign errors, incorrect shift axes, reflection and stretching. All graph choices share a unit grid and viewport. English and Arabic prompts, options, and worked answers display together; Arabic text uses RTL while equations stay LTR. Bilingual fields and graph metadata survive JSON export/import and cloud sync. Existing exact starter questions upgrade automatically; custom edits remain intact.

Source items 23–30 add eight bilingual transformation-description MCQs covering vertical stretch/compression, horizontal reciprocal factors, reflection, and combined shifts. Items 24 and 26 explain that reflecting the even parent function across the y-axis has no visible effect; equivalent vertical descriptions appear in the explanation rather than as competing correct choices.

Source equations 5–10 add six bilingual solution-set MCQs. Each has four distinct sets, exactly one complete correct set, factoring steps and checks in the original equation. Distractors include lost zero roots, sign errors and incorrect factors.

Applications 29 and 30 each have two standalone bilingual MCQs: free-fall time and factored ground-level equation; box volume factorization and numerical volume at x=9. Box questions include an inline SVG net/fold diagram with dimensions and bilingual captions. Negative free-fall time is excluded by the physical domain.

Graphs 31–34 each have a standalone bilingual MCQ showing a vector graph with four quadratic-function options. No feature-entry worksheet accompanies these MCQs. Graph 34 uses one unit per x step and two per y step; axis labels and question text state this explicitly.

The previous 48 questions in 10G3 have been removed from the EOT Grade 10 General Week 8 exam. Each question stores the common bilingual exam title plus its original section for topic grouping. Existing exact starter records are upgraded without replacing teacher edits.

## Railway deployment (recommended host)

The app now includes a standalone Node.js production server and a multi-stage Docker build. Railway serves the frontend and `/api/questions` from one service; Neon remains the database. The existing Vercel adapter remains available.

1. In Railway, create a project → Deploy from GitHub repo → `Kamelbshara2/eot2026-2027`, branch `main`.
2. Set service variables `DATABASE_URL` (Neon connection string with TLS) and `ADMIN_TOKEN` (a long private editing key). Vercel variables do not transfer automatically. Do not add these to Git or Docker build arguments.
3. Railway reads `railway.json`: build the Dockerfile, run `npm run db:migrate` before deployment, then `npm start`. Migrations create the schema, seed all 35 questions and update exact starter records while retaining custom edits and deletions. Missing database credentials stop the pre-deploy step.
4. In the service Networking settings, generate a public domain. The server binds `0.0.0.0` and uses Railway's `PORT` automatically. Readiness checks use `/healthz`.
5. Check `/` for the exam app and `/api/questions` for the database rows; enable cloud editing in the browser and verify synchronization from a second browser.

For local production testing, run `npm run build` then `npm start` (default port 3000). Database settings can be loaded privately from `.env`; the static app still loads when the database is unavailable, and sync status reports the failure. A healthy `/healthz` indicates the HTTP process is running; database readiness requires a successful `/api/questions` request.

CLI deployment requires a Railway project token supplied securely as `RAILWAY_TOKEN` in the execution environment. Never enter token values in chat or commit them. No Railway login or project provisioning is implied by these files.

## Classroom portal and student sign-ins

The home screen has cards for 10A1, 10G3 and 9G3. Both 10A1 and 10G3 contain an **8th week exam**; 9G3 currently has no exams. Students enter only their name and school. Grade and classroom come from the selected card. These are self-reported visits, not verified identities or password accounts. Practice opens immediately, even without a backend. Only the teacher uses an administrator account.

The browser tab retains the visit and drafts in sessionStorage across refreshes. **Save answer** queues that answer for upload, including paper attachments. The app attempts to register the visit first, then sends queued answers, retrying on reconnect, focus, every 30 seconds while visible, and subsequent saves. Each visit uses a stable UUID so retries cannot create duplicate visits. The UI distinguishes local pending work from confirmed server saves. Unsynced work is unavailable to the teacher; keep the tab open until it syncs. Closing the tab or signing out clears local access to the work. If browser storage is full or unavailable, saving warns that the answer remains in memory only. This is deliberately tab-scoped to limit personal data retained on shared devices.

`POST /api/student-logins` records an event in Neon only after validation. The server records the timestamp; malformed data, incorrect classroom/grade combinations, and unavailable databases return explicit errors. A failed check-in never counts as a confirmed database record and never prevents local practice.

Run `npm run db:migrate` after this update (Railway pre-deploy and Vercel builds run it automatically) to create the `student_logins` table. `GET /api/student-logins` returns the most recent 100 events only with `Authorization: Bearer <admin-session-token>`; public reads are rejected. Do not publish or commit student records. This feature requires the Node/Vercel API and cannot record visits on GitHub Pages alone.

## GitHub Pages frontend

`.github/workflows/pages.yml` builds and publishes only `dist` from `main`. Before the first deployment, the repository owner must choose **Settings → Pages → Source: GitHub Actions**. The default workflow token cannot create a Pages site. Build and tests run independently; the deploy job checks that Pages is enabled before publishing. GitHub account/repository visibility restrictions still apply. The project path is `/eot2026-2027/`; assets and bundled database requests honor that base path. Classroom and exam links use hashes, so direct exam links work without server rewrites.

Pages cannot execute API code or connect directly to Neon securely. Provide a running Railway/Vercel Node backend. Set repository Actions variable `API_BASE_URL` to its public HTTPS origin, then rerun the Pages workflow. Configure `DATABASE_URL` and `ADMIN_TOKEN` on that backend, run its schema migration, and set backend variable `PUBLIC_APP_ORIGIN=https://kamelbshara2.github.io`. CORS permits that frontend origin, including preflight for JSON sign-in and authenticated editing. Never use database credentials as frontend variables or commit student records.

Without a backend URL, Pages supports classroom selection and local student practice. The visit banner and save status explain that pending visits and answers have not reached the teacher. Database tracking and administrator tools require a working backend. No site publication is established merely by committing this workflow.

## Student practice and administrator roles

Students see one question per slide, can navigate Previous/Next, and use **Save answer** to store the current response. Navigation retains a local draft; only Save answer queues it for the teacher. Neither local saving nor navigation confirms a database save. Responses (MCQ choice, FRQ fields and coordinate-plane strokes) are recorded per signed-in visit and question, with a server timestamp. MCQs are checked against the server's answer key; FRQs are available for teacher review. Student sessions expire after 24 hours; students still need no password or account. Their sign-in UUID is kept in sessionStorage for the tab.

Question creation, editing, deletion and imports require an administrator session. Those controls are hidden in student mode and mutation handlers independently validate a live server session. Admin passwords are stored as salted scrypt hashes in Neon, never in frontend files or Git. A successful username/password login issues a revocable 8-hour opaque session token, held in sessionStorage; the database keeps only its SHA-256 hash. Five failed logins lock the account for 15 minutes. Old editing-key bearer tokens are no longer accepted for question writes or student-record reads.

The admin **Student practice** dashboard shows the latest 100 sign-in visits, saved answer counts, correct MCQ counts, last activity and recorded answers/drawings. Refresh loads current records. Log out on shared devices. Answers belong to individual visits; a new sign-in starts a separate visit.

Run the migration to create `admin_users`, `admin_sessions`, and `practice_responses`. Provision or reset an administrator with `node scripts/set-admin.mjs <username>`, supplying the password privately on stdin; this also revokes existing sessions for that account. No passwords belong in environment examples or repository files. The configured administrator account lives in Neon, so it is shared across backend deployments using that database.

These features still need the separate backend URL when the frontend is hosted on GitHub Pages.

## 10A1 — 8th week exam of EOT

10A1 now has its own 15 bilingual dilation MCQs: five with polygon graph options, five with transformed coordinate options (including C′ in the triangle example), and five requiring a scale factor plus enlargement/reduction classification. Original/image polygons use blue/green consistently; graph options use identical scales per question. Item 12 uses a redrawn logo with exact corresponding dilation vertices. The 10G3 bank is empty and ready for replacement questions; 9G3 has no published exam yet. Questions have explicit classroom and position fields for consistent slide order, regardless of database row order. The practice API rejects saves for another classroom. Dashboard totals follow the selected classroom's bank.

## Learning outcomes and textbook assignments

The administrator's **Learning outcomes** manager lets you choose a classroom, enter English/Arabic outcome titles, textbook pages, target question count and outcome order, select existing questions, and move the selected questions up/down. Assigned versus target counts are shown separately, so incomplete plans can be saved. Each question belongs to at most one outcome. Editing another outcome is required before moving an already assigned question; backend transactions reject stale revisions and cross-classroom assignments. Deleting an outcome unassigns its questions and preserves questions and practice answers.

Students can filter practice slides by outcome, see its book pages, or practise all outcomes in sequence. Questions follow outcome order and then explicit within-outcome order; unassigned questions appear afterward. The admin practice dashboard also reports saved-answer and MCQ-correct counts per outcome.

The bundled `public/data/learning-outcomes.json` seeds three requested 10A1 outcomes without replacing subsequent admin edits: similar polygons, page 128 Q11–14 (4 questions); AA triangle similarity, page 133 Q1–8 (9 questions because Q8A and Q8B are separate); and similar-triangle problem solving, page 139 Q5–11 (7 FRQs). The AA outcome includes a generated polished lighthouse illustration shared by its two independent questions. Original dilation questions remain unassigned until the administrator provides their outcome. 10A1 currently has 35 questions; 10G3 has been cleared for replacement questions by learning outcome. The server migrations create `learning_outcomes` and `outcome_questions`; the API is `/api/learning-outcomes`, with public reads and admin-only writes. GitHub Pages still requires a configured separate backend for live changes and practice tracking.

## Page 139 FRQs and paper answers

The third 10A1 outcome, **Using similar triangles to solve problems (FRQ)**, contains page 139 Q5–11 as seven separate bilingual FRQs with diagrams and marking guides. Students may type their working or attach one PNG/JPEG/WebP photo or PDF per question, up to 2 MB. Uploading a file only selects it; **Save answer** confirms persistence in Neon. Re-uploading replaces the file; saving other edits preserves the existing upload. All FRQ questions support this option.

`practice_uploads` stores file bytes separately from response metadata. Practice lists and the teacher dashboard receive metadata, not every file's binary data. `/api/practice-paper` serves authenticated downloads to the student owning the visit or a signed-in administrator; other students and anonymous visitors are rejected. The teacher dashboard shows a paper-answer download button. Server-side validation checks file size, declared MIME and file signatures and rejects HTML/SVG uploads. FRQ paper answers remain for teacher review, without automatic grades. No student uploads are stored in the public Git repository or Pages assets.

The previous 48 questions in 10G3 were retired at the teacher's request. The 10G3 exam card remains empty for new outcome-based content; all 35 questions in 10A1 remain unchanged. `lib/retired-questions.json` removes those specific IDs from existing browser caches and pending writes. Schema migration tombstones the same IDs in Neon and removes their outcome assignments, preserving historical student responses. New 10G3 questions with new IDs are unaffected.
