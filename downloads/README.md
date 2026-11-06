# Downloadable exams

## 10A1 Week 10 — one additional attempt

[Download the separate additional-attempt SCORM 1.2 ZIP](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10A1-Week10-Extra-Attempt-SCORM12.zip).

Import this as a **new LMS activity**, named **10A1 Week 10 — Additional attempt**. Do not replace the first activity or delete its submissions. Set maximum attempts to **1** and maximum grade to **10**, and restrict the new activity to students who submitted the original exam using LMS groups/access rules. The ZIP cannot inspect another activity's completion or assign students by itself.

The new package has its own SCORM identifier and browser attempt-storage namespace. A completed first exam therefore does not consume this new activity's attempt. The first activity's grades and submissions stay intact; the new activity records its score separately. All approved settings remain: **15 minutes, 10 marks, three shuffled pooled MCQs, one common four-part auto-marked FRQ, images, student name/number, focus alarm, timeout submission and LMS reporting**. Rebuild only this new file with `node scripts/build-week10-extra-attempt.mjs` after building the original package. No database reset is performed.

## Week 10 — paper backup

- [9G3 paper exam — PDF](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/9G3-Week10-Paper-Exam.pdf)
- [10G3 paper exam — PDF](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10G3-Week10-Paper-Exam.pdf)
- [10A1 paper exam — PDF](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10A1-Week10-Paper-Exam.pdf)
- [All three student exams — six-page PDF](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/Week10-All-Classes-Paper-Exams.pdf)
- [Separate teacher answer keys — three-page PDF](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/Week10-Teacher-Answer-Keys.pdf)

Print at **100% / actual size on A4**. Each classroom's two-page paper has the same **15-minute / 10-mark** blueprint as its LMS exam: three MCQs worth two marks each, and the same common four-part numeric FRQ worth one mark per blank. Name, student-number, class and date fields are blank. The paper MCQs form a fixed selection from the released SCORM topic pools; printed option letters are mapped in the separate teacher key. The student PDFs contain no model answers or watermarks.

Build HTML and the review manifest with `node scripts/build-week10-paper-exams.mjs`, then export using `node scripts/export-week10-paper-pdfs.mjs` with Playwright/Chromium installed. If provided by the execution environment, set `PLAYWRIGHT_MODULE` to its installed module path and `CHROMIUM_PATH` to its browser executable. The exporter checks content against page footers and horizontal bounds before writing the PDFs. HTML sources and `week10-paper-exam-manifest.json` are included beside the PDFs for review.

## Week 10 — SCORM 1.2

**10A1 correction:** its ZIP now includes the required triangle diagrams. If you imported the earlier copy, replace it in your LMS with the corrected ZIP below before administering the exam. The scoring, question pools and common FRQ are unchanged.

**10A1 images and sound:** every MCQ pool variant, including every geometric-mean question, and the common 3D-coordinate FRQ include embedded SVG diagrams. The 10A1 paper backup also includes these illustrations. The 10A1 SCORM exam plays a repeating warning tone when the exam tab becomes hidden or its window loses focus, and stops on return or submission. Start unlocks sound; students can use **Test / enable alarm** before starting and after reopening. Keep device audio on and allow audio in the LMS player. Browser/OS restrictions or mute can suppress sound; the visible warning and LMS focus log remain. Focus loss can indicate minimizing or switching apps, but the browser cannot identify the other app. Scores, student details and warnings continue to be reported to the LMS after submission. The sound feature is enabled for 10A1 only.

**10A1 shuffling:** new attempts draw one MCQ from each topic pool, shuffle the three MCQs' display order, and shuffle their answer choices. The common four-part FRQ remains last. The exact form, display order, options and original **15-minute** deadline are retained when resuming; older attempts keep their original order. Random draws can coincide between students. The total remains **10 marks** (3 × 2 + 4 × 1), one attempt, automatic marking, student name/number, all images, the focus alarm and LMS submission reporting.

- [9G3 — Grade 9 General](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/9G3-Week10-Math-SCORM12.zip)
- [10G3 — Grade 10 General](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10G3-Week10-Math-SCORM12.zip)
- [10A1 — Grade 10 Advanced](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10A1-Week10-Math-SCORM12.zip)

Each Forms-style exam has **15 minutes, one attempt and 10 marks**: three MCQs worth two marks each, plus one common four-part FRQ with four numeric blanks worth one mark each. Short answers are automatically corrected, including equivalent fractions/decimals and Arabic digits. Student name and student number are required before the timer starts; leading zeros are preserved.

Each learner receives one randomly selected MCQ from each of three fixed topic/task pools. The common FRQ is identical within each classroom. Every classroom learning outcome is represented; 9G3's description and graph questions cannot repeat the same source exercise. Pools contain 16 MCQs for 9G3, 12 for 10G3, and 16 for 10A1. Random draws may coincide. All content is adapted from existing Week 10 student practice; no unseen questions were added.

Upload each ZIP directly to its class's LMS activity. **Set maximum attempts to 1 and gradebook maximum to 10**, allow resuming the same attempt, and hide answer review. SCORM reports scores on a 0–100 scale; the LMS scales them to 10 marks. Full-screen/focus warnings, copy restrictions, timeout submission, persisted forms/answers/deadlines and completion locks deter casual cheating; they are not secure proctoring. The included `README.txt` contains setup and marking details. Verified with a simulated SCORM 1.2 LMS; test in your own LMS before assigning.

Rebuild with `node scripts/build-week10-scorm.mjs`. Sources are in `scorm/week10/`; the reviewable topic blueprint is `week10-scorm-manifest.json`.

## Week 9

[Download the 10G3 Week 9 SCORM 1.2 ZIP](https://github.com/Kamelbshara2/eot2026-2027/raw/refs/heads/main/downloads/10G3-Week9-Math-SCORM12.zip)

This standalone LMS package contains five multiple-choice questions, worth two marks each, for a total of 10 marks. The exam has a 10-minute timer, saves progress within the same attempt, submits automatically when time expires, shuffles questions and options, and records focus changes. Completed attempts are locked.

Upload the ZIP directly to your LMS without extracting it. Set the SCORM activity's **maximum attempts to 1** and **maximum grade to 10**. The package reports a normalized score from 0 to 100, which the LMS scales to the 10-mark maximum. SCORM 1.2 does not provide a portable manifest setting for the LMS attempt limit.

The ZIP includes setup instructions. Browser controls deter casual copying; they do not provide secure remote proctoring.
