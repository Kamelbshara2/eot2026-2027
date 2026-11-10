# Worked solutions for image-card MCQs (steps + LaTeX)
Method: `python3 scripts/make-card-sheets.py 12G /tmp/claude-0/r12g` builds contact sheets of the cards still without a solution (id + key in the caption);
read each card, derive the answer, compare with the key (verified=1 only when equal; add a note when read from a graph),
save with `scripts/solutions_io.save(cls, batchname, {id: (verified, [(text, latex), ...])})`, then `python3 scripts/apply-upper-solutions.py`.
Rendering: `answer.steps` in lib/study-booklet.js (`solutionSteps`). Order of work: 12G cards, then 12A cards, 11G cards, then text questions.
