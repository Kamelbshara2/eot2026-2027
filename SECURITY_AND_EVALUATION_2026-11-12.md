# Security review and evaluation — 12 Nov 2026

## 1. Data-theft risk review

### What is protected well
| Area | Finding |
|---|---|
| Teacher sign-in (`api/admin.js`) | scrypt salted hashes, constant-time compare, lock-out after 5 failed tries (15 min), random 256-bit session tokens stored only as SHA-256 hashes, 8-hour expiry, logout deletes the session. |
| Writing questions / outcomes | Every POST to `/api/questions` and `/api/learning-outcomes` needs a valid teacher session; legacy keys and student ids are rejected (tests in `tests/admin.test.js`). |
| Student answers and uploads | A student can read and write only their own rows (bearer = their random v4 id, valid 24 h); classroom is checked on every save; uploaded papers are limited to PNG/JPEG/WebP/PDF with signature checks, 2 MB, served as attachments with `nosniff`. |
| Teacher dashboard | Student names and schools are HTML-escaped before display (no stored XSS). |
| SQL | All queries use tagged-template parameters (no string-built SQL). |
| CORS | Only same host or `PUBLIC_APP_ORIGIN` may call the API. |
| Secrets | `.env` is git-ignored; no database URLs, keys or tokens found anywhere in the repository history. |

### Fixed in this pass
1. **Retired questions leaked.** `GET /api/questions` returned the full content of deleted questions to anyone. Students now receive only live questions; deleted rows come back as tombstones (`data: null`). Signed-in teachers still get everything. Test added.
2. **Missing browser security headers.** Added on both hosts (`vercel.json`, `server.mjs`): `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy` (camera, microphone, location and payment off), `Cross-Origin-Opener-Policy: same-origin`.

### Remaining risks: these need your decision
| Risk | Level | Why it is not changed automatically | Option |
|---|---|---|---|
| **Answer keys are public.** The study booklets check answers in the browser, so `public/data/study/*.json` contains every correct option, full solution and calculator key. Anyone can download them from the site address. | Medium (by design) | Self-checking practice needs the key on the device. | Acceptable for revision material. Do **not** put real exam papers in `public/`. |
| **Week 9 teacher answer key is public.** `public/exams/math-9th-week-teacher-answer-keys.pdf/.html` and `week9-exam-manifest.json` (with `correctIndex`) can be downloaded by anyone who guesses the URL. | Low now (exam already given); High if reused | A test and your printing links expect these paths. | Move teacher keys to `downloads/` (not published), the same way the Week 10 key already is. |
| **No rate limiting.** Student sign-in and practice saves (up to 2 MB per upload) can be spammed to fill the database. | Low–Medium | Serverless functions need an external store (e.g. Upstash, Vercel KV) to rate-limit. | Add Vercel Firewall rate-limit rules on `/api/*`, or a KV-based limiter. |
| **Student identity is name + school only.** Anyone can sign in under any name, which suits a practice tool. Each sign-in gets a new random id, so nobody can read another student's answers. | Low | A password would add friction for students. | Optional: a class join code checked on the server. |
| **The page can be framed** (no `X-Frame-Options` / `frame-ancestors`). | Low | You may embed the site in Masar/Teams; blocking frames would break that. | If it is never embedded, add `Content-Security-Policy: frame-ancestors 'self'`. |
| **Content shield is deterrence only.** The blur-on-focus-loss and the key blocks stop casual copying. No browser can stop phone photos or OS screenshots. | Info | — | Watermarks with the student name (already present) are the real deterrent. |
| **KaTeX 0.16 low advisory** (GHSA-238p-pmpm-9mq7). Exploiting it needs an existing prototype-pollution bug; trust is limited to `\htmlClass`/`\htmlData`. | Low | KaTeX 0.19 is a breaking upgrade; all maths rendering must be re-tested. | Schedule the upgrade after the EOT. |

## 2. Evaluation: improvement opportunities

| Area | Current state | Opportunity |
|---|---|---|
| Step reasons | Every question has steps with a "why". 459 steps still use a generic reason (e.g. "work out the value"). | Write topic-specific reasons for these, starting with the most-practised outcomes. |
| Calculator | 237 questions use the calculator, all with emulator key images; 1,319 are marked "solved by hand" with the button hidden. | Add a short "check with the calculator" tip only where a by-hand answer is easy to verify (optional; kept out to avoid extras, as you asked). |
| Coverage | Every word of each EOT outcome description is practised (0 gaps after adding 17 authored questions, marked `authored_lo_variant`). | Replace authored questions with textbook exercises when the next textbook pages are uploaded. |
| Adaptive practice | Students choose questions in order. | Offer "practise my mistakes": re-show the questions a student got wrong, from saved attempts. |
| Teacher insight | The dashboard shows saved and correct counts per student. | Add a per-outcome heat-map of wrong answers to guide re-teaching before the EOT. |
| Accessibility | WCAG AA contrast passes in all 3 themes; bidi Arabic/English steps. | Add a larger-text toggle for low-vision students; test with a screen reader. |
| Offline | Booklets load from static JSON. | A service worker would let students revise without internet. |
