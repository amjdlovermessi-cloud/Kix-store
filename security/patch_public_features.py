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
# Render fallback data immediately. A single stalled Supabase request (especially
# site_settings) must never keep both category and product sections on loaders.
load_start = store_js.find('async function loadData(){')
load_end = store_js.find('\nfunction renderCategories', load_start)
if load_start < 0 or load_end < 0:
    raise SystemExit('Could not locate loadData() safely.')
new_load = """async function loadData(){
  try{renderCategories();}catch(e){console.error('KIX fallback categories render failed',e);const el=$('#categoryGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض الأقسام: '+String(e&&e.message||e)+'</div>';}
  try{renderProducts();}catch(e){console.error('KIX fallback products render failed',e);const el=$('#productGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض المنتجات: '+String(e&&e.message||e)+'</div>';}
  try{renderCart();updatePaymentInfo();}catch(e){console.warn('KIX initial cart/payment render failed',e);}
  if(!sb){console.warn('KIX Supabase client unavailable; showing fallback catalog.');return;}
  const timed=(query,label)=>Promise.race([Promise.resolve(query),new Promise((_,reject)=>setTimeout(()=>reject(new Error(label+' request timed out')),10000))]);
  const results=await Promise.allSettled([
    timed(sb.from('categories').select('*').eq('active',true).order('sort_order'),'categories'),
    timed(sb.from('products').select('*').eq('active',true).order('sort_order'),'products'),
    timed(sb.from('site_settings').select('key,value'),'site_settings')
  ]);
  if(results[0].status==='fulfilled'&&!results[0].value.error&&results[0].value.data?.length){categories=results[0].value.data;try{renderCategories();}catch(e){console.error('KIX categories render failed',e);const el=$('#categoryGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض الأقسام: '+String(e&&e.message||e)+'</div>';}}
  else if(results[0].status==='rejected'||results[0].value?.error)console.warn('KIX categories query failed',results[0].reason||results[0].value.error);
  if(results[1].status==='fulfilled'&&!results[1].value.error&&results[1].value.data){products=results[1].value.data;try{renderProducts();}catch(e){console.error('KIX products render failed',e);const el=$('#productGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض المنتجات: '+String(e&&e.message||e)+'</div>';}}
  else if(results[1].status==='rejected'||results[1].value?.error)console.warn('KIX products query failed',results[1].reason||results[1].value.error);
  if(results[2].status==='fulfilled'&&!results[2].value.error&&results[2].value.data){results[2].value.data.forEach(x=>settings[x.key]=x.value);document.querySelectorAll('a[href^="https://wa.me/"]').forEach(a=>a.href='https://wa.me/'+settings.whatsapp_number);document.querySelectorAll('a[href^="https://t.me/"]').forEach(a=>a.href='https://t.me/'+settings.telegram_username);}
  else if(results[2].status==='rejected'||results[2].value?.error)console.warn('KIX settings query failed',results[2].reason||results[2].value.error);
  try{renderCart();updatePaymentInfo();}catch(e){console.warn('KIX final cart/payment render failed',e);}
}"""
store_js = store_js[:load_start] + new_load + store_js[load_end:]
# Render each storefront area independently so one UI exception cannot strand both loaders.
old_render = 'renderCategories();renderProducts();renderCart();updatePaymentInfo();'
new_render = """try{renderCategories()}catch(e){console.error('KIX categories render failed',e);const el=$('#categoryGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض الأقسام: '+String(e&&e.message||e)+'</div>';}try{renderProducts()}catch(e){console.error('KIX products render failed',e);const el=$('#productGrid');if(el)el.innerHTML='<div class="loading">خطأ عرض المنتجات: '+String(e&&e.message||e)+'</div>';}try{renderCart()}catch(e){console.error('KIX cart render failed',e)}try{updatePaymentInfo()}catch(e){console.error('KIX payment render failed',e)}"""
if old_render in store_js:
    store_js=store_js.replace(old_render,new_render,1)
else:
    print('Independent render guards already handled by loadData(); no legacy render sequence to patch.')
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
# Surface uncaught browser errors on the storefront instead of leaving a silent loader.
index=site/'index.html'
html=index.read_text(encoding='utf-8')
if 'id="kixRuntimeDiag"' not in html:
    diagnostic = """<script id="kixRuntimeDiag">
(()=>{const show=(kind,detail)=>{let box=document.getElementById('kixRuntimeDiagBox');if(!box){box=document.createElement('div');box.id='kixRuntimeDiagBox';box.style.cssText='position:fixed;z-index:2147483647;left:10px;right:10px;bottom:10px;padding:12px 14px;border:1px solid #ff5267;border-radius:12px;background:#160b10;color:#fff;font:13px/1.6 system-ui;direction:rtl;overflow-wrap:anywhere;box-shadow:0 8px 30px #0009';document.body.appendChild(box);}box.textContent='تشخيص KIX | '+kind+': '+String(detail||'خطأ غير معروف').slice(0,500);};window.addEventListener('error',e=>show('JavaScript',e.message+' ('+e.filename+':'+e.lineno+')'));window.addEventListener('unhandledrejection',e=>show('Promise',e.reason&&e.reason.message||e.reason));setTimeout(()=>{for(const id of ['categoryGrid','productGrid']){const el=document.getElementById(id);if(el&&/جاري التحميل|loading/i.test(el.textContent||'')){show('واجهة العرض','وصل اتصال قاعدة البيانات لكن بقي '+id+' في حالة التحميل. أرسل لقطة لهذه الرسالة.');break;}}},12000);})();
</script>"""
    if '</body>' in html:
        html=html.replace('</body>',diagnostic+'\\n</body>',1)
        index.write_text(html,encoding='utf-8')
