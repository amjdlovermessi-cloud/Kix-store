from pathlib import Path
import sys

site = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parent.parent
for name in ('kix-payment-experience.js', 'kix-payment-experience.css'):
    source = root / name
    if not source.is_file():
        raise SystemExit(f'KIX payment patch: missing asset {source}')
    (site / name).write_bytes(source.read_bytes())
index = site / 'index.html'
store = site / 'store.js'
if not index.is_file() or not store.is_file():
    raise SystemExit('KIX payment patch: index.html or store.js missing')
html = index.read_text(encoding='utf-8')
a = html.find('<dialog id="checkoutDialog"')
b = html.find('</dialog>', a)
if a < 0 or b < 0:
    raise SystemExit('KIX payment patch: checkout dialog not found')
b += len('</dialog>')
checkout = '''<dialog id="checkoutDialog" class="modal kix-checkout-modal"><form id="checkoutForm">
<div class="modal-head"><div><span class="kix-checkout-kicker">KIX SECURE CHECKOUT</span><h2>إكمال الطلب</h2></div><button type="button" class="close-modal" data-close="checkoutDialog" aria-label="إغلاق">✕</button></div>
<div class="kix-checkout-steps"><span class="is-active"><b>01</b> بياناتك</span><i></i><span class="is-active"><b>02</b> الدفع</span><i></i><span><b>03</b> تأكيد الطلب</span></div>
<div aria-hidden="true" style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden"><label>اترك هذا الحقل فارغاً<input name="website" type="text" tabindex="-1" autocomplete="off"></label></div>\n<section class="kix-checkout-section"><div class="kix-section-heading"><b>01</b><div><strong>معلومات التواصل</strong><small>حتى نكدر نتابع طلبك ونسلّمك المنتج</small></div></div>
<div class="form-grid"><label>الاسم الكامل<input name="customer_name" required maxlength="100" placeholder="اكتب اسمك"></label><label>رقم الهاتف<input name="phone" required maxlength="30" inputmode="tel" placeholder="07xxxxxxxxx"></label><label class="wide">البريد الإلكتروني <small>(اختياري)</small><input name="email" type="email" placeholder="name@example.com"></label><label class="wide">ملاحظات الطلب <small>(اختياري)</small><textarea name="notes" rows="2" placeholder="أي تفاصيل إضافية عن طلبك..."></textarea></label></div></section>
<section class="kix-checkout-section"><div class="kix-section-heading"><b>02</b><div><strong>اختَر طريقة الدفع</strong><small>وسائل الدفع المتاحة حالياً</small></div></div>
<div class="kix-payment-options">
<button type="button" class="kix-payment-option is-selected" data-payment-select="asiacell"><span class="kix-payment-logo asia">A</span><span><strong>آسياسيل</strong><small>تحويل محلي داخل العراق</small></span><i>✓</i></button>
<button type="button" class="kix-payment-option" data-payment-select="superqi"><span class="kix-payment-logo super">Q</span><span><strong>سوبر كي</strong><small>تحويل عبر Super Qi</small></span><i>✓</i></button>
<button type="button" class="kix-payment-option" data-payment-select="dizly"><span class="kix-payment-logo dizly">D</span><span><strong>Dizly</strong><small>للزبائن خارج العراق</small></span><i>✓</i></button></div>
<select name="payment_method" id="paymentMethod" class="kix-native-payment" required aria-label="طريقة الدفع"><option value="asiacell">آسياسيل</option><option value="superqi">سوبر كي</option><option value="dizly">Dizly</option></select>
<div id="paymentInstructions" class="payment-instructions"></div>
<label class="kix-proof-upload"><span class="kix-proof-icon">↑</span><span><strong>إرفاق إثبات التحويل</strong><small>صورة JPG أو PNG أو WEBP، بحد أقصى 5MB</small></span><input id="kixPaymentProof" type="file" accept="image/png,image/jpeg,image/webp"><b id="kixProofName">اختيار صورة</b></label>
<div id="kixProofPreview" class="kix-proof-preview" hidden><img id="kixProofImage" alt="معاينة إثبات التحويل"><span id="kixProofLabel"></span><button type="button" id="kixRemoveProof">إزالة</button></div>
<input type="hidden" name="receipt_mime"><input type="hidden" name="receipt_data">
<p class="fine-print">يتم التحقق من التحويل يدوياً. إرفاق الإثبات يساعدنا على مراجعة طلبك، ولا يعني أن الدفع تأكد تلقائياً.</p></section>
<button class="btn primary full kix-submit-order" type="submit" id="submitOrder">تأكيد الطلب والمتابعة <span>←</span></button><p class="kix-checkout-secure">🔒 بياناتك تُستخدم لمعالجة الطلب والتواصل بشأنه فقط.</p>
</form></dialog>'''
html = html[:a] + checkout + html[b:]
if 'href="payment.html"' not in html:
    html = html.replace('<footer class="footer">', '<section class="kix-payment-page-link"><a href="payment.html">تعرّف على طرق الدفع المتاحة <span>←</span></a></section><footer class="footer">', 1)
