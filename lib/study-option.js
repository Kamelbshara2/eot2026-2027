// One answer option: optional picture (graph choices) followed by the maths or the text.
export const optionBody = (o, math, esc, base = '/', assets = {}) =>
  `${o.image && assets[o.image] ? `<img class="opt-img" loading="lazy" src="${base}${esc(assets[o.image].src)}" alt="${esc(assets[o.image].alt_text)}">` : ''}${o.math_latex ? math(o.math_latex) : esc(o.text)}`;
