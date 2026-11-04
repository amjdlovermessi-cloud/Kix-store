from pathlib import Path
import sys
site=Path(sys.argv[1]); root=Path(__file__).resolve().parent.parent
for name in ('kix-public-features.js','kix-public-features.css','kix-admin-reviews.js','kix-mascot-3d.js','kix-mascot-3d.css'):
    src=root/name
    if not src.exists(): raise SystemExit(f'Missing {src}')
    (site/name).write_bytes(src.read_bytes())
index=site/'index.html'; html=index.read_text(encoding='utf-8')
if 'kix-mascot-3d.css' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-mascot-3d.css"><script type="module" src="kix-mascot-3d.js"></script></head>',1)
if 'kix-public-features.css' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-public-features.css"><script src="kix-public-features.js" defer></script></head>',1)
if 'id="kixPublicStats"' not in html:
    section='''<section class="wrap kix-public-panel" id="kixPublicStats"><span class="eyebrow">KIX COMMUNITY</span><h2>أرقام المتجر وآراء الزبائن</h2><div class="kix-stat-grid"><div class="kix-stat"><strong id="kixVisits">—</strong><span>زيارة مسجلة</span></div><div class="kix-stat"><strong id="kixOrders">—</strong><span>طلب مكتمل أو قيد التجهيز</span></div><div class="kix-stat"><strong id="kixAverage">—</strong><span>متوسط التقييم</span></div><div class="kix-stat"><strong id="kixRatings">—</strong><span>تقييم منشور</span></div></div></section><section class="wrap kix-public-panel" id="kixReviews"><span class="eyebrow">CUSTOMER VOICES</span><h2>تقييمات وتجارب الزبائن</h2><div class="kix-review-layout"><div id="kixReviewList" class="kix-review-list"><p class="kix-empty">جاري تحميل التقييمات...</p></div><form id="kixReviewForm" class="kix-review-form"><h3>شاركنا رأيك</h3><label>الاسم الظاهر<input name="display_name" required minlength="2" maxlength="60" placeholder="اسم مستعار أو اسمك"></label><label>التقييم<select name="rating" required><option value="5">5 نجوم</option><option value="4">4 نجوم</option><option value="3">3 نجوم</option><option value="2">نجمتان</option><option value="1">نجمة واحدة</option></select></label><label>تعليقك<textarea name="comment" required minlength="8" maxlength="700" rows="4" placeholder="اكتب تجربتك مع KIX..."></textarea></label><button class="btn primary" type="submit">إرسال التقييم</button><p id="kixReviewMessage" class="kix-review-message">التقييمات تُراجع قبل ظهورها للعامة.</p></form></div></section>'''
    html=html.replace('    <section class="contact-section wrap"',section+'\n    <section class="contact-section wrap"',1)
index.write_text(html,encoding='utf-8')
owner=site/'owner.html'; html=owner.read_text(encoding='utf-8')
if 'kix-admin-reviews.js' not in html:
    html=html.replace('<script src="admin.js" defer></script>','<script src="admin.js" defer></script><link rel="stylesheet" href="kix-public-features.css"><script src="kix-admin-reviews.js" defer></script>',1)
owner.write_text(html,encoding='utf-8')
print('Public statistics and review UI patched.')
