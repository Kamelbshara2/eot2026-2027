# Calculator integration review — 8 November 2026

The user confirmed **Casio fx-991EX ClassWiz**. ES PLUS and CW menu instructions must not be substituted.

## Candidates inspected

- [calc-key / KeyFontHelper](https://github.com/CalcWorld/KeyFontHelper), npm `calc-key` 1.0.4, GPL-3.0-or-later: maps key names to font characters, including EX maps. The inspected npm package does not bundle the matching Casio font files. This is a key-rendering helper, not a working calculator emulator. No code or fonts from it were included here.
- [fx991ex-emulator](https://github.com/magicnothief/fx991ex-emulator) and [fx-991es web emulator](https://github.com/waynelogan/casio-fx-991es-web-emulator) were found in GitHub search. Their firmware accuracy and redistribution rights were not established. An ES-branded implementation does not establish EX menu accuracy.
- [Casio education emulator product page](https://edu.casio.com/products/classroom/emulator/) and Casio support pages could not be fetched in this environment (HTTP 403). No official emulator was downloaded or redistributed.

## Implemented approach

`render-calculator-guides.mjs` uses Playwright/Chromium to produce original instructional key cards. Cards name the EX model, show mode/keys/input expressions and are explicitly labelled **not an official firmware screenshot**. They do not resemble a purported screenshot of an operating Casio device. Practice pages also expose the steps as accessible text; cards are hidden in a disclosure and excluded from active mocks.

Guides distinguish Calculate evaluation, SOLVE, numerical equivalence checks, degree-mode trigonometry, SSA angle checks and TABLE. Numerical checks are not proofs. TABLE generates coordinate values, not graphs. The booklets use blank answer tables; completed values remain in solutions. Keyboard/input sequences have been reviewed for the EX workflow, but were not validated against a physical calculator or licensed official emulator in this environment.

A future licensed/verified EX emulator may replace the visual layer without changing LO/question associations. Recheck model menus and font rights before integration. These findings are a scoped candidate review, not a claim that no suitable library exists anywhere.
