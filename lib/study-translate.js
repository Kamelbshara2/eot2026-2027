// Arabic translation lookup for question text. Keys are the English text with every number replaced by '#'.
const NUM = /-?\d+(?:\.\d+)?/g;
export const translationKey = s => String(s ?? '').trim().replace(NUM, '#');
export function translate(table, kind, text) {
  const ar = table?.[kind]?.[translationKey(text)];
  if (!ar) return '';
  const nums = String(text).match(NUM) || [];
  let i = 0;
  return ar.replace(/#/g, () => nums[i++] ?? '#').replace(/\{(\d)\}/g, (m, n) => nums[n - 1] ?? m);
}

// Keep Latin/maths fragments (e.g. "△ABC ∼ △DEF", "x=5", "A(2, 3)") left-to-right inside Arabic sentences.
const LTR_RUN = /[A-Za-z△∠√½][A-Za-z0-9△∠∼°′=+×÷/^²³().,\-−√·½±≤≥ ]*[A-Za-z0-9△°)′²³]/g;
// HTML entities (&lt; &quot; &amp; …) are protected first so a Latin-looking entity name is never wrapped.
export const bidi = html => {
  const held = [];
  const safe = String(html).replace(/&(?:[a-z]+|#\d+|#x[0-9a-f]+);/gi, m => `\u0002${held.push(m) - 1}\u0003`);
  return safe.replace(LTR_RUN, run => `<bdi dir="ltr">${run}</bdi>`).replace(/\u0002(\d+)\u0003/g, (_, i) => held[Number(i)]);
};

// An answer option needs an Arabic subtitle when it carries written words (not only an expression or numbers).
export const isProseOption = o => !o.math_latex || /\\text\{[^}]*[A-Za-z]{3}/.test(o.math_latex)
  || /[A-Za-z]{4,}/.test(String(o.math_latex).replace(/\\(begin|end)\{[^}]*\}/g, '').replace(/\\[A-Za-z]+/g, ''));