# Remove only the obsolete hint text. Never remove its parent HTML element:
# broad parent-tag matching can accidentally delete the mascot or product categories.
mascot_decor_removed=0
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
        # Remove only the two exact decorative siblings beside the mascot button.
        # Keep the mascot button/image, hero-stage, orbit elements, and all store sections.
        for obsolete in (
            '<span class="mascot-wave" aria-hidden="true">👋</span>',
            '<div class="mascot-hint">اضغط على Kix وخليه يسويلك حركة! ✨</div>',
            '<div class="mascot-hint">اضغط على Kix وخليه يسويلك حركة!</div>',
        ):
            mascot_decor_removed += cleaned.count(obsolete)
            cleaned=cleaned.replace(obsolete,'')
        cleaned=cleaned.replace('👋 أضغط على KIX','').replace('👋 اضغط على KIX','')
        if cleaned!=content:
            candidate.write_text(cleaned,encoding='utf-8')
# Remove only the mascot's greeting and flip-hint overlays from the deployed archive.
# Keep the mascot button, 3D canvas, animation loop, and flip click behavior intact.
# Diagnose the actual mascot source inside the deployed ZIP before applying targeted edits.
for candidate in site.rglob('*'):
    if candidate.is_file() and candidate.suffix.lower() in ('.html','.js','.css'):
        try: diagnostic_text=candidate.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        tokens=('greeting','fliphint','kix-mascot','اضغط','أضغط','حتى يسويلك حركة','حتى يسوي لك حركة')
        if any(token in diagnostic_text.lower() for token in tokens):
            snippets=[]
            low=diagnostic_text.lower()
            for token in tokens:
                pos=0
                while True:
                    pos=low.find(token,pos)
                    if pos<0: break
                    snippets.append(f'{token} => {diagnostic_text[max(0,pos-500):min(len(diagnostic_text),pos+900)]}')
                    pos+=len(token)
            print(f'MASCOT_SOURCE {candidate}: ' + ' || '.join(snippets[:20]))
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
        updated=re.sub(r"greeting\.textContent\s*=\s*[^;]*;", "", updated)
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
print(f'Mascot decorative hand/hint elements removed: {mascot_decor_removed}.')
print(f'Mascot greeting/hint overlays removed in {mascot_targets} matching asset(s).')
final_html=(site/'index.html').read_text(encoding='utf-8')
hand_present='mascot-wave' in final_html
hint_present='mascot-hint' in final_html
mascot_button_present='id="mascotButton"' in final_html
categories_present='id="categories"' in final_html
print(f'Mascot hint verification: hand_present={hand_present}; hint_present={hint_present}; mascot_button_present={mascot_button_present}; categories_present={categories_present}.')

owner=site/'owner.html'; html=owner.read_text(encoding='utf-8')
if 'kix-admin-reviews.js' not in html:
    html=html.replace('<script src="admin.js" defer></script>','<script src="admin.js" defer></script><link rel="stylesheet" href="kix-public-features.css"><script src="kix-admin-reviews.js" defer></script>',1)
owner.write_text(html,encoding='utf-8')
print('Public statistics and review UI patched.')

# Install the mobile navigation close-on-selection behavior.
mobile_nav_source = root / "security" / "patch_mobile_nav.py"
if mobile_nav_source.exists():
    import subprocess
    subprocess.run([sys.executable, str(mobile_nav_source), str(site)], check=True)

# Product detail pages and recommendation cards.
for name in ('product-detail.html','kix-product-detail.js','kix-product-detail.css'):
    src=root/name
    if not src.exists(): raise SystemExit(f'Missing {src}')
    (site/name).write_bytes(src.read_bytes())
store=site/'store.js'; store_js=store.read_text(encoding='utf-8')
old_card='<article class="product-card">'
new_card='<article class="product-card" data-product-id="${esc(p.id)}" role="link" tabindex="0">'
if 'data-product-id="${esc(p.id)}"' not in store_js:
    if store_js.count(old_card) < 2:
        raise SystemExit('Product card template not found twice; refusing unsafe patch.')
    store_js=store_js.replace(old_card,new_card)
