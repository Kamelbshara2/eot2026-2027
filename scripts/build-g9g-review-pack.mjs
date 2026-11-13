// Grade 9 General (9G3) review pack (user request, 13 Nov 2026):
//  1) 30-minute worksheet PDF from the bank (questions not in the printed study booklet), teacher key on page 4
//  2) SCORM 1.2 auto-marked quiz of authored MIRROR questions (same outcome and structure, new numbers)
// Run: PLAYWRIGHT_MODULE=/opt/node-tools/node_modules/playwright/index.mjs node scripts/build-g9g-review-pack.mjs
import {buildWorksheet, buildScorm, tex, near, check, same} from './review-pack-lib.mjs';

const floor = Math.floor;
await buildWorksheet({
  classroom: '9G3', slug: 'grade-9-general', grade: 'Grade 9 General', gradeAr: 'الصف التاسع عام',
  partA: [
    {id: '9G-Q01-p9-exercise-16', min: 1, key: 'C', work: '(11-4)\\cdot5\\ \\ (\\text{difference first, then multiply})'},
    {id: '9G-Q02-p42-exercise-30', min: 1, key: 'C', work: '4(8p)+4(16q)-4(7r)=32p+64q-28r', check: () => same(p => 4 * (8 * p + 16 * 2 - 7 * 3), p => 32 * p + 64 * 2 - 28 * 3)},
    {id: '9G-Q03-p81-exercise-14', min: 1, key: 'C', work: 'a=\\tfrac58+\\tfrac12=\\tfrac58+\\tfrac48=\\tfrac98', check: () => near(5 / 8 + 1 / 2, 9 / 8)},
    {id: '9G-Q20-p89-exercise-31', min: 1, key: 'B', work: '\\tfrac x4=1-5=-4\\Rightarrow x=-16', check: () => near(-16 / 4 + 5, 1)},
    {id: 'G9G-BOOK-Q15-MCQ-04', min: 1, key: 'B', work: 'm=\\tfrac{1-(-4)}{0-5}=\\tfrac{5}{-5}=-1', check: () => near((1 - -4) / (0 - 5), -1)},
    {id: '9G3-REV-LO17-03', min: 1, key: 'A', work: 'd=-3;\\ a_{11}=-9+10(-3)=-39', check: () => -9 + 10 * -3 === -39},
    {id: '9G-Q04-p125-exercise-18', min: 2, key: 'B', work: 'df+10=6g\\Rightarrow df=6g-10\\Rightarrow f=\\tfrac{6g-10}{d}', check: () => near((3 * ((6 * 5 - 10) / 3) + 10) / 6, 5)},
    {id: '9G-Q06-p97-exercise-5', min: 2, key: 'B', work: 'b-4=3b\\Rightarrow -4=2b\\Rightarrow b=-2', check: () => near((-2 - 4) / 6, -2 / 2)},
    {id: '9G-Q09-p113-exercise-17', min: 2, key: 'A', work: '7\\cdot8=4(f-4)\\Rightarrow 56=4f-16\\Rightarrow f=18', check: () => near(7 / 4, (18 - 4) / 8)},
    {id: '9G-Q10-p89-exercise-25', min: 2, key: 'A', work: 'ax=-3-11=-14\\Rightarrow x=-\\tfrac{14}{a}', check: () => near(3 * (-14 / 3) + 11, -3)},
    {id: '9G-Q12-p235-exercise-13', min: 2, key: 'D', work: '-8y=2x+24\\Rightarrow y=-\\tfrac x4-3', check: () => same(x => (-2 * x - 24) / 8, x => -x / 4 - 3)},
    {id: '9G-Q16-p265-variant-variant', min: 2, key: 'C', work: 'x-1=-1.4;\\ \\lfloor-1.4\\rfloor=-2;\\ 2(-2)=-4', check: () => 2 * floor(-0.4 - 1) === -4},
  ],
  partB: [
    {id: '9G-Q23-p97-exercise-9', minutes: 7, parts: [{text: 'Show all steps and check your solution. State whether the equation has one solution, no solution or infinitely many solutions.', marks: 10, hint: 'Distribute → collect the variable on one side → divide → substitute to check', lines: 7}]},
    {id: '9G-Q26-p255-exercise-18', minutes: 5, parts: [{text: 'Find the common difference.', marks: 4, lines: 2}, {text: 'Find the next three terms.', marks: 6, lines: 3}]},
  ],
  keyB: [
    `<p><b>13.</b> ${tex('5g+40-7=117-g\\Rightarrow 5g+33=117-g\\Rightarrow 6g=84\\Rightarrow g=14')}</p>`,
    `<p class="mk">Check: ${tex('5(14+8)-7=103')} and ${tex('117-14=103')} ✓ · one solution. Marks: distribute (2), collect terms (3), solve (3), check and state the type (2).</p>`,
    `<p><b>14 (a).</b> ${tex('d=-5-(-2)=-3')} <span class="mk">(4)</span></p><p><b>14 (b).</b> ${tex('-11-3=-14,\\ -17,\\ -20')} <span class="mk">(2 each)</span></p>`,
  ],
  srcnote: 'Source: Grade 9 General textbook exercises and labelled variants from the platform bank; none appear in the printed Term 1 study booklet.',
});
check(5 * (14 + 8) - 7 === 103 && 117 - 14 === 103, 'Q13 key');