if '</footer>' in html and 'kix-footer-payment-methods' not in html:
    footer = """<div class="kix-footer-payment-methods" aria-label="طرق الدفع المتاحة"><span class="kix-footer-payment-title">طرق الدفع</span><span class="kix-footer-payment-item"><img class="kix-payment-brand asia" src="https://www.asiacell.com/assets/ac-logo.svg" alt="Asiacell"><b>آسياسيل</b></span><span class="kix-footer-payment-item"><img class="kix-payment-brand super" src="https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/9f/74/3c/9f743c5f-8bb4-f7f7-3f98-3c5b39135be5/AppIcon-0-0-1x_U007ephone-0-1-0-sRGB-85-220.png/1200x630wa.png" alt="SuperQi"><b>سوبر كي</b></span><span class="kix-footer-payment-item"><img class="kix-payment-brand dizly" src="https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/5e/47/e6/5e47e63c-58ca-244a-102c-1fbe1007e811/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/1200x630wa.png" alt="Dizly"><b>Dizly</b></span><span class="kix-footer-payment-item"><img class="kix-payment-brand usdt" src="https://cdn.simpleicons.org/tether/26A17B" alt="USDT"><b>USDT</b></span><span class="kix-footer-payment-item"><img class="kix-payment-brand ton" src="https://cdn.simpleicons.org/ton/0098EA" alt="TON"><b>TON</b></span></div>"""
    html = html.replace('</footer>', footer + '</footer>', 1)
if 'kix-payment-experience.js' not in html:
    html = html.replace('<script src="store.js" defer></script>', '<script src="store.js" defer></script><link rel="stylesheet" href="kix-payment-experience.css?v=20261128-2"><script src="kix-payment-experience.js?v=20261128-2" defer></script>', 1)
html = html.replace('kix-payment-experience.js?v=20261128-1','kix-payment-experience.js?v=20261128-2').replace('kix-payment-experience.css?v=20261128-1','kix-payment-experience.css?v=20261128-2')
index.write_text(html, encoding='utf-8')
js_path = site / 'store.js'
js = js_path.read_text(encoding='utf-8')
old = "payment_method:f.get('payment_method'),website:f.get('website'),items"
new = "payment_method:f.get('payment_method'),website:f.get('website'),receipt_mime:f.get('receipt_mime'),receipt_data:f.get('receipt_data'),items"
if new not in js:
    if old not in js:
        raise SystemExit('KIX payment patch: order payload insertion point not found')
    js = js.replace(old, new, 1)
js_path.write_text(js, encoding='utf-8')
payment = site / 'payment.html'
if payment.exists():
    phtml = payment.read_text(encoding='utf-8')
    start = phtml.find('<article class="kix-policy-card">')
    end = phtml.find('</article>', start)
    if start >= 0 and end >= 0:
        body = '''<article class="kix-policy-card kix-payment-methods-page"><span class="eyebrow">PAYMENT METHODS</span><h1>طرق الدفع المتاحة</h1><p>اختَر الوسيلة المناسبة إلك. تظهر تفاصيل التحويل داخل صفحة إتمام الطلب حتى تستخدم أحدث بيانات الاستلام.</p>
<div class="kix-methods-grid">
<div class="kix-method-card"><span class="kix-payment-logo asia">A</span><h2>آسياسيل</h2><p>تحويل محلي داخل العراق. يظهر رقم التحويل عند اختيار آسياسيل أثناء إتمام الطلب.</p><small>متاح داخل العراق</small></div>
<div class="kix-method-card"><span class="kix-payment-logo super">Q</span><h2>سوبر كي</h2><p>الدفع عبر Super Qi أو البطاقة داخل العراق باستخدام رقم الاستلام المعروض في صفحة الدفع.</p><small>متاح داخل العراق</small></div>
<div class="kix-method-card"><span class="kix-payment-logo dizly">D</span><h2>Dizly</h2><p>وسيلة دفع للزبائن خارج العراق. استخدم معرّف الاستلام الظاهر بعد اختيارها.</p><small>للزبائن خارج العراق</small></div>
</div><div class="kix-payment-note"><strong>مهم قبل التحويل</strong><p>أرسل الطلب أولاً، ثم حوّل المبلغ وأرفق صورة إثبات التحويل. تتم مراجعة الدفع يدوياً قبل تسليم المنتج.</p></div><a class="kix-policy-back" href="index.html#products">العودة للمتجر واختيار منتج</a></article>'''
        phtml = phtml[:start] + body + phtml[end + len('</article>'):]
        phtml = phtml.replace('</head>', '<link rel="stylesheet" href="kix-payment-experience.css?v=20261128-2"></head>', 1)
        payment.write_text(phtml, encoding='utf-8')
print('KIX payment experience installed.')
