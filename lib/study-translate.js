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
