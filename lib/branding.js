export const platformName='منصة الرياضيات 100 مع الاستاذ كامل';
export const contactNumber='0502837825';
export const platformContact=()=>`<a class="platform-contact" href="tel:${contactNumber}" aria-label="التواصل مع الأستاذ كامل على ${contactNumber}"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6.6 3.5 9 8 6.8 10.2a15 15 0 0 0 7 7L16 15l4.5 2.4v3a1 1 0 0 1-1.1 1C9.5 20.5 3.5 14.5 2.6 4.6a1 1 0 0 1 1-1.1Z"/></svg></span><span><small>للتواصل · Contact</small><b dir="ltr">${contactNumber}</b></span></a>`;
export const platformBrand=()=>`<a class="platform-brand" href="#/classrooms" aria-label="${platformName} — الصفحة الرئيسية"><span class="brand-symbol" aria-hidden="true">100<span>π</span></span><span><strong lang="ar" dir="rtl">${platformName}</strong><small>MATH 100 · LEARN. PRACTICE. ACHIEVE.</small></span></a>`;
export const classroomLabels={
 '10A1':{en:'Grade 10 Advanced',ar:'الصف العاشر المتقدم'},
 '10G3':{en:'Grade 10 General',ar:'الصف العاشر العام'},
 '9G3':{en:'Grade 9',ar:'الصف التاسع'}
};