// ---------------------------------------------------------------- mirror quiz
const W13 = {h: 9, side: 43}; // 4(h+3) − 5 = 52 − h
check(4 * (W13.h + 3) - 5 === W13.side && 52 - W13.h === W13.side, 'W13');
const seq = [7, 3, -1, -5], d = seq[1] - seq[0], next = [1, 2, 3].map(k => seq[3] + k * d);
check(d === -4 && next.join() === '-9,-13,-17', 'W14');
// mirror MCQ checks
check(near(2 / 3 + 1 / 4, 11 / 12) && near((1 + 2) / (4 + 3), 3 / 7), 'M3');
check(same(h => (3 * ((5 * h + 8) / 3) - 8) / 5, h => h), 'M4'); // k=3: (k·m − 8)/5 = h with m=(5h+8)/k
check((6 + 6) / 4 === 6 / 2, 'M5');
check(near(5 / 3, (12 - 2) / 6), 'M6');
check(near(4 * (-18 / 4) + 13, -5), 'M7');
check(same(x => (-3 * x - 18) / 6, x => -x / 2 - 3), 'M8');
check(near((6 - -2) / (2 - 6), -2), 'M9');
check(3 * floor(-2.5 + 1) === -6 && 3 * floor(-2.5) === -9 && 3 * Math.trunc(-1.5) === -3, 'M10');
check(4 + 8 * 7 === 60 && 4 + 9 * 7 === 67 && 4 + 7 * 7 === 53, 'M11');
check(25 / 5 - 3 === 2, 'M12');

