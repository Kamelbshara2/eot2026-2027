# Forma — EOT Grade 10 General, Week 8 Exam

HTML/CSS/JavaScript + Vite, KaTeX, Vercel Functions and Neon Postgres. Six graphing FRQs include tables, scaled drawing planes and hidden solutions. Four additional graph-reading FRQs include vector graphs, axis/vertex/intercept/domain/range fields and end-behavior selections. Graphs are transcribed assuming one grid square is one unit. Supports image uploads, FRQ/MCQ editing, search and JSON backups.

## Local development

Node.js 22+. Run `npm ci`, `npm run dev`, `npm test`, and `npm run build`. The Vite development server includes the API; `npm run preview` serves only static build files and cannot test the API.

## Connect Neon and deploy to Vercel

1. Create or select a Neon Postgres database (or add Neon through Vercel's Marketplace integration).
2. Set server environment variables in Vercel: `DATABASE_URL` = the Neon connection string with TLS enabled; `ADMIN_TOKEN` = a long random editing key. Never prefix either with `VITE_` or commit their values. For local development, copy `.env.example` to `.env` and enter the values privately. Restart the dev server after configuring.
3. Run `npm run db:migrate` with the database connection configured. This creates `questions` and seeds the 108 bundled questions without overwriting existing data. Run it again safely after schema initialization. It also adds domain and range to exact original graph-reading exercises, preserving custom edits and deleted questions. The browser queues the same upgrade for existing cached originals. Vercel runs the migration automatically before its production build through `npm run build:vercel`; `DATABASE_URL` must be configured for the Production and Preview environments being deployed. Local `npm run build` remains database-independent. It also upgrades exact original questions to bilingual content without replacing teacher edits.
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

The current bank has 108 questions: 35 in 10A1 (7 FRQs and 28 MCQs), 48 in 10G3 (10 FRQs and 38 MCQs), and 25 in 9G3 (8 FRQs and 17 MCQs). The following quadratic question descriptions document the retired bank. The eight functions from source items 3–10 each appear twice: four SVG graph options, and four bilingual transformation descriptions. Every MCQ has a validated `correctIndex`; radio selection and Check answer give practice feedback. All eight targets are translations with no reflection or stretch. Distractors include sign errors, incorrect shift axes, reflection and stretching. All graph choices share a unit grid and viewport. English and Arabic prompts, options, and worked answers display together; Arabic text uses RTL while equations stay LTR. Bilingual fields and graph metadata survive JSON export/import and cloud sync. Existing exact starter questions upgrade automatically; custom edits remain intact.

Source items 23–30 add eight bilingual transformation-description MCQs covering vertical stretch/compression, horizontal reciprocal factors, reflection, and combined shifts. Items 24 and 26 explain that reflecting the even parent function across the y-axis has no visible effect; equivalent vertical descriptions appear in the explanation rather than as competing correct choices.

Source equations 5–10 add six bilingual solution-set MCQs. Each has four distinct sets, exactly one complete correct set, factoring steps and checks in the original equation. Distractors include lost zero roots, sign errors and incorrect factors.

Applications 29 and 30 each have two standalone bilingual MCQs: free-fall time and factored ground-level equation; box volume factorization and numerical volume at x=9. Box questions include an inline SVG net/fold diagram with dimensions and bilingual captions. Negative free-fall time is excluded by the physical domain.

Graphs 31–34 each have a standalone bilingual MCQ showing a vector graph with four quadratic-function options. No feature-entry worksheet accompanies these MCQs. Graph 34 uses one unit per x step and two per y step; axis labels and question text state this explicitly.

The previous 48 questions in 10G3 have been removed from the EOT Grade 10 General Week 8 exam. Each question stores the common bilingual exam title plus its original section for topic grouping. Existing exact starter records are upgraded without replacing teacher edits.

## Railway deployment (recommended host)

The app now includes a standalone Node.js production server and a multi-stage Docker build. Railway serves the frontend and `/api/questions` from one service; Neon remains the database. The existing Vercel adapter remains available.

1. In Railway, create a project → Deploy from GitHub repo → `Kamelbshara2/eot2026-2027`, branch `main`.
2. Set service variables `DATABASE_URL` (Neon connection string with TLS) and `ADMIN_TOKEN` (a long private editing key). Vercel variables do not transfer automatically. Do not add these to Git or Docker build arguments.
3. Railway reads `railway.json`: build the Dockerfile, run `npm run db:migrate` before deployment, then `npm start`. Migrations create the schema, seed all 108 questions and update exact starter records while retaining custom edits and deletions. Missing database credentials stop the pre-deploy step.
4. In the service Networking settings, generate a public domain. The server binds `0.0.0.0` and uses Railway's `PORT` automatically. Readiness checks use `/healthz`.
5. Check `/` for the exam app and `/api/questions` for the database rows; enable cloud editing in the browser and verify synchronization from a second browser.

For local production testing, run `npm run build` then `npm start` (default port 3000). Database settings can be loaded privately from `.env`; the static app still loads when the database is unavailable, and sync status reports the failure. A healthy `/healthz` indicates the HTTP process is running; database readiness requires a successful `/api/questions` request.

CLI deployment requires a Railway project token supplied securely as `RAILWAY_TOKEN` in the execution environment. Never enter token values in chat or commit them. No Railway login or project provisioning is implied by these files.

## Classroom portal and student sign-ins

The home screen has cards for 10A1, 10G3 and 9G3. Each classroom contains an **8th week exam** with its own question bank and learning outcomes. Students enter only their name and school. Grade and classroom come from the selected card. These are self-reported visits, not verified identities or password accounts. Practice opens immediately, even without a backend. Only the teacher uses an administrator account.

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

10A1 now has its own 15 bilingual dilation MCQs: five with polygon graph options, five with transformed coordinate options (including C′ in the triangle example), and five requiring a scale factor plus enlargement/reduction classification. Original/image polygons use blue/green consistently; graph options use identical scales per question. Item 12 uses a redrawn logo with exact corresponding dilation vertices. The 10G3 bank contains 38 quadratic MCQs and 10 quadratic FRQs; 9G3 has its own published Week 8 exam. Questions have explicit classroom and position fields for consistent slide order, regardless of database row order. The practice API rejects saves for another classroom. Dashboard totals follow the selected classroom's bank.

## Learning outcomes and textbook assignments

The administrator's **Learning outcomes** manager lets you choose a classroom, enter English/Arabic outcome titles, textbook pages, target question count and outcome order, select existing questions, and move the selected questions up/down. Assigned versus target counts are shown separately, so incomplete plans can be saved. Each question belongs to at most one outcome. Editing another outcome is required before moving an already assigned question; backend transactions reject stale revisions and cross-classroom assignments. Deleting an outcome unassigns its questions and preserves questions and practice answers.

Students can filter practice slides by outcome, see its book pages, or practise all outcomes in sequence. Questions follow outcome order and then explicit within-outcome order; unassigned questions appear afterward. The admin practice dashboard also reports saved-answer and MCQ-correct counts per outcome.

The bundled `public/data/learning-outcomes.json` seeds twelve outcomes, including three requested 10A1 outcomes without replacing subsequent admin edits: similar polygons, page 128 Q11–14 (4 questions); AA triangle similarity, page 133 Q1–8 (9 questions because Q8A and Q8B are separate); and similar-triangle problem solving, page 139 Q5–11 (7 FRQs). The AA outcome includes a generated polished lighthouse illustration shared by its two independent questions. Original dilation questions remain unassigned until the administrator provides their outcome. 10A1 currently has 35 questions; 10G3 now has 38 quadratic MCQs and 10 FRQs organized into five learning outcomes. The server migrations create `learning_outcomes` and `outcome_questions`; the API is `/api/learning-outcomes`, with public reads and admin-only writes. GitHub Pages still requires a configured separate backend for live changes and practice tracking.

## Page 139 FRQs and paper answers

The third 10A1 outcome, **Using similar triangles to solve problems (FRQ)**, contains page 139 Q5–11 as seven separate bilingual FRQs with diagrams and marking guides. Students may type their working or attach one PNG/JPEG/WebP photo or PDF per question, up to 2 MB. Uploading a file only selects it; **Save answer** confirms persistence in Neon. Re-uploading replaces the file; saving other edits preserves the existing upload. All FRQ questions support this option.

`practice_uploads` stores file bytes separately from response metadata. Practice lists and the teacher dashboard receive metadata, not every file's binary data. `/api/practice-paper` serves authenticated downloads to the student owning the visit or a signed-in administrator; other students and anonymous visitors are rejected. The teacher dashboard shows a paper-answer download button. Server-side validation checks file size, declared MIME and file signatures and rejects HTML/SVG uploads. FRQ paper answers remain for teacher review, without automatic grades. No student uploads are stored in the public Git repository or Pages assets.

The previous 48 questions in 10G3 were retired at the teacher's request. The 10G3 exam card now contains the new outcome-based quadratic questions; all 35 questions in 10A1 remain unchanged. `lib/retired-questions.json` removes those specific IDs from existing browser caches and pending writes. Schema migration tombstones the same IDs in Neon and removes their outcome assignments, preserving historical student responses. New 10G3 questions with new IDs are unaffected.


### Student question workspace

Practice now uses a responsive question card with a learning-outcome navigator, direct numbered question links, answered indicators, and a next-unanswered shortcut. The mobile question navigator starts collapsed, keeping the question in view. Previous, Save answer and Next remain available at the bottom of the viewport while reading. Alt+Left/Right changes questions outside inputs and dialogs. The current outcome filter, question position and unsaved-draft indicators survive a tab refresh; teacher submission still requires Save answer. The answered count indicates work entered, not correct answers or confirmed database saves.

A diagram viewer provides 75–200% zoom with horizontal panning on small screens. SVG viewBoxes, coordinates, aspect ratios, labels and graph scales are preserved; equations continue to use KaTeX in both the question and explanation. Paper attachments and worked solutions expand independently. Short MCQ answers use compact two-column cards; identical English/Arabic mathematical expressions display once.


### 10G3 quadratic learning outcomes

The Week 8 EOT exam has three new independent outcome items: transformations on page 707 Q3–10 (8 graph-choice MCQs and 8 description MCQs), transformations on pages 707–708 Q23–30 (8 graph-choice MCQs and 8 description MCQs), and factoring on page 721 Q5–10 (6 solution-set MCQs). All 38 questions are bilingual, have four options and one correct answer, and use new `10g3-` IDs; the old retired 10G3 IDs stay deleted. Source items 21–22 are outside the requested range and are not included. Existing 10A1 content remains unchanged.

The two transformation outcomes share the requested learning-outcome title, with distinct page/question ranges and Arabic labels. Q24 and Q26 explain the reciprocal horizontal scale factor and why reflection across the y-axis has no visible effect on an even quadratic. All graph options use the same coordinate scale and viewport. Newly published outcome seeds merge into existing browser caches without replacing teacher edits or restoring previously seen deletions.


### Printable 10G3 quadratic FRQs

Two additional Week 8 learning outcomes contain four graph-reading FRQs (maximum/minimum value and interpretation, symmetry, vertex, y-intercept, domain, range and end behavior) and six graph-solving FRQs (page 711 Q1–6). The first image has no supplied textbook page; its reference is recorded as graph questions 1–4. No page number was guessed. The original 35 questions in 10A1 remain unchanged.

Students can type, draw, upload a paper answer, or choose **Print question** / **Print worksheets**. The group print action uses the current outcome filter, or all ten printable FRQs when viewing all outcomes. The teacher can print a question from its detail view, or all printable FRQs in the selected classroom. Native printing also supports saving as PDF.

Each A4 portrait page has blank name/school fields, bilingual instructions, an accurate vector graph, answer boxes and ruled working space. Graph-solving pages include a blank five-row x/y table, an empty Cartesian plane and separate intercept/solution boxes. Print content is generated from the question definition and excludes model answers, existing table entries, typed responses and drawn strokes. The viewer's current question and saved answers are not changed by printing. KaTeX equations and local font assets are included in the print document. Tested as a ten-page A4 PDF, with one question per page and no overlapping working areas or footers.

Graphing grids use equal physical spacing for grid squares. Axis labels and instructions explicitly state each axis's numerical step (including y-step 5 where needed). The drawing tool uses the plane's actual bounds, and the saved SVG viewBox remains 600×410.


### 9G3 Week 8 exam and complete FRQ printing

9G3 has 25 bilingual questions assigned to four outcomes: solve equations for specific variables (page 125 Q11–18: eight MCQs; Q19–22: four two-part FRQs); calculate and interpret rate of change (page 221 examples 3–4: four table MCQs); calculate and interpret slope (page 223: the two supplied graphs plus three original practice graphs); and graph linear functions using tables (page 215 Q5–8: four FRQs). The Grade 9 portal infers grade 9 at check-in and uses the Grade 9 exam title. Existing Grade 10 questions remain unchanged.

At the teacher's request, the last rate table was adjusted to a straight-line pattern: x = 22, 29, 36, 43, 50 and y = −4, −1, 2, 5, 8, giving constant rate 3/7. All four rate tables now have constant rates. Slope graphs are exact SVG plots with a numbered unit grid, axes and only the blue function line; the original rise/run helper segments are omitted. The three extra slope graphs are labeled as original practice, rather than attributed to missing textbook artwork.

Every FRQ is now printable. Generic word-problem pages retain the complete English/Arabic scenario, equations and both parts, with separate response areas and ruled working space. Generic geometry pages retain their diagrams. Linear graphing pages have blank five-row tables and suitably scaled empty Cartesian planes, without the quadratic axis-of-symmetry instruction. Each page identifies its classroom, learning outcome and textbook reference. Printing an outcome or the whole classroom uses its FRQs; it excludes all model answers and student drafts. Verified packets contain 8 A4 pages for 9G3, 7 for 10A1 and 10 for 10G3.

### Grade 9 General — Week 10

Week 10 has four separate learning outcomes: linear-function dilations (12 MCQs, one description and one graph question for each exercise on page 246); arithmetic-sequence reasoning, continuation, nth-term rules and 11th terms (13 MCQs, page 257); deriving nth-term formulas (5 FRQs); and using a formula to find the 101st term and an inverse term position (5 FRQs). The two written outcomes use page 255 Q19–22 plus one clearly identified teacher-designed sequence each. The sequence 10, 15, 25, 40 is retained as a non-arithmetic reasoning question; arithmetic formulas are not applied to it.

Open **9G3 → Week 10** to practise each outcome. **Print FRQ review** collects the ten written questions only, with the platform watermark. The same review is available at `public/worksheets/grade-9-general-week10-arithmetic-frq-review.pdf`.

Run `node scripts/add-week10-grade9-questions.mjs` to generate the question and outcome seeds; `node scripts/build-week10-grade9-worksheets.mjs` generates the printable HTML. `node scripts/export-week10-grade9-sql.mjs` prepares a transaction-safe Neon import with exact routing. The existing `npm run db:migrate` also seeds this content when the backend database is reachable. Bundled data and local browser caching do not confirm database persistence.

### Grade 10 General and Advanced — Week 10

10G3 has 36 questions: 10 printable FRQs on multiplication properties and applications, 9 MCQs on dividing monomials, 7 MCQs on zero/negative exponents, and 10 MCQs on rational exponents. The rational-exponent outcome includes all page 599 Q9–16 and two additional rewriting exercises. Q57 uses the confirmed outer power `2t`; Q58 provides an empty classification table and a drawable equal-unit Cartesian plane, including in its printable review.

10A1 has 50 questions: 10 geometric-mean MCQs, 15 Pythagorean/converse MCQs, 13 special-triangle MCQs, and 12 printable 3D midpoint/distance FRQs. The duplicated midpoint screenshot is included once. Coordinate questions Q13–24 belong to the confirmed Q24 outcome; no textbook page is invented for that image. The Week 9 geometric-mean exercises retain their original IDs and assignments; Week 10 uses separately assigned copies.

Authoring scripts are `scripts/add-week10-general-questions.mjs` and `scripts/add-week10-advanced-questions.mjs`. Matching `build-week10-*-worksheets.mjs` scripts generate printable HTML; `export-week10-*-sql.mjs` scripts generate transaction-safe imports. All three Week 10 FRQ PDF reviews are in `public/worksheets/`. Every Week 10 outcome has at least five questions. All 178 Week 8/9 question records are preserved.

### Student interface

The student interface uses `student-theme.css` and `lib/student-design.js` for the classroom home, math illustration, responsive classroom/outcome cards, and study workspace. Home statistics come from the current week's published questions and outcomes. Outcome progress uses the same saved-draft check as question navigation; it does not indicate correctness or award invented progress. Question actions appear below the content so they do not cover equations.

Arabic regular/bold fonts are served from `public/fonts/` under the included Noto SIL Open Font License; no external font service is required. The theme is scoped to screens, leaving the existing A4 FRQ print styles and watermarks intact. Keyboard focus, reduced-motion preferences, student name/school entry, teacher sign-in, and Weeks 8–10 navigation remain available.

Students can choose **الحالي**, **استوديو**, or **مسار** above the classroom workspace. Studio uses cobalt editorial rows and geometric artwork; Masar uses a forest/lime learning path and desktop classroom rail. The browser remembers the choice under `math100-student-theme-v1`. Switching themes updates styles without replacing question fields, navigating away, or clearing answers.

The native animated helper **مِيم** opens from each practice question. It offers a concept hint, progressively revealed steps from that question's approved solution, and a solved example from the same concept/classroom/week when available. Graph examples include the correct graph. Arabic/English explanations, keyboard dialog controls, a remembered motion toggle, and reduced-motion support are included. This implementation runs locally in the website without a Pets integration or an external AI service. It is excluded from printed worksheets and the separate SCORM exam package.

### Week 10 SCORM exams

Standalone SCORM 1.2 ZIPs for **9G3, 10G3 and 10A1** are available in [downloads](downloads/README.md). Each uses a 15-minute deadline, one graded attempt, required student name/number, three MCQs at two marks each and one four-part automatically marked numeric FRQ at one mark per blank. Topic/task pools keep the same topic weights on every form; the common FRQ is identical within a classroom. All content comes from existing Week 10 practice. The website's question records and native practice flows are unchanged.

`node scripts/build-week10-scorm.mjs` rebuilds all three ZIPs and their blueprint manifest using the maintained runtime in `scorm/week10/`. Tests inspect the packaged files, numeric marking, source alignment, outcome coverage, shuffled key mappings, attempt validation and timeout behavior. Browser verification uses a simulated SCORM 1.2 LMS, including save failure/retry, reload recovery, duplicate-window locking, completion locks and mobile layouts. The LMS activity must also enforce maximum attempts **1** and maximum grade **10**; review the included setup instructions before assigning.

Week 10 also has two-page A4 paper backups for each classroom, a six-page combined student pack and a separate three-page teacher key in [downloads](downloads/README.md). The fixed paper forms use the same topic pools, 10 marks, 15 minutes and common four-part FRQs as the SCORM exams. Rebuild with `node scripts/build-week10-paper-exams.mjs`, then `node scripts/export-week10-paper-pdfs.mjs` using installed Playwright/Chromium. The paper review caught and corrected missing triangle diagrams in the original 10A1 SCORM ZIP; re-import that ZIP if using the earlier copy. A regression test now compares every diagram-dependent triangle pool item with its source renderer.

10A1 now includes an image for every question, including a geometric-mean altitude diagram for every geometric-mean variant and a schematic 3D-coordinate segment for the FRQ. `lib/exam-illustrations.js` supplies these reusable illustrations to the SCORM and paper builders. Its SCORM package enables the offline warning sound in `scorm/week10/focus-alarm.js`; Start or the sound-test button activates audio, focus/tab loss starts the tone, and returning or submitting stops it. Browser/device audio restrictions are reported visibly and do not block grading. LMS score and per-part interactions remain independent of the warnings, with no automatic mark penalty. Reopening may require the sound-test button again because of autoplay rules.

10A1 SCORM attempts also shuffle the three MCQs’ display order, in addition to topic-pool selection and answer choices. One question per topic and the common four-part FRQ keep all forms at the same 10-mark distribution. The 15-minute deadline and complete shuffled form are saved for resuming; existing attempts without a saved display order retain their original order.

A separate **10A1 Week 10 additional-attempt** ZIP is available in [downloads](downloads/README.md). Import it as a new LMS activity and restrict it to the students who submitted the first exam. Its independent package ID and browser storage key preserve the original completed attempt while allowing one new 15-minute attempt with the same questions, images, scoring, shuffle and alarm. `node scripts/build-week10-extra-attempt.mjs` derives it from the released original ZIP without altering that ZIP. No database or submission deletion is needed or performed.

Grade 9 has a separate **20-minute Week 10 SCORM 1.2 exam**, built by `node scripts/build-grade9-week10-20min-scorm.mjs`. It preserves the original 16-question topic pools and four-part FRQ, adds given-term illustrations, enables shuffled MCQ order and the focus alarm, and retains the 10-mark / one-attempt / LMS-reporting settings. Both the packaged timer and displayed labels use 20 minutes. Import as a new activity; the original 15-minute Grade 9 package, Grade 10 packages and previous submissions remain untouched. Source alignment, all sampled forms' marking, every topic's coverage, images and the full 20-minute timeout/resume behavior are tested.

An independent **9G3 single-student, one-trial** package is also available in [downloads](downloads/README.md). It preserves that 20-minute exam's exact runtime and questions, with a new package/storage identity. Build with `node scripts/build-grade9-single-student-scorm.mjs`, import as a new activity, and restrict access to the intended learner in the LMS. No student's identity is embedded in this public ZIP, and the package does not replace LMS audience controls.

### 10A1 Term 1 question bank by learning outcome

The supplied Grade 10 Advanced question bank is available in **10A1 → Term 1 exam question bank**, with 25 separate outcome banks: six MCQs each for LO01–LO20 and three multipart FRQs each for LO21–LO25. It includes all 135 supplied question IDs, the three SVG diagrams, textbook references, answer mappings and marking rubrics. Each LO has its own downloadable JSON file. Navigation and LO titles are bilingual; questions retain the supplied English wording. MCQs remain unscored practice and FRQ rubrics retain their supplied 10 marks.

The bank uses a separate route and file-backed content collection, so weekly practice, existing student submissions and all SCORM packages are unchanged. Bank practice drafts remain in the browser tab and are labelled as local practice rather than teacher submissions. See [the import notes](content-imports/README.md) for the one documented median clarification and the retained original source. Rebuild with `node scripts/import-grade10-advanced-term1-bank.mjs`.

The bank's **اعمل اختبار تجريبي** button creates a one-hour mock exam: exactly one MCQ from each of the 20 MCQ learning outcomes, shuffled questions/options, one practice point per question and a total out of 20. The current form, responses, position and fixed deadline resume across refresh/navigation in the same tab. Answers and explanations appear after manual or timeout submission; a new randomized attempt can then be created. The five FRQ outcomes are excluded from this MCQ-only mock. Results are local practice, not LMS or teacher grades, and sign-out clears them.

**10 General Term 1 textbook review:** enter **10G3 → Term 1 exam question bank** for 25 LO banks with 120 MCQs and 21 written book exercises. Each question cites its original page and exercise. The mock draws one MCQ per topic (20 total), lasts 60 minutes and corrects after submission; local results are not sent to LMS. Download the [30-page study booklet](public/worksheets/grade-10-general-term1-study-booklet.pdf) from the bank: 4–5 textbook questions per LO, compact two-column MCQs, original diagrams, complete FRQs with working space and answer keys. Provenance and regeneration instructions are in [content-imports/README.md](content-imports/README.md).
