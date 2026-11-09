# Calculator support review

The study app now attaches a calculator/written-solution guide to all 389 questions across 76 learning outcomes: 126 questions in 9G3, 155 in 10G3 and 108 in 10A1. The source banks, diagrams and marking keys are unchanged. The generated companion data records the method, preparation, actual inputs, reference outputs and use of those outputs in written work. It adds support for 120 questions previously without an applicable guide.

27 questions require reasoning and 14 require reading a diagram or setting up the mathematics before numerical entry. These are explicitly identified; coverage does not mean a scientific calculator can solve or prove every question. Numerical substitutions check examples, not identities. TABLE generates coordinate pairs, not graphs. Exact algebra, domains, endpoints and requested written methods remain part of the solution.

## Corrections and validation

- Integer-factorisation parameter questions enumerate factor pairs instead of using an arbitrary numerical substitution.
- Two rational equations failed SOLVE from the initial guess zero. Their tested guess is now 10, with forbidden denominator values and substitution checks included.
- The graph-workspace question includes reference tables for all three requested functions: X, X² and X³.
- Quadratic instructions use Equation/Func → Polynomial → Degree 2. They distinguish real, repeated and non-real roots.
- Existing screenshot examples were recaptured with the local English menu adaptation. They remain three general demonstrations, not 389 question-specific physical calculator captures.
- Independently computed reference values were compared with 477 arithmetic key sequences and 151 table-point evaluations in the vendored engine. 23 quadratic sequences and 18 SOLVE sequences also passed. Table-point checks evaluate each expression in Calculate mode; they do not certify every TABLE navigation sequence.
- Browser checks covered SOLVE, radicals, quadratics, the three-function graph task and proof questions at 1360px and 390px. No KaTeX errors, page exceptions or horizontal page overflow were found in these representative lessons.

## Sources and limits

The original bank prompts and keys, and [the upstream emulator implementation](https://github.com/magicnothief/fx991ex-emulator/tree/2c26421/src/calc), informed the methods. Public repository searches for calculator manuals did not yield a suitable additional manual. Live access to the [official Casio EX guide](https://support.casio.com/global/en/calc/manual/fx-991EX_en/) was blocked by the environment proxy; it is a reference link, not a newly verified source. No physical EX or ES PLUS validation is claimed. ES PLUS menu numbers differ; this companion primarily documents the integrated CE X/ClassWiz workflow. Original diagram accuracy and all source marking keys were not independently re-certified by numerical tests.

The older calculator-guide inventory describes the original metadata. `calculator-support-review.json` is the coverage inventory for this companion layer; `calculator-key-validation.json` records the engine checks.

## Reproduce

Use Python with Sympy and `antlr4-python3-runtime==4.11.1`:

```sh
python scripts/calculator-guides/build-support.py
node scripts/calculator-guides/verify-support.mjs
npm test
npm run build
```

To recapture the illustrated demonstrations, start the development server, then run `node scripts/calculator-examples/capture.cjs`. Set `CALCULATOR_URL` and `CHROMIUM_PATH` when needed.
