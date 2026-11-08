# Grade 10 Advanced Term 1 bank

`Grade10_Advanced_Question_Bank.json` is the supplied source file, retained byte-for-byte. It contains 25 learning outcomes, 120 MCQs and 15 multipart FRQs. Its textbook references identify alignment; the questions are newly authored parallel practice, as stated in the file. The site now explicitly labels this as parallel practice with changed numbers/contexts and supplied schematic SVGs, not a verified verbatim textbook selection.

Run `node scripts/import-grade10-advanced-term1-bank.mjs` to publish the standalone 10A1 bank in `public/data/exam-banks/10a1-term1/`. The output contains the original source, the complete organized `bank.json`, a site index, one downloadable JSON bank per LO and the three referenced SVG illustrations. The importer rejects unknown outcomes, duplicate IDs, invalid answer mappings, incorrect FRQ mark totals and executable/external SVG content.

The site exposes this bank under **10A1 → Term 1 exam question bank**, independently of Weeks 8–10. MCQ marks remain `null`, as supplied; each written practice set retains its author-assigned 10 marks. Student drafts are held in the current browser tab only and are explicitly labelled as not sent to the teacher. This addition does not seed or modify the live Neon database or alter existing question/exam records.

The **اعمل اختبار تجريبي** option draws one MCQ from each of LO01–LO20, shuffles the 20 questions and their options, and starts a **60-minute** deadline on Start. Each answer is worth one practice point, for a result out of 20; this does not assign marks to the original bank items. No solutions or rule reminders appear during the attempt. Refreshing or leaving and returning in the same tab resumes the saved form, answers and original deadline. Expired attempts submit on the next active timer check, including when returning after time away. Results include the selected answer, correct answer, supplied explanation and diagrams. Students can start another mock after finishing. Mock results stay in the tab, are cleared on sign-out and are not LMS/teacher submissions.

One documented content clarification is applied to the published question copy: **G10A-Q23-FRQ-03, part (b)** now uses a separate pair of similar triangles with the same 3:5 scale factor. The original triangle's sides 6, 9, 12 imply a median from A of √90/2, so the additional stated median 7.2 could not belong to that triangle. The new wording preserves the supplied number, intended answer 12 and two marks. The index and LO23 download record the original and revised wording; the original source download is untouched.

**G10A-Q19-MCQ-03** also carries a calculator-precision note: 45/tan(18°) ≈ 138.495759 m rounds to 138 m. The original question, correct option and explanation remain intact; the note prevents rounding the intermediate value to 138.5 before rounding again.

## Grade 10 General: textbook-only Term 1 selection

The uploaded `10عام.pdf` is a 170-page image-only extract of Reveal, printed pp. 569–738. Its SHA-256 is `d7e5f97845c8c15fa857e4e34763cd73614463506ef520cc61666452918bf7af`. The full book is not duplicated in the repository. The supplied official coverage is retained at `term1-coverage/grade10-general-coverage.pdf`.

`grade10-general-term1-selection.json` records every selected exercise, its printed/PDF page, the book hash, all MCQ choices/keys, complete FRQ parts and worked rubrics. Every numeric problem comes from the book; only MCQ choices and explanatory answers are added. The selection is not newly authored parallel practice. The bank has **25 independent LO downloads, 120 MCQs (six per slot Q1–Q20) and 21 written questions (four per Q21, Q22, Q24 and Q25; five for Q23)**. Supplementary same-LO exercises on pp. 607, 721 and 729 supply enough practice where the coverage cites fewer than four actual questions. They are identified in the LO references. The two p.608 items cited under the square-root quotient outcome are actually **cube roots**; their root indices are preserved.

Rebuild from the user-provided book, without fetching any external resources:

```sh
python scripts/build-grade10-general-term1-bank.py /path/to/10عام.pdf
node scripts/build-grade10-general-term1-booklet.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/usr/bin/chromium node scripts/export-grade10-general-term1-booklet.mjs
```

The Python builder requires PyMuPDF and SymPy; the HTML builder uses the existing KaTeX package. Start Vite on port 4320 with base `/eot2026-2027/`, or set `BOOKLET_BASE_URL` for another server. The print source embeds its fonts and original clipped diagrams. PDF export checks every page against its footer, verifies math stays within question columns and rejects missing diagrams or invalid KaTeX.

The site route is `#/classrooms/10G3/banks/term1`. Its **60-minute / 20-MCQ** mock uses exactly the same one-question-per-topic selection, shuffled question/option order, saved deadline and post-submission review as Advanced. Responses/results remain in the same tab, with separate storage for each bank and student. The old Advanced storage keys are preserved. No live database, weekly questions, published SCORM packages or official exam attempts are changed. Written practice uses explicit 10-point model rubrics, not the official final-exam slot weights.

The linked **30-page A4 study booklet** selects **80 MCQs + all 21 FRQs** (4–5 questions per LO), includes brief rule reminders, original graph/image crops and source references, uses two columns for compact MCQs and full width for long choices, and keeps complete written tasks together with solution space. Four final pages give MCQ keys and worked FRQ answers. Selection prioritises the supplied coverage and complementary skills; it makes no unsupported prediction about government exam questions. The official coverage says 150 minutes and 100 marks, distinct from this local practice mock.

Grade 9 General remains pending a readable textbook upload; its coverage PDF alone is not used to invent questions.

The PDF exporter also runs `python scripts/verify-term1-booklet.py 10G3`: this reads the actual PDF, checks all 80 printed MCQ keys against the published bank and per-LO downloads, and compares the decoded pixels of all 11 included diagrams with their PNG assets. Pass the original textbook path as a final argument to additionally verify each asset against its exact original PDF crop. This checks artifact consistency and source-image fidelity; it does not by itself prove mathematical correctness or validate an inaccessible Grade 9 book.