listener="""
const productGrid=$('#productGrid');
if(productGrid){
  const openProduct=el=>{
    const card=el.closest('[data-product-id]');
    if(!card||el.closest('[data-add]')) return;
    location.href='product-detail.html?id='+encodeURIComponent(card.dataset.productId);
  };
  productGrid.addEventListener('click',e=>openProduct(e.target));
  productGrid.addEventListener('keydown',e=>{
    if((e.key==='Enter'||e.key===' ')&&e.target.closest('[data-product-id]')&&!e.target.closest('[data-add]')){
      e.preventDefault();openProduct(e.target);
    }
  });
}
"""
if 'product-detail.html?id=' not in store_js:
    marker="function init(){ $('#year').textContent=new Date().getFullYear();"
    if marker not in store_js: raise SystemExit('Store init insertion point not found.')
    store_js=store_js.replace(marker,marker+listener,1)
store.write_text(store_js,encoding='utf-8')

print('Product detail pages installed.')


# Add the official KIX Store Instagram link to the storefront footer.
index=site/'index.html'
html=index.read_text(encoding='utf-8')
if 'id="kixInstagramLink"' not in html:
    instagram='''<section class="kix-instagram-footer" aria-label="حساب KIX STORE على إنستغرام"><a id="kixInstagramLink" href="https://www.instagram.com/kixstore_1/" target="_blank" rel="noopener noreferrer" aria-label="تابع KIX STORE على إنستغرام"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/></svg><span><strong>تابع KIX STORE</strong><small>على إنستغرام · @kixstore_1</small></span><b aria-hidden="true">↗</b></a></section><style>.kix-instagram-footer{display:flex;justify-content:center;padding:22px 16px 30px;background:#08080b}.kix-instagram-footer a{display:flex;align-items:center;gap:13px;width:min(100%,420px);padding:14px 17px;border:1px solid rgba(255,55,75,.48);border-radius:15px;background:linear-gradient(120deg,#171116,#101015);color:#fff;text-decoration:none;box-shadow:0 8px 28px #0005}.kix-instagram-footer svg{width:31px;height:31px;color:#ff5267;flex:none}.kix-instagram-footer span{display:grid;gap:3px;flex:1}.kix-instagram-footer strong{font-size:14px}.kix-instagram-footer small{font-size:12px;color:#aaa}.kix-instagram-footer b{color:#ff5267;font-size:20px}</style>'''
    if '</body>' not in html: raise SystemExit('Instagram patch failed: </body> not found in index.html')
    html=html.replace('</body>',instagram+'\\n</body>',1)
    index.write_text(html,encoding='utf-8')
print('Instagram footer link installed and verified:', 'id="kixInstagramLink"' in (site/'index.html').read_text(encoding='utf-8'))


# Update every storefront Telegram destination to the user's new official account.
import re
telegram_updated = 0
for candidate in site.rglob('*'):
    if not candidate.is_file() or candidate.suffix.lower() not in ('.html','.js','.css','.json'):
        continue
    try:
        source = candidate.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    revised = re.sub(r'https?://(?:www\\.)?(?:t\\.me|telegram\\.me)/[^\\s\\"\'<>]+',
                     'https://t.me/kixstore1', source, flags=re.I)
    revised = re.sub(r'(?i)(href\\s*=\\s*["\'])(?:https?://)?(?:www\\.)?(?:t\\.me|telegram\\.me)/[^"\']*',
                     r'\\1https://t.me/kixstore1', revised)
    if revised != source:
        candidate.write_text(revised, encoding='utf-8')
        telegram_updated += 1
print(f'Telegram destinations updated to https://t.me/kixstore1 in {telegram_updated} deployed asset(s).')


# Add the new official Telegram contact next to the Instagram footer link.
index = site/'index.html'
html = index.read_text(encoding='utf-8')
if 'id="kixTelegramLink"' not in html:
    telegram = '''<section class="kix-social-footer" aria-label="حساب KIX STORE على تيليغرام"><a id="kixTelegramLink" href="https://t.me/kixstore1" target="_blank" rel="noopener noreferrer"><span class="kix-telegram-icon" aria-hidden="true">➤</span><span><strong>تواصل ويانا على تيليغرام</strong><small>@kixstore1</small></span><b aria-hidden="true">↗</b></a></section><style>.kix-social-footer{display:flex;justify-content:center;padding:0 16px 24px;background:#08080b}.kix-social-footer a{display:flex;align-items:center;gap:13px;width:min(100%,420px);padding:14px 17px;border:1px solid rgba(45,165,220,.48);border-radius:15px;background:linear-gradient(120deg,#111820,#101015);color:#fff;text-decoration:none}.kix-social-footer .kix-telegram-icon{display:grid;place-items:center;width:31px;height:31px;border-radius:50%;background:#229ed9;color:white;font-size:17px;flex:none}.kix-social-footer a span:nth-child(2){display:grid;gap:3px;flex:1}.kix-social-footer strong{font-size:14px}.kix-social-footer small{font-size:12px;color:#aaa}.kix-social-footer b{color:#229ed9;font-size:20px}</style>'''
    if '</body>' not in html: raise SystemExit('Telegram footer insertion failed: </body> missing')
    html = html.replace('</body>', telegram+'\\n</body>', 1)
    index.write_text(html, encoding='utf-8')
print('Telegram footer link installed:', 'id="kixTelegramLink"' in (site/'index.html').read_text(encoding='utf-8'))
