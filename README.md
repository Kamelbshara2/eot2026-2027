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
