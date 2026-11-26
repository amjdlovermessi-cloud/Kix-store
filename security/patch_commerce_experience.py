from pathlib import Path
import sys

site = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parent
if not (site / "index.html").is_file():
    raise SystemExit("KIX commerce patch: index.html missing")

for name in ("kix-commerce-enhancements.js", "kix-commerce-enhancements.css"):
    source = root / name
    if not source.is_file():
        raise SystemExit(f"Missing commerce asset: {source}")
    (site / name).write_bytes(source.read_bytes())

index = site / "index.html"
html = index.read_text(encoding="utf-8")
css_tag = '<link rel="stylesheet" href="kix-commerce-enhancements.css?v=20261126-1">'
js_tag = '<script src="kix-commerce-enhancements.js?v=20261126-1" defer></script>'
if "kix-commerce-enhancements.css" not in html:
    html = html.replace("</head>", css_tag + "\n</head>", 1)
if "kix-commerce-enhancements.js" not in html:
    html = html.replace("</head>", js_tag + "\n</head>", 1)

trust = """<section class="wrap kix-trust-panel" id="kixTrustAndPolicies">
<div><span class="eyebrow">SHOP WITH CLARITY</span><h2>كل التفاصيل المهمة، <em>قبل الشراء</em></h2><p>اقرأ شروط المنتج والدفع والضمان حتى تعرف شنو تشتري، شلون تستلمه، وشنو حقوقك إذا صار خلل.</p></div>
<nav aria-label="معلومات المتجر"><a href="guarantee.html">الضمان والاسترداد</a><a href="payment.html">طرق الدفع والاستلام</a><a href="faq.html">الأسئلة الشائعة</a><a href="about.html">من نحن</a><a href="contact.html">تواصل معنا</a></nav></section>"""
if 'id="kixTrustAndPolicies"' not in html and '<section class="contact-section' in html:
    html = html.replace('<section class="contact-section', trust + '\n<section class="contact-section', 1)

footer_links = '<nav class="kix-footer-links" aria-label="روابط المتجر"><a href="about.html">من نحن</a><a href="guarantee.html">الضمان والاسترداد</a><a href="payment.html">طرق الدفع</a><a href="faq.html">الأسئلة الشائعة</a><a href="contact.html">اتصل بنا</a></nav>'
if 'class="kix-footer-links"' not in html:
    html = html.replace('<small>©', footer_links + '<small>©', 1)
index.write_text(html, encoding="utf-8")

