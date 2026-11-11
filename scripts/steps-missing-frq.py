#!/usr/bin/env python3
"""Worked steps for the last written parts that had none (teacher request 2026-11-11)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def S(t, a, l, w, wa): return {'text': t, 'ar': a, 'latex': l, 'why': w, 'why_ar': wa}
STEPS = {
 ('9G3', 'G9G-BOOK-Q24-FRQ-03', 'a'): [
  S('Choose easy x-values (even numbers, because of the ½).', 'اختر قيماً سهلة لـ x (أعداداً زوجية بسبب ½).', r'x=-2,\ 0,\ 2', 'Even x-values make ½x a whole number.', 'القيم الزوجية تجعل ½x عدداً صحيحاً.'),
  S('Substitute each x into y = ½x + 1.', 'عوّض كل قيمة x في y = ½x + 1.', r'y(-2)=0,\ y(0)=1,\ y(2)=2', 'Each pair (x, y) is a point on the line.', 'كل زوج (x, y) نقطة على المستقيم.'),
  S('Plot (−2, 0), (0, 1), (2, 2) and draw one straight line through them with arrows on both ends.', 'مثّل النقاط (−2, 0) و (0, 1) و (2, 2) وارسم مستقيماً واحداً يمر بها مع أسهم في الطرفين.', r'y=\tfrac12x+1', 'If the three points are not in a straight line, recheck the table.', 'إذا لم تقع النقاط الثلاث على استقامة واحدة فراجع الجدول.')],
 ('10G3', 'G10G-Q23-FRQ-05', 'b'): [
  S('Enter each equation in the calculator (Table or graph mode) and look at the shape.', 'أدخل كل معادلة في الحاسبة (وضع الجدول أو الرسم) وانظر إلى الشكل.', r'y=x,\ y=x^2,\ y=x^3', 'Seeing the three side by side shows the difference between linear and nonlinear.', 'رؤية الثلاثة معاً توضح الفرق بين الخطي وغير الخطي.'),
  S('y = x: a straight line through the origin. y = x²: an upward parabola (U shape). y = x³: an increasing S-shaped curve through the origin.', 'y = x: مستقيم يمر بنقطة الأصل. y = x²: قطع مكافئ مفتوح لأعلى (شكل U). y = x³: منحنى متزايد على شكل S يمر بنقطة الأصل.', '', 'All three pass through (0, 0) and (1, 1), but only y = x keeps a constant slope.', 'الثلاثة تمر بـ (0, 0) و (1, 1)، لكن y = x وحده ميله ثابت.')],
 ('10G3', 'G10G-Q23-FRQ-05', 'd'): [
  S('Simplify the equation and look at the highest power of x.', 'بسّط المعادلة وانظر إلى أعلى أس لـ x.', '', 'The power of x decides the shape.', 'أس x هو ما يحدد الشكل.'),
  S('If it can be written as y = ax + b (x to the first power only), it is linear; x², x³, √x, 1/x make it nonlinear.', 'إذا أمكن كتابتها y = ax + b (x للقوة الأولى فقط) فهي خطية؛ أما x² و x³ و √x و 1/x فتجعلها غير خطية.', r'y=ax+b', 'Linear means a constant rate of change, which only the first power gives.', 'الخطية تعني معدل تغير ثابتاً، ولا يعطيه إلا الأس الأول.')]}
for (c, qid, pid), st in STEPS.items():
    p = ROOT / f'public/data/study/{c}.json'; b = json.loads(p.read_text())
    part = next(pt for q in b['questions'] if q['id'] == qid for pt in q['parts'] if pt['id'] == pid)
    part['answer']['steps'] = st; part['answer']['steps_verified'] = True
    p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':')))
print('done', len(STEPS))
