from pathlib import Path
import re
import sys
site=Path(sys.argv[1]); root=Path(__file__).resolve().parent.parent
for name in ('kix-public-features.js','kix-public-features.css','kix-admin-reviews.js','kix-currency.js','kix-currency.css'):
    src=root/name
    if not src.exists(): raise SystemExit(f'Missing {src}')
    (site/name).write_bytes(src.read_bytes())
index=site/'index.html'; html=index.read_text(encoding='utf-8')
if 'kix-currency.js' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-currency.css"><script src="kix-currency.js" defer></script></head>',1)
if 'kix-public-features.css' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-public-features.css"><script src="kix-public-features.js" defer></script></head>',1)
if 'id="kixPublicStats"' not in html:
    section='''<section class="wrap kix-public-panel" id="kixPublicStats"><span class="eyebrow">KIX COMMUNITY</span><h2>أرقام المتجر وآراء الزبائن</h2><div class="kix-stat-grid"><div class="kix-stat"><strong id="kixVisits">—</strong><span>زيارة مسجلة</span></div><div class="kix-stat"><strong id="kixOrders">—</strong><span>طلب مكتمل أو قيد التجهيز</span></div><div class="kix-stat"><strong id="kixAverage">—</strong><span>متوسط التقييم</span></div><div class="kix-stat"><strong id="kixRatings">—</strong><span>تقييم منشور</span></div></div></section><section class="wrap kix-public-panel" id="kixReviews"><span class="eyebrow">CUSTOMER VOICES</span><h2>تقييمات وتجارب الزبائن</h2><div class="kix-review-layout"><div id="kixReviewList" class="kix-review-list"><p class="kix-empty">جاري تحميل التقييمات...</p></div><form id="kixReviewForm" class="kix-review-form"><h3>شاركنا رأيك</h3><label>الاسم الظاهر<input name="display_name" required minlength="2" maxlength="60" placeholder="اسم مستعار أو اسمك"></label><label>التقييم<select name="rating" required><option value="5">5 نجوم</option><option value="4">4 نجوم</option><option value="3">3 نجوم</option><option value="2">نجمتان</option><option value="1">نجمة واحدة</option></select></label><label>تعليقك<textarea name="comment" required minlength="8" maxlength="700" rows="4" placeholder="اكتب تجربتك مع KIX..."></textarea></label><button class="btn primary" type="submit">إرسال التقييم</button><p id="kixReviewMessage" class="kix-review-message">التقييمات تُراجع قبل ظهورها للعامة.</p></form></div></section>'''
    html=html.replace('    <section class="contact-section wrap"',section+'\n    <section class="contact-section wrap"',1)
store=site/'store.js'; store_js=store.read_text(encoding='utf-8')
old_money="""const $=s=>document.querySelector(s), money=n=>new Intl.NumberFormat('ar-IQ').format(Number(n||0))+' د.ع';"""
new_money="""const $=s=>document.querySelector(s), money=n=>{const amount=Number(n||0);return localStorage.getItem('kix-display-currency')==='USD'?'$'+(amount/1520).toFixed(2):new Intl.NumberFormat('ar-IQ').format(amount)+' د.ع'};"""
if old_money in store_js and 'kix-display-currency' not in store_js:
    store_js=store_js.replace(old_money,new_money,1)
elif 'kix-display-currency' not in store_js:
    raise SystemExit('Currency patch failed: original money() formatter was not found in store.js')
if "kix-currency-changed" not in store_js:
    marker="document.addEventListener('DOMContentLoaded',init);"
    listener="window.addEventListener('kix-currency-changed',()=>{if($('#productSearch')?.value||$('#categoryFilter')?.value)filterProducts();else renderProducts();renderCart();});\n"+marker
    if marker not in store_js:
        raise SystemExit('Currency patch failed: store initialization marker was not found')
    store_js=store_js.replace(marker,listener,1)
if 'kix-display-currency' not in store_js or 'kix-currency-changed' not in store_js:
    raise SystemExit('Currency patch verification failed: formatter or refresh listener is missing')
store.write_text(store_js,encoding='utf-8')
index.write_text(html,encoding='utf-8')
# Remove only the obsolete hint text. Never remove its parent HTML element:
# broad parent-tag matching can accidentally delete the mascot or product categories.
for candidate in site.rglob('*'):
    if candidate.is_file() and candidate.suffix.lower() in ('.html','.js','.css'):
        try:
            content=candidate.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        cleaned=content
        for phrase in (
            'أضغط على KIX حتى يسويلك حركة',
            'اضغط على KIX حتى يسويلك حركة',
            'أضغط على KIX حتى يسوي لك حركة',
            'اضغط على KIX حتى يسوي لك حركة',
        ):
            cleaned=cleaned.replace(phrase,'')
        cleaned=cleaned.replace('👋 أضغط على KIX','').replace('👋 اضغط على KIX','')
        if cleaned!=content:
            candidate.write_text(cleaned,encoding='utf-8')
# Remove only the mascot's greeting and flip-hint overlays from the deployed archive.
# Keep the mascot button, 3D canvas, animation loop, and flip click behavior intact.
mascot_targets=0
for candidate in site.rglob('*'):
    if not candidate.is_file() or candidate.suffix.lower() not in ('.html','.js','.css'):
        continue
    try:
        content=candidate.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    updated=content
    if candidate.suffix.lower() in ('.html','.js'):
        updated,n=re.subn(
            r"\n\s*const greeting\s*=\s*document\.createElement\('div'\);.*?button\.appendChild\(flipHint\);\s*",
            "\n  // Greeting and flip-hint overlays removed.\n  button.addEventListener('click',()=>{ if(!flipStart){ flipStart=performance.now(); } });\n",
            updated, count=1, flags=re.S
        )
        if n:
            mascot_targets+=1
        updated=re.sub(r"greeting\.textContent\s*=\s*(['"]).*?\1;", "", updated)
    if candidate.suffix.lower()=='.css':
        updated,n=re.subn(
            r"\n\.kix-mascot-greeting,\.kix-mascot-flip-hint\{.*?@keyframes kixGreetingPulse[^\n]*\n?",
            "\n",
            updated, count=1, flags=re.S
        )
        if n:
            mascot_targets+=1
    if updated!=content:
        candidate.write_text(updated,encoding='utf-8')
print(f'Mascot greeting/hint overlays removed in {mascot_targets} matching asset(s).')

owner=site/'owner.html'; html=owner.read_text(encoding='utf-8')
if 'kix-admin-reviews.js' not in html:
    html=html.replace('<script src="admin.js" defer></script>','<script src="admin.js" defer></script><link rel="stylesheet" href="kix-public-features.css"><script src="kix-admin-reviews.js" defer></script>',1)
owner.write_text(html,encoding='utf-8')
print('Public statistics and review UI patched.')