pages = {
"guarantee.html": {
"title": "سياسة الضمان والاسترداد",
"desc": "شروط الضمان والاستبدال والاسترداد في KIX Store.",
"body": """<p class="kix-policy-note">نريد أن تكون شروط كل منتج واضحة قبل الدفع. تختلف مدة الضمان وطريقة التسليم بحسب نوع المنتج ومصدره، لذلك اقرأ وصف المنتج وأي شروط خاصة به قبل إتمام الطلب.</p>
<h2>متى يشملك الضمان؟</h2><ul><li>إذا كان المنتج الذي استلمته مختلفاً جوهرياً عن الوصف أو المواصفات المعروضة.</li><li>إذا كان الكود أو بيانات التسليم غير صالحة عند التسليم، بعد التحقق من الحالة وعدم وجود استخدام أو تغيير من طرف المشتري.</li><li>إذا لم نتمكن من توفير المنتج المتفق عليه، تتم معالجة الطلب باستبدال مناسب أو استرداد المبلغ بحسب الحالة.</li></ul>
<h2>شلون تقدم طلب ضمان؟</h2><p>تواصل ويانا عبر قنوات الدعم، واذكر رقم الطلب وأرفق وصف المشكلة وصورة أو تسجيل شاشة عند الحاجة. يُفضّل إرسال البلاغ خلال 24 ساعة من الاستلام، أو ضمن المدة المحددة في وصف المنتج إذا كانت مختلفة.</p>
<h2>متى قد لا يشمل الضمان؟</h2><ul><li>مشاركة بيانات الدخول أو الكود مع أشخاص آخرين أو تغيير بيانات الحساب بعد التسليم.</li><li>استخدام المنتج بطريقة تخالف تعليمات البائع أو شروط الخدمة ذات الصلة.</li><li>تغيير المنطقة أو المنصة أو إعدادات الحساب خلافاً لما هو موضح في وصف المنتج.</li><li>تلف أو انتهاء صلاحية ناتج عن استخدام صحيح بعد التسليم، إذا كان ذلك موضحاً مسبقاً في تفاصيل المنتج.</li></ul>
<h2>الاسترداد</h2><p>إذا ثبت وجود خلل مشمول بالضمان وتعذر الاستبدال أو لم يكن الاستبدال مناسباً، نراجع خيار استرداد المبلغ إلى وسيلة الدفع المتاحة. لا نستخدم عبارة «لا استرداد» لإلغاء حقوق العميل في حال وجود منتج معيب أو غير مطابق.</p>
<h2>ملاحظة مهمة</h2><p>لا نضمن استمرار حساب أو اشتراك لدى منصة خارجية إذا كانت شروط المنصة أو قراراتها تؤثر في الخدمة، إلا بالقدر الذي يلتزم به وصف المنتج والضمان المعلن. لا تعرض KIX Store أي منتج على أنه رسمي أو معتمد ما لم يُذكر ذلك ويمكن إثباته.</p>"""
},
"payment.html": {
"title": "طرق الدفع والاستلام",
"desc": "تعرف على آلية الدفع وتأكيد الطلب واستلام المنتجات الرقمية.",
"body": """<p>تظهر وسائل الدفع المتاحة وتفاصيل التحويل داخل نافذة إتمام الطلب. اختر الوسيلة المناسبة واتبع التعليمات الظاهرة وقت الشراء، لأن بيانات الاستلام قد تتغير.</p>
<h2>خطوات الدفع</h2><ol><li>أضف المنتجات إلى السلة وتأكد من السعر النهائي بالدينار العراقي.</li><li>أدخل اسمك ورقم هاتفك وأرسل الطلب.</li><li>حوّل المبلغ باستخدام وسيلة الدفع المختارة، ثم أرسل رقم الطلب وإثبات التحويل عبر قناة الدعم.</li><li>تتم مراجعة التحويل يدوياً، وبعد تأكيده تتواصل الإدارة معك لإتمام التسليم.</li></ol>
<h2>هل التسليم فوري؟</h2><p>إنشاء الطلب يتم إلكترونياً، لكن تأكيد الدفع والتسليم قد يحتاجان إلى مراجعة يدوية. لذلك لا نعد بالتسليم الفوري على مدار الساعة ما لم يظهر ذلك صراحةً على المنتج وكانت آلية التسليم الآلي مفعّلة له.</p>
<h2>ماذا لو دفعت ولم يتغير الطلب؟</h2><p>احتفظ بإثبات التحويل وتواصل معنا مع رقم الطلب ورقم الهاتف المستخدم. لا ترسل بيانات بطاقتك السرية أو كلمة مرور تطبيق الدفع لأي شخص.</p>
<h2>الأسعار والعملة</h2><p>السعر النهائي المعروض في صفحة المنتج والسلة هو المرجع عند إنشاء الطلب. إذا ظهر سعر مختلف بين الصفحة ومرحلة الدفع، أوقف العملية وتواصل مع الدعم قبل التحويل.</p>"""
},
"faq.html": {
"title": "الأسئلة الشائعة",
"desc": "إجابات عن الشراء والحسابات والدفع والتسليم والضمان.",
"body": """<h2>هل أحتاج إلى إنشاء حساب؟</h2><p>لا. تقدر تتصفح وتشتري كضيف. إنشاء الحساب اختياري ويساعدك على متابعة طلباتك وإحصائيات مشترياتك عندما تكون الطلبات مرتبطة بحسابك.</p>
<h2>شلون أطلب؟</h2><p>اختَر المنتج، أضفه إلى السلة، أدخل الاسم ورقم الهاتف، ثم أرسل الطلب واتبع تعليمات الدفع الظاهرة.</p>
<h2>متى أستلم المنتج؟</h2><p>بعد مراجعة الدفع وتأكيده. وقت التسليم يختلف حسب نوع المنتج وتوفره وساعات الدعم، ويُفضّل مراجعة وصف المنتج.</p>
<h2>وين ألقى رقم الطلب؟</h2><p>يظهر بعد تسجيل الطلب بنجاح. احتفظ به واستخدمه عند التواصل مع الدعم.</p>
<h2>هل كل المنتجات رسمية؟</h2><p>لا نفترض ذلك تلقائياً. اقرأ وصف كل منتج لمعرفة طبيعته وطريقة التسليم وأي قيود أو شروط تخصه. لا تعتمد على كلمة «رسمي» ما لم تكن مذكورة بوضوح.</p>
<h2>شلون أطلب ضمان؟</h2><p>راجع <a href="guarantee.html">سياسة الضمان والاسترداد</a> ثم تواصل معنا مع رقم الطلب وتفاصيل المشكلة.</p>
<h2>هل يمكن إلغاء الطلب؟</h2><p>إذا لم يبدأ تنفيذ الطلب أو التسليم بعد، تواصل معنا بأسرع وقت. بعد تسليم كود أو بيانات رقمية، تُراجع طلبات الإلغاء وفق حالة المنتج وسياسة الضمان.</p>"""
},
"about.html": {
"title": "من نحن",
"desc": "تعرف على KIX Store وتجربة التسوق الرقمية.",
"body": """<p>KIX Store متجر للمنتجات الرقمية والألعاب والاشتراكات وبطاقات الشحن. هدفنا أن نجمع خيارات رقمية متنوعة في مكان واحد مع عرض مفهوم للأسعار وتفاصيل المنتج وخطوات الطلب.</p>
<h2>وضوح قبل الشراء</h2><p>نحرص على توضيح نوع المنتج وطريقة التسليم والقيود ومدة الضمان المتاحة لكل منتج. إذا كانت معلومة أساسية غير واضحة، اسأل فريق الدعم قبل الدفع.</p>
<h2>خدمة العملاء</h2><p>نستقبل استفسارات الطلبات ومشكلات التسليم عبر قنوات التواصل المنشورة في صفحة <a href="contact.html">اتصل بنا</a>.</p>
<h2>مهم تعرف</h2><p>KIX Store متجر مستقل، ولا يعني عرض منتج تابع لعلامة أو منصة خارجية وجود شراكة أو اعتماد رسمي منها، إلا إذا ذُكر ذلك صراحةً وبشكل قابل للتحقق.</p>"""
},
"contact.html": {
"title": "تواصل معنا",
"desc": "قنوات التواصل مع دعم KIX Store.",
"body": """<p>إذا عندك سؤال قبل الشراء أو تحتاج متابعة طلب، جهّز رقم الطلب إن وجد، ثم تواصل عبر إحدى القنوات التالية.</p>
<div class="kix-policy-links"><a href="https://wa.me/9647751689317" target="_blank" rel="noopener">الدعم عبر واتساب</a><a href="https://t.me/kixstore1" target="_blank" rel="noopener">الدعم عبر تلغرام</a></div>
<h2>حتى نخدمك أسرع</h2><ul><li>أرسل رقم الطلب.</li><li>اشرح المشكلة باختصار.</li><li>أرفق إثبات الدفع أو صورة الخطأ عند الحاجة.</li><li>لا ترسل كلمات المرور أو رموز التحقق أو بيانات البطاقة السرية.</li></ul>"""
}
}
template = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#09090d"><meta name="description" content="{desc}"><title>{title} | KIX Store</title><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="kix-commerce-enhancements.css"></head><body><div class="announcement">KIX STORE <b>✦</b> معلومات واضحة وتجربة شراء أسهل</div><header class="site-header"><div class="header-inner"><a class="brand" href="index.html"><img src="assets/kix-logo.png" alt="KIX Store"><span>KIX <b>STORE</b></span></a><nav class="main-nav"><a href="index.html">الرئيسية</a><a href="index.html#products">المنتجات</a><a href="guarantee.html">الضمان</a><a href="payment.html">الدفع</a><a href="contact.html">تواصل معنا</a></nav><a class="btn ghost" href="index.html#products">العودة للمتجر</a></div></header><main class="kix-policy-page"><article class="kix-policy-card"><span class="eyebrow">KIX STORE · CUSTOMER INFORMATION</span><h1>{title}</h1>{body}<a class="kix-policy-back" href="index.html">← العودة إلى المتجر</a></article></main><footer class="footer"><div class="wrap footer-inner"><a class="brand" href="index.html"><img src="assets/kix-logo.png" alt=""><span>KIX <b>STORE</b></span></a><nav class="kix-footer-links"><a href="about.html">من نحن</a><a href="guarantee.html">الضمان والاسترداد</a><a href="payment.html">طرق الدفع</a><a href="faq.html">الأسئلة الشائعة</a><a href="contact.html">اتصل بنا</a></nav><small>© KIX Store</small></div></footer></body></html>"""
for filename, data in pages.items():
    page = template.format(title=data["title"], desc=data["desc"], body=data["body"])
    (site / filename).write_text(page, encoding="utf-8")

print("KIX commerce experience installed: product sorting/details, trust links, and 5 policy pages.")
