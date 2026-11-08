# Textbook-only review banks and retained imports

The active Advanced bank now comes from the uploaded `10adv 1.pdf` (printed pp. 627–686) and `10متقدم 2.pdf` (pp. 57–220). **100 original questions / 25 outcomes / 80 MCQs / 20 FRQs / 60 original image crops**. All source hashes, page mappings, exercises, choices and worked answers are recorded in `grade10-advanced-textbook-selection.json`. The [30-page booklet](../public/worksheets/grade-10-advanced-term1-study-booklet.pdf) contains all 100 selected questions. MCQ choices and worked solutions are added; original numerical data and diagrams are retained.

The original `Grade10_Advanced_Question_Bank.json` remains byte-for-byte intact. Its former published bank, including the documented median clarification and calculator precision note, is preserved under `legacy-10a1-parallel-bank/`. It is parallel practice with changed numbers and schematic SVGs, not the active textbook bank. The old importer now targets that archive by default and cannot overwrite the active bank accidentally.

Regenerate the active Advanced bank and booklet:

```sh
python scripts/build-grade10-advanced-textbook-bank.py /path/to/10adv-1.pdf /path/to/10adv-2.pdf
node scripts/build-grade10-advanced-term1-booklet.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/usr/bin/chromium node scripts/export-grade10-advanced-term1-booklet.mjs
python scripts/verify-term1-booklet.py 10A1 /path/to/10adv-1.pdf /path/to/10adv-2.pdf
```

## Grade 9 General: textbook-only Term 1 selection

The uploaded `9-1.pdf` contains printed pp. 1–134 and `9-2.pdf` contains pp. 135–281. `grade9-general-textbook-selection.json` records both hashes and every selected exercise. The supplied coverage is retained at `term1-coverage/grade9-general-coverage.pdf`. The bank has **26 independent LO downloads / 104 questions / 80 MCQs / 24 complete FRQs / 16 original image crops**, four questions per outcome. The [30-page booklet](../public/worksheets/grade-9-general-term1-study-booklet.pdf) uses the same selection, with original visuals, two-column MCQs, full written tasks, solution space, blank coordinate planes and worked keys.

Where a cited range contains fewer than four exercises, original subparts are separated or an original same-LO exercise is used, with explicit citations: rate-of-change examples plus Check blanks; step-function graph descriptions plus domain/range; graph A on p.233 supplements the three labelled graphs on p.236. No changed-number variants are introduced. Original source details include p.81 exercise 2 (`44=t−72`), p.89 exercise 29 (`5f/2−6=19`), and p.265 exercise 18c (`f(9.7)`); answers are 116, 10 and 16 respectively.

```sh
python scripts/build-grade9-general-textbook-bank.py /path/to/9-1.pdf /path/to/9-2.pdf
node scripts/build-grade9-general-term1-booklet.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/usr/bin/chromium node scripts/export-grade9-general-term1-booklet.mjs
python scripts/verify-term1-booklet.py 9G3 /path/to/9-1.pdf /path/to/9-2.pdf
```

Both banks are separate static collections under `public/data/exam-banks/`, accessible at `#/classrooms/{10A1|9G3}/banks/term1`. Their mock selects exactly one question per MCQ outcome, 20 total, shuffles questions/options, and uses a fixed 60-minute deadline. Responses and results remain local to the tab; retakes are available after finishing. They do not seed Neon, change weekly practice or replace published SCORM exams. Written rubrics are 10-point practice rubrics, not official slot weights. Advanced textbook attempts use a new namespace to avoid mixing previous parallel-bank forms.

## Grade 10 General: textbook-only Term 1 selection

The uploaded `10عام.pdf` is a 170-page image-only extract of Reveal, printed pp. 569–738. Its SHA-256 is `d7e5f97845c8c15fa857e4e34763cd73614463506ef520cc61666452918bf7af`. The full book is not duplicated in the repository. The supplied official coverage is retained at `term1-coverage/grade10-general-coverage.pdf`.

`grade10-general-term1-selection.json` records every selected exercise, its printed/PDF page, the book hash, all MCQ choices/keys, complete FRQ parts and worked rubrics. Every numeric problem comes from the book; only MCQ choices and explanatory answers are added. The selection is not newly authored parallel practice. The bank has **25 independent LO downloads, 120 MCQs (six per slot Q1–Q20) and 21 written questions (four per Q21, Q22, Q24 and Q25; five for Q23)**. Supplementary same-LO exercises on pp. 607, 721 and 729 supply enough practice where the coverage cites fewer than four actual questions. They are identified in the LO references. The two p.608 items cited under the square-root quotient outcome are actually **cube roots**; their root indices are preserved.

Rebuild from the user-provided book, without fetching any external resources:

```sh
python scripts/build-grade10-general-term1-bank.py /path/to/10عام.pdf
node scripts/build-grade10-general-term1-booklet.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/usr/bin/chromium node scripts/export-grade10-general-term1-booklet.mjs
```

The Python builder requires PyMuPDF and SymPy; the HTML builder uses the existing KaTeX package. The exporter loads the embedded HTML directly into Chromium; a dev server is optional. Set `BOOKLET_BASE_URL` to verify a served copy instead. The print source embeds its fonts and original clipped diagrams. PDF export checks every page against its footer, verifies math stays within question columns and rejects missing diagrams or invalid KaTeX.

The site route is `#/classrooms/10G3/banks/term1`. Its **60-minute / 20-MCQ** mock uses exactly the same one-question-per-topic selection, shuffled question/option order, saved deadline and post-submission review as Advanced. Responses/results remain in the same tab, with separate storage for each bank and student. The old Advanced storage keys are preserved. No live database, weekly questions, published SCORM packages or official exam attempts are changed. Written practice uses explicit 10-point model rubrics, not the official final-exam slot weights.

The linked **30-page A4 study booklet** selects **80 MCQs + all 21 FRQs** (4–5 questions per LO), includes brief rule reminders, original graph/image crops and source references, uses two columns for compact MCQs and full width for long choices, and keeps complete written tasks together with solution space. Four final pages give MCQ keys and worked FRQ answers. Selection prioritises the supplied coverage and complementary skills; it makes no unsupported prediction about government exam questions. The official coverage says 150 minutes and 100 marks, distinct from this local practice mock.

All selections prioritise the supplied learning outcomes and complementary skills. They do not predict particular government final-exam questions.

The PDF exporter also runs `python scripts/verify-term1-booklet.py 10G3`: this reads the actual PDF, checks all 80 printed MCQ keys against the published bank and per-LO downloads, and compares the decoded pixels of all 11 included diagrams with their PNG assets. Pass the original textbook path as a final argument to additionally verify each asset against its exact original PDF crop. This checks artifact consistency and source-image fidelity; it does not by itself prove mathematical correctness; the source questions and worked answers are reviewed separately.
