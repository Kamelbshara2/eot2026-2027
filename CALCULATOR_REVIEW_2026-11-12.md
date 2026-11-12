# مراجعة دليل الحاسبة · Calculator guide review (12/11/2026)

يظهر دليل الحاسبة (وصور الخطوات على المحاكي) **فقط** في الأسئلة التي تُستخدم فيها الحاسبة فعلاً. باقي الأسئلة تُحل يدوياً، ويُخفى زر الحاسبة فيها.

The calculator guide (with emulator step images) appears **only** where a calculator is really used. All other questions are solved by hand and the calculator button is hidden.

- Rule: `scripts/calculator-guides/calculator-policy.py` (outcome list + rounding questions + questions that ask for a calculator; exact/conceptual answers by hand).
- Every calculator question has key sequences; each sequence is replayed on the bundled fx-991CE X emulator in `tests/calculator-support.test.js` and must equal the independently computed value.
- Missing sequences were taken from the verified worked solutions (numeric expressions) or written by hand (trig legs, arc length with the π key, ln growth rate); 12G quadratics use Equation mode (a, b, c).

| Class | Calculator questions | By hand | Outcomes using the calculator |
|---|---|---|---|
| 9G3 | 38 | 200 | LO09 Solve proportions (4); LO21 Evaluate algebraic expressions (7); LO22 Use and rearrange formulas (4); LO24 Graph with a table (5); LO25 Piecewise functions (6); LO26 Arithmetic nth term (12) |
| 9A | 10 | 178 | LO24 Apply the arithmetic sequence formula (5); LO25 Solve equations for specific variables (5) |
| 10G3 | 41 | 114 | LO10 Rational exponents (6); LO11 Products of square roots (1); LO14 Factoring in context (6); LO16 Translations of quadratics (8); LO18 Dilations and reflections of quadratics (8); LO19 Solve quadratics by graphing (7); LO23 Multiplication properties of exponents (1); LO25 Write a quadratic from its graph (4) |
| 10A1 | 53 | 152 | LO08 Kites (2); LO14 Parts of similar triangles (2); LO18 Right-triangle trigonometry (9); LO19 Angles of elevation and depression (7); LO20 Area with two sides and an angle (9); LO24 Distance and midpoint in space (12); LO25 Law of Sines and the ambiguous case (12) |
| 11G | 23 | 114 | LO10 Applications of the Pythagorean Theorem (3); LO14 Trigonometric ratios: sides and angles (5); LO15 Trigonometric applications (5); LO23 Trigonometric ratios: perimeter and area (5); LO24 Angles of elevation and depression (5) |
| 11A | 31 | 123 | LO05 Change of base formula (5); LO06 Natural base and natural logarithms (5); LO14 Distribution: center, spread and shape (5); LO21 Evaluate expressions involving the natural base and logarithms (5); LO22 Exponential growth and decay using logarithms (2); LO24 Normal probabilities, areas and inverse values (4); LO25 Degrees, radians, arc length and phase shifts (5) |
| 12G | 27 | 255 | LO03 Solve quadratics by graphing (12); LO06 Quadratic Formula (9); LO24 Solve exponential equations (3); LO25 Normal probabilities and inverse values (3) |
| 12A | 9 | 171 | LO01 Estimate arc length (6); LO25 Applications of exponential and logarithmic derivatives (3) |
