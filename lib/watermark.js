export const watermarkText='ألاستاذ كامل بشارة 0502837825';
export const questionWatermark=()=>`<div class="question-watermark" aria-hidden="true">${Array.from({length:3},()=>`<span lang="ar" dir="rtl">${watermarkText}</span>`).join('')}</div>`;
export const watermarkCss=`
.watermarked-question,.worksheet-print-page,.card,.visual-gallery{position:relative;isolation:isolate}
.watermarked-question{min-height:200px}
.question-watermark{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;justify-content:space-around;align-items:center;pointer-events:none;user-select:none;overflow:hidden;opacity:.12;color:#243e37;print-color-adjust:exact;-webkit-print-color-adjust:exact}
.question-watermark>span{display:block;flex-shrink:0;white-space:nowrap;font:600 clamp(14px,2.2vw,25px)/1.8 Arial,Tahoma,sans-serif;transform:rotate(-24deg);text-align:center}
.worksheet-print-page>.question-watermark{opacity:.13}
.worksheet-print-page>.question-watermark>span{font-size:23pt}
.card>.question-watermark>span{font-size:15px}
@media print{.question-watermark{display:flex!important;print-color-adjust:exact;-webkit-print-color-adjust:exact}}
`;