await buildScorm({
  slug: 'grade-9-general', grade: 'Grade 9 General', gradeAr: 'الصف التاسع عام', identifier: 'G9G_TERM1_MIRROR_QUIZ_30MIN',
  mcq: [
    {lo: 'LO01', title: 'Numerical expressions', en: 'Which numerical expression represents the difference of fifteen and six, multiplied by three?', ar: 'أيّ تعبير عددي يمثّل الفرق بين خمسة عشر وستة، مضروباً في ثلاثة؟',
     opts: ['15-6(3)', '(15-6)3', '(15+6)3', '15-(6+3)'], key: 'B', work: '(15-6)\\cdot3=27', why: ['only 6 is multiplied by 3', '', 'this is a sum, not a difference', 'adds 6 and 3 instead of multiplying']},
    {lo: 'LO02', title: 'Distributive Property', en: 'Use the Distributive Property to rewrite and simplify.', ar: 'استخدم خاصية التوزيع لإعادة الكتابة والتبسيط.', math: '5(6a-9b+2c)',
     opts: ['6a-9b+10c', '30a+45b+10c', '30a-9b+2c', '30a-45b+10c'], key: 'D', work: '5(6a)-5(9b)+5(2c)=30a-45b+10c', why: ['multiplied only the last term', 'lost the minus sign', 'multiplied only the first term', '']},
    {lo: 'LO03', title: 'Addition and subtraction equations', en: 'Solve the equation.', ar: 'حلّ المعادلة.', math: 'y-\\frac{2}{3}=\\frac{1}{4}',
     opts: ['-\\frac{5}{12}', '\\frac{11}{12}', '\\frac{3}{7}', '\\frac{12}{11}'], key: 'B', work: 'y=\\tfrac14+\\tfrac23=\\tfrac{3}{12}+\\tfrac{8}{12}=\\tfrac{11}{12}', why: ['subtracted instead of adding', '', 'added numerators and denominators', 'reciprocal of the answer']},
    {lo: 'LO20', title: 'Solve multi-step equations', en: 'Solve the equation.', ar: 'حلّ المعادلة.', math: '\\frac{x}{5}-3=2',
     opts: ['-5', '1', '25', '-25'], key: 'C', work: '\\tfrac x5=2+3=5\\Rightarrow x=25', why: ['subtracted 3 instead of adding it', 'divided by 5 instead of multiplying', '', 'sign error']},
    {lo: 'LO15', title: 'Slope from two points', en: 'What is the slope of the line through the given points?', ar: 'ما ميل المستقيم المارّ بالنقطتين؟', math: '(6,-2),\\ (2,6)',
     opts: ['-2', '2', '-\\frac{1}{2}', '\\frac{1}{2}'], key: 'A', work: 'm=\\tfrac{6-(-2)}{2-6}=\\tfrac{8}{-4}=-2', why: ['', 'sign error in the run', 'run over rise', 'run over rise and a sign error']},
    {lo: 'LO17', title: 'Arithmetic sequence arguments', en: 'What is the 9th term?', ar: 'ما الحدّ التاسع؟', math: '4,\\ 11,\\ 18,\\ 25,\\ldots',
     opts: ['67', '60', '63', '53'], key: 'B', work: 'd=7;\\ a_9=4+(9-1)\\cdot7=60', why: ['used n instead of n − 1', '', 'used 9 × 7 only', 'this is the 8th term']},
    {lo: 'LO04', title: 'Rearrange formulas', en: 'Solve the equation for m. Assume any divisor is nonzero.', ar: 'حلّ المعادلة بالنسبة إلى m. افترض أن كل مقسوم عليه لا يساوي صفراً.', math: '\\frac{km-8}{5}=h',
     opts: ['\\frac{5h+8}{k}', '\\frac{5h-8}{k}', '\\frac{h+8}{5k}', 'k(5h+8)'], key: 'A', work: 'km-8=5h\\Rightarrow km=5h+8\\Rightarrow m=\\tfrac{5h+8}{k}', why: ['', 'sign error when moving −8', 'did not multiply h by 5', 'multiplied by k instead of dividing']},
    {lo: 'LO06', title: 'Variables on each side', en: 'Solve the equation.', ar: 'حلّ المعادلة.', math: '\\frac{c+6}{4}=\\frac{c}{2}',
     opts: ['-6', '2', '6', '3'], key: 'C', work: 'c+6=2c\\Rightarrow c=6', why: ['sign error when collecting c', 'divided 6 by 3', '', 'halved 6']},
    {lo: 'LO09', title: 'Solve proportions', en: 'Solve the proportion.', ar: 'حلّ التناسب.', math: '\\frac{5}{3}=\\frac{k-2}{6}',
     opts: ['8', '-12', '\\frac{1}{12}', '12'], key: 'D', work: '5\\cdot6=3(k-2)\\Rightarrow 30=3k-6\\Rightarrow k=12', why: ['subtracted 2 instead of adding', 'sign error', 'reciprocal of the answer', '']},
    {lo: 'LO10', title: 'Multi-step equations with parameters', en: 'Solve for x. Assume b ≠ 0.', ar: 'حلّ بالنسبة إلى x. افترض أن b ≠ 0.', math: '-5=bx+13',
     opts: ['-18b', '-\\frac{18}{b}', '\\frac{18}{b}', '\\frac{8}{b}'], key: 'B', work: 'bx=-5-13=-18\\Rightarrow x=-\\tfrac{18}{b}', why: ['multiplied by b instead of dividing', '', 'sign error', 'added 13 instead of subtracting']},
    {lo: 'LO12', title: 'Slope-intercept form', en: 'Which equation is the slope-intercept form? Options give y.', ar: 'أيّ معادلة هي صيغة الميل والمقطع؟ الخيارات تعطي y.', math: '-3x-6y=18',
     opts: ['\\frac{x}{2}-3', '3-\\frac{x}{2}', '-\\frac{x}{2}-3', '-2x-3'], key: 'C', work: '-6y=3x+18\\Rightarrow y=-\\tfrac x2-3', why: ['sign of the x-term', 'sign of the constant', '', 'slope upside down']},
    {lo: 'LO16', title: 'Evaluate step functions', en: 'Evaluate the step function.', ar: 'احسب قيمة الدالة الدرجية.', math: 'f(x)=3\\lfloor x+1\\rfloor,\\quad x=-2.5',
     opts: ['-3', '-4.5', '-9', '-6'], key: 'D', work: 'x+1=-1.5;\\ \\lfloor-1.5\\rfloor=-2;\\ 3(-2)=-6', why: ['rounded −1.5 toward zero', 'did not take the floor', 'ignored the +1', '']},
  ],
  written: [
    {lo: 'LO23', title: 'Equations, identities and contradictions', en: 'Solve the equation and check your solution.', ar: 'حلّ المعادلة وتحقّق من الحل.', math: '4(h+3)-5=52-h',
     body: `<p class="fill">${tex('h=')} [[num:w13h]]</p><p class="fill">Check: both sides equal [[num:w13s]]</p><p class="fill">Type · النوع: [[sel:w13t]]</p>`,
     fields: [{id: 'w13h', kind: 'num', answer: W13.h, pts: 6, label: 'h'}, {id: 'w13s', kind: 'num', answer: W13.side, pts: 2, label: 'value of each side'},
       {id: 'w13t', kind: 'select', answer: 'one', pts: 2, label: 'type', options: [['one', 'One solution · حلّ واحد'], ['none', 'No solution · لا حلّ'], ['all', 'Infinitely many (identity) · عدد لا نهائي']]}],
     hint: 'h: 6 marks · check value: 2 marks · type: 2 marks',
     work: tex('4h+12-5=52-h\\Rightarrow 4h+7=52-h\\Rightarrow 5h=45\\Rightarrow h=9') + '<br>' + tex('\\text{Check: }4(12)-5=43,\\ 52-9=43\\ \\checkmark\\ \\text{one solution}'), answerText: 'h = 9, both sides 43, one solution'},
    {lo: 'LO26', title: 'Arithmetic nth term', en: 'Find the common difference of the arithmetic sequence, then find the next three terms.', ar: 'أوجد أساس المتتابعة الحسابية، ثم أوجد الحدود الثلاثة التالية.', math: '7,\\ 3,\\ -1,\\ -5,\\ldots',
     body: `<p class="fill">(a) ${tex('d=')} [[num:w14d]]</p><p class="fill">(b) Next three terms: [[num:w14a]] , [[num:w14b]] , [[num:w14c]]</p>`,
     fields: [{id: 'w14d', kind: 'num', answer: d, pts: 4, label: 'common difference'}, ...next.map((v, k) => ({id: 'w14' + 'abc'[k], kind: 'num', answer: v, pts: 2, label: `term ${5 + k}`}))],
     hint: 'd: 4 marks · each term: 2 marks', work: tex('d=3-7=-4;\\ -5-4=-9,\\ -13,\\ -17'), answerText: 'd = −4; −9, −13, −17'},
  ],
});
