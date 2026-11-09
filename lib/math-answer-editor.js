import {MathfieldElement} from 'mathlive';

// Serve fonts locally so the editor also works in the packaged site.
MathfieldElement.fontsDirectory = `${import.meta.env?.BASE_URL || '/'}vendor/mathlive/fonts`;
MathfieldElement.soundsDirectory = null;

const templates = {
  fraction: '\\frac{#@}{#?}',
  power: '{#@}^{#?}',
  root: '\\sqrt{#@}',
  nthroot: '\\sqrt[#?]{#@}',
  subscript: '{#@}_{#?}',
  brackets: '\\left(#@\\right)',
  pi: '\\pi',
  infinity: '\\infty',
  le: '\\le',
  ge: '\\ge',
};

export function initMathAnswerEditors(area, drafts, questionId) {
  area.querySelectorAll('.math-answer-editor').forEach(editor => {
    const field = editor.querySelector('math-field');
    const index = field.dataset.writing;
    field.mathVirtualKeyboardPolicy = 'manual';
    field.value = drafts[questionId]?.parts?.[index] || '';
    field.addEventListener('input', () => {
      const draft = (drafts[questionId] ||= {});
      (draft.parts ||= {})[index] = field.value;
    });
    editor.querySelectorAll('[data-math-template]').forEach(button => {
      // Keep the current selection in the field when a mouse or touch button is pressed.
      button.addEventListener('pointerdown', e => e.preventDefault());
      button.addEventListener('click', () => {
        field.focus();
        field.insert(templates[button.dataset.mathTemplate], {focus:true, selectionMode:'placeholder'});
      });
    });
    editor.querySelector('[data-math-keyboard]').addEventListener('click', () => {
      field.focus();
      window.mathVirtualKeyboard?.show();
    });
  });
}
