import katex from 'katex';
export function normalizeStudyMath(value) {
 const source = String(value ?? '');
 try {
  katex.renderToString(source, {throwOnError:true,strict:'ignore'});
  return source;
 } catch {
  return source.replaceAll(String.fromCharCode(92,92),String.fromCharCode(92));
 }
}
