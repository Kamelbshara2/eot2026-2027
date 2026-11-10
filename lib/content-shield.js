// Content shield: no context menu, and an immediate blur layer whenever the page loses focus
// (app switch, notification shade, tab change, screenshot gestures) so questions cannot be captured.
// A browser cannot truly stop OS screenshots; this removes the page from view at the moment the OS takes focus.
export function isBlockedKey(e) {
  const code = String(e.code || '');
  const k = (code.startsWith('Key') ? code.slice(3) : code.startsWith('Digit') ? code.slice(5) : String(e.key || '')).toLowerCase(), mod = e.ctrlKey || e.metaKey;
  if (e.altKey && e.metaKey && ['i', 'j', 'c', 'u'].includes(k)) return true;           // macOS devtools / source
  if (k === 'printscreen' || k === 'f12' || String(e.key) === 'F12') return true;
  if (e.metaKey && e.shiftKey && ['3', '4', '5', 's'].includes(k)) return true;       // macOS screenshots
  if (e.metaKey && e.shiftKey && k === 's') return true;                               // Windows snipping (Win+Shift+S)
  if (mod && e.shiftKey && ['i', 'j', 'c', 's'].includes(k)) return true;              // devtools / save
  if (mod && ['s', 'u'].includes(k)) return true;                                      // save / view-source
  return false;
}
const editable = t => !!(t && t.closest && t.closest('input,textarea,[contenteditable="true"]'));

export function installContentShield(doc = document, win = window) {
  if (doc.__shield) return doc.__shield;
  const root = doc.documentElement;
  const cover = doc.createElement('div');
  cover.className = 'shield-cover'; cover.setAttribute('role', 'alert'); cover.hidden = true;
  cover.innerHTML = '<div><strong>المحتوى محمي</strong><span>عُد إلى هذه الصفحة لمتابعة الدراسة</span></div>';
  doc.body.appendChild(cover);
  let away = false;
  const hide = () => { away = true; root.classList.add('shield-away'); cover.hidden = false; };
  const show = () => { if (doc.hidden || !doc.hasFocus()) return; away = false; root.classList.remove('shield-away'); cover.hidden = true; };
  const clear = () => { try { navigator.clipboard?.writeText(''); } catch { /* ignore */ } };
  doc.addEventListener('visibilitychange', () => (doc.hidden ? hide() : show()));
  win.addEventListener('blur', hide);
  win.addEventListener('pagehide', hide);
  win.addEventListener('focus', show);
  win.addEventListener('pageshow', show);
  doc.addEventListener('pointerdown', () => { if (away) show(); }, true);
  doc.addEventListener('contextmenu', e => e.preventDefault(), true);
  doc.addEventListener('dragstart', e => e.preventDefault(), true);
  doc.addEventListener('copy', e => { if (!editable(e.target)) e.preventDefault(); }, true);
  doc.addEventListener('cut', e => { if (!editable(e.target)) e.preventDefault(); }, true);
  doc.addEventListener('selectstart', e => { if (!editable(e.target)) e.preventDefault(); }, true);
  doc.addEventListener('keydown', e => { if (isBlockedKey(e)) { e.preventDefault(); hide(); } }, true);
  doc.addEventListener('keyup', e => { if (String(e.key).toLowerCase() === 'printscreen') { clear(); hide(); } }, true);
  win.addEventListener('beforeprint', () => { if (!doc.querySelector('.print-sheet')) hide(); });
  if (doc.hidden || !doc.hasFocus()) hide();
  doc.__shield = {hide, show, isAway: () => away};
  return doc.__shield;
}
