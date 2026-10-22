# Forma — EOT Grade 10 General, Week 8 Exam

HTML/CSS/JavaScript + Vite, KaTeX, Vercel Functions and Neon Postgres. Six graphing FRQs include tables, scaled drawing planes and hidden solutions. Four additional graph-reading FRQs include vector graphs, axis/vertex/intercept/domain/range fields and end-behavior selections. Graphs are transcribed assuming one grid square is one unit. Supports image uploads, FRQ/MCQ editing, search and JSON backups.

## Local development

Node.js 22+. Run `npm ci`, `npm run dev`, `npm test`, and `npm run build`. The Vite development server includes the API; `npm run preview` serves only static build files and cannot test the API.

## Connect Neon and deploy to Vercel

1. Create or select a Neon Postgres database (or add Neon through Vercel's Marketplace integration).
2. Set server environment variables in Vercel: `DATABASE_URL` = the Neon connection string with TLS enabled; `ADMIN_TOKEN` = a long random editing key. Never prefix either with `VITE_` or commit their values. For local development, copy `.env.example` to `.env` and enter the values privately. Restart the dev server after configuring.
3. Run `npm run db:migrate` with the database connection configured. This creates `questions` and seeds the 48 bundled questions without overwriting existing data. Run it again safely after schema initialization. It also adds domain and range to exact original graph-reading exercises, preserving custom edits and deleted questions. The browser queues the same upgrade for existing cached originals. Vercel runs the migration automatically before its production build through `npm run build:vercel`; `DATABASE_URL` must be configured for the Production and Preview environments being deployed. Local `npm run build` remains database-independent. It also upgrades exact original questions to bilingual content without replacing teacher edits.
4. Import the Git repository into Vercel using the repository’s `vercel.json` (Vite, build command `npm run build:vercel`, output directory `dist`). The `api/questions.js` function runs on Vercel; redeploy after setting environment variables.
5. Open the app and click **Enable cloud editing**, then enter the editing key. The key remains in sessionStorage for that tab; use a trusted device and close the tab to end the session. Everyone can read the public question bank, including answers. Only key holders can write. This is a single-owner editing key, not per-user accounts.
6. Confirm **Cloud synced**, then open a second browser/device to verify the question appears. Test create, edit and delete. Live migration and cross-device verification require database credentials in the deployment environment.

## Offline sync and conflicts

Questions save immediately to a versioned localStorage envelope, including pending writes. The app pulls on startup, every 15 seconds while visible, and when connectivity returns; edits trigger a push. Existing local questions migrate into the pending queue. Cloud rows use server revisions and atomic compare-and-swap writes. Deleted rows remain as tombstones to prevent old devices from resurrecting them. Device clocks do not decide which write wins.

Conflicting edits remain local and queued; the cloud record is preserved. Export a JSON backup, then choose **Use cloud version** to discard local pending edits and load server data. You can reapply your intended edits afterward. This reset requires confirmation and a successful cloud read. Imports merge by ID and queue changes. Sync covers the question bank and images, not student responses or temporary drawings. Local storage quota errors retain the previous bank; export backups regularly. Cloud editing requires an active editing key. If the API or connection is unavailable the app stays local and retries, with status shown in the header.

Image uploads: PNG/JPEG/WebP, up to 3 MB, embedded as data URLs. An API question payload is limited to 4 MB; large image collections can exhaust browser storage or make full-bank polling expensive. For a large bank, move images to object storage and paginate reads before scaling.

## Content and backups

`public/data/questions.json` is the bundled starter bank. Once sync initializes, persisted deletions are authoritative and seeds are not re-added. Export/import JSON for portable backups. Question text is escaped safely, with `$...$`, `$$...$$` and `\(...\)` rendered by KaTeX; raw HTML is not executed. Graphing metadata survives question edits and exports.

No live database has been created or verified by this repository alone. `DATABASE_URL` and `ADMIN_TOKEN` must be supplied securely in environment settings, not in chat. In restricted cloud environments, allow HTTPS egress to the exact Neon endpoint hostname from your connection settings; do not publish the connection string.

## Bilingual transformation MCQs

The bank now has 48 questions: 10 FRQs and 38 MCQs. The eight functions from source items 3–10 each appear twice: four SVG graph options, and four bilingual transformation descriptions. Every MCQ has a validated `correctIndex`; radio selection and Check answer give practice feedback. All eight targets are translations with no reflection or stretch. Distractors include sign errors, incorrect shift axes, reflection and stretching. All graph choices share a unit grid and viewport. English and Arabic prompts, options, and worked answers display together; Arabic text uses RTL while equations stay LTR. Bilingual fields and graph metadata survive JSON export/import and cloud sync. Existing exact starter questions upgrade automatically; custom edits remain intact.

Source items 23–30 add eight bilingual transformation-description MCQs covering vertical stretch/compression, horizontal reciprocal factors, reflection, and combined shifts. Items 24 and 26 explain that reflecting the even parent function across the y-axis has no visible effect; equivalent vertical descriptions appear in the explanation rather than as competing correct choices.

Source equations 5–10 add six bilingual solution-set MCQs. Each has four distinct sets, exactly one complete correct set, factoring steps and checks in the original equation. Distractors include lost zero roots, sign errors and incorrect factors.

Applications 29 and 30 each have two standalone bilingual MCQs: free-fall time and factored ground-level equation; box volume factorization and numerical volume at x=9. Box questions include an inline SVG net/fold diagram with dimensions and bilingual captions. Negative free-fall time is excluded by the physical domain.

Graphs 31–34 each have a standalone bilingual MCQ showing a vector graph with four quadratic-function options. No feature-entry worksheet accompanies these MCQs. Graph 34 uses one unit per x step and two per y step; axis labels and question text state this explicitly.

All 48 questions belong to the EOT Grade 10 General Week 8 exam. Each question stores the common bilingual exam title plus its original section for topic grouping. Existing exact starter records are upgraded without replacing teacher edits.

## Railway deployment (recommended host)

The app now includes a standalone Node.js production server and a multi-stage Docker build. Railway serves the frontend and `/api/questions` from one service; Neon remains the database. The existing Vercel adapter remains available.

1. In Railway, create a project → Deploy from GitHub repo → `Kamelbshara2/eot2026-2027`, branch `main`.
2. Set service variables `DATABASE_URL` (Neon connection string with TLS) and `ADMIN_TOKEN` (a long private editing key). Vercel variables do not transfer automatically. Do not add these to Git or Docker build arguments.
3. Railway reads `railway.json`: build the Dockerfile, run `npm run db:migrate` before deployment, then `npm start`. Migrations create the schema, seed all 48 questions and update exact starter records while retaining custom edits and deletions. Missing database credentials stop the pre-deploy step.
4. In the service Networking settings, generate a public domain. The server binds `0.0.0.0` and uses Railway's `PORT` automatically. Readiness checks use `/healthz`.
5. Check `/` for the exam app and `/api/questions` for the database rows; enable cloud editing in the browser and verify synchronization from a second browser.

For local production testing, run `npm run build` then `npm start` (default port 3000). Database settings can be loaded privately from `.env`; the static app still loads when the database is unavailable, and sync status reports the failure. A healthy `/healthz` indicates the HTTP process is running; database readiness requires a successful `/api/questions` request.

CLI deployment requires a Railway project token supplied securely as `RAILWAY_TOKEN` in the execution environment. Never enter token values in chat or commit them. No Railway login or project provisioning is implied by these files.

## Classroom portal and student sign-ins

The home screen has cards for 10A1, 10G3 and 9G3. 10G3 contains the **8th week exam** card linking to `#/classrooms/10G3/exams/week-8`. The other classrooms show an empty-exam state. Name, school and grade are required before entering the exam; classroom is taken from the selected card. These are self-reported check-ins, not verified student identities or password accounts. A tab remembers a confirmed sign-in until sign-out or closing the tab.

`POST /api/student-logins` records an event in Neon only after validation. Each request carries a UUID, making retries idempotent and preventing duplicate events after an uncertain connection. The server records the timestamp; malformed data, incorrect classroom/grade combinations, and unavailable databases return explicit errors. Students cannot enter through the normal portal until their database write is confirmed. Names and schools are not queued in localStorage and failed requests do not pretend to be successful.

Run `npm run db:migrate` after this update (Railway pre-deploy and Vercel builds run it automatically) to create the `student_logins` table. `GET /api/student-logins` returns the most recent 100 events only with `Authorization: Bearer <ADMIN_TOKEN>`; public reads are rejected. Do not publish or commit student records. This feature requires the Node/Vercel API and cannot record visits on GitHub Pages alone.

## GitHub Pages frontend

`.github/workflows/pages.yml` builds and publishes only `dist` from `main`. Before the first deployment, the repository owner must choose **Settings → Pages → Source: GitHub Actions**. The default workflow token cannot create a Pages site. Build and tests run independently; the deploy job checks that Pages is enabled before publishing. GitHub account/repository visibility restrictions still apply. The project path is `/eot2026-2027/`; assets and bundled database requests honor that base path. Classroom and exam links use hashes, so direct exam links work without server rewrites.

Pages cannot execute API code or connect directly to Neon securely. Provide a running Railway/Vercel Node backend. Set repository Actions variable `API_BASE_URL` to its public HTTPS origin, then rerun the Pages workflow. Configure `DATABASE_URL` and `ADMIN_TOKEN` on that backend, run its schema migration, and set backend variable `PUBLIC_APP_ORIGIN=https://kamelbshara2.github.io`. CORS permits that frontend origin, including preflight for JSON sign-in and authenticated editing. Never use database credentials as frontend variables or commit student records.

Without a backend URL, Pages still shows classroom cards, but student sign-ins clearly report that the backend is not connected and do not claim to record visits. Database sign-in remains required before practice; this is not a practice-only deployment. No site publication is established merely by committing this workflow.
