(()=>{'use strict';
const cfg=window.KIX_CONFIG||{},$=s=>document.querySelector(s),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>localStorage.getItem('kix-display-currency')==='USD'?'new URLSearchParams(location.search).get('id');
let product=null,all=[];
function toast(m){const t=$('#kixDetailToast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
function image(src){return src||'assets/products/fc-27.webp'}
function readCart(){try{return JSON.parse(localStorage.getItem('kix-cart')||'[]')}catch(e){return []}}
function writeCart(cart){localStorage.setItem('kix-cart',JSON.stringify(cart));updateQtyUI()}
function changeQty(delta){let cart=readCart(),x=cart.find(x=>String(x.id)===String(product.id)),qty=x?Number(x.qty)||0:0,next=Math.max(0,Math.min(20,qty+delta));if(next===qty)return;if(next===0)cart=cart.filter(x=>String(x.id)!==String(product.id));else if(x)x.qty=next;else cart.push({id:product.id,qty:next});writeCart(cart);toast(next?'تم تحديث عدد النسخ':'تم حذف المنتج من السلة')}
function updateQtyUI(){if(!product)return;const x=readCart().find(x=>String(x.id)===String(product.id)),qty=x?Number(x.qty)||0:0;const q=$('#kixQtyValue'),total=$('#kixQtyTotal'),minus=$('#kixQtyMinus');if(q)q.textContent=qty;if(total)total.textContent=fmt(Number(product.price_iqd||0)*qty);if(minus)minus.disabled=qty===0}
function render(p,cats){product=p;document.title=p.name+' | Kix Store';const cat=cats.find(c=>String(c.id)===String(p.category_id));
const el=$('#kixDetailContent');el.innerHTML='<article class="kix-detail-card"><div class="kix-detail-image"><img src="'+esc(image(p.image_url))+'" alt="'+esc(p.name)+'">'+(p.badge?'<span class="product-badge">'+esc(p.badge)+'</span>':'')+'</div><div class="kix-detail-info"><span class="eyebrow">KIX DIGITAL STORE'+(cat?' · '+esc(cat.name):'')+'</span><h1>'+esc(p.name)+'</h1><div class="kix-detail-price">'+fmt(p.price_iqd)+'</div><div class="kix-detail-description">'+esc(p.description||'منتج رقمي من Kix Store. راجع التفاصيل قبل إتمام الطلب.')+'</div><div class="kix-detail-facts"><div><b>التسليم</b><span>رقمي بعد تأكيد الطلب والدفع</span></div><div><b>الدعم</b><span>متاح عبر واتساب وتلغرام</span></div><div><b>ملاحظة</b><span>يمكنك كتابة المنصة أو المنطقة أو أي تفاصيل مطلوبة في ملاحظات الطلب</span></div></div><div class="kix-quantity-box"><span class="kix-quantity-label">عدد النسخ</span><div class="kix-quantity-control"><button type="button" id="kixQtyMinus" aria-label="تقليل عدد النسخ">−</button><strong id="kixQtyValue">0</strong><button type="button" id="kixQtyPlus" aria-label="زيادة عدد النسخ">+</button></div><div class="kix-quantity-total">الإجمالي: <strong id="kixQtyTotal">0 د.ع</strong></div><small>اختر العدد المطلوب، وستُحدّث السلة تلقائياً.</small></div><a class="kix-detail-contact" href="index.html#contact">تحتاج مساعدة قبل الشراء؟ تواصل معنا</a></div></article>';
$('#kixQtyMinus').onclick=()=>changeQty(-1);$('#kixQtyPlus').onclick=()=>changeQty(1);updateQtyUI();
const related=all.filter(x=>String(x.id)!==String(p.id)&&String(x.category_id)===String(p.category_id)).slice(0,4);
const extra=all.filter(x=>String(x.id)!==String(p.id)&&String(x.category_id)!==String(p.category_id)).slice(0,Math.max(0,4-related.length));
const list=related.concat(extra).slice(0,4);
if(list.length){$('#kixRelatedSection').hidden=false;$('#kixRelatedGrid').innerHTML=list.map(x=>'<article class="product-card"><a class="kix-related-link" href="product-detail.html?id='+encodeURIComponent(x.id)+'"><div class="product-image"><img loading="lazy" src="'+esc(image(x.image_url))+'" alt="'+esc(x.name)+'"></div><div class="product-info"><h3>'+esc(x.name)+'</h3><p>'+esc(x.description||'منتج رقمي من Kix Store')+'</p><div class="product-bottom"><span class="price">'+fmt(x.price_iqd)+'</span><span class="kix-related-open">التفاصيل ←</span></div></div></a></article>').join('')}
}
async function start(){
$('#kixDetailYear').textContent=new Date().getFullYear();
if(!id){$('#kixDetailContent').textContent='رابط المنتج غير مكتمل.';return}
if(!window.supabase||!cfg.supabaseUrl||!cfg.supabaseAnonKey){$('#kixDetailContent').textContent='تعذر الاتصال بالمتجر حالياً.';return}
const sb=window.supabase.createClient(cfg.supabaseUrl,cfg.supabaseAnonKey);
const results=await Promise.all([sb.from('products').select('*').eq('id',id).eq('active',true).maybeSingle(),sb.from('products').select('*').eq('active',true).order('sort_order').limit(100),sb.from('categories').select('id,name')]);
const pr=results[0],allr=results[1],cr=results[2];
if(pr.error||!pr.data){$('#kixDetailContent').textContent='هذا المنتج غير متاح حالياً أو تم إيقافه.';return}
all=allr.data||[];render(pr.data,cr.data||[])
}
window.addEventListener('kix-currency-changed',()=>{if(product){$('#kixDetailContent .kix-detail-price').textContent=fmt(product.price_iqd);updateQtyUI();}});
document.addEventListener('DOMContentLoaded',start)
})();+(Number(n||0)/1520).toFixed(2):new Intl.NumberFormat('ar-IQ').format(Number(n||0))+' د.ع',id=new URLSearchParams(location.search).get('id');
let product=null,all=[];
function toast(m){const t=$('#kixDetailToast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
function image(src){return src||'assets/products/fc-27.webp'}
function addCart(){let cart=[];try{cart=JSON.parse(localStorage.getItem('kix-cart')||'[]')}catch(e){}let x=cart.find(x=>String(x.id)===String(product.id));if(x)x.qty++;else cart.push({id:product.id,qty:1});localStorage.setItem('kix-cart',JSON.stringify(cart));toast('انضاف المنتج إلى السلة بنجاح')}
function render(p,cats){product=p;document.title=p.name+' | Kix Store';const cat=cats.find(c=>String(c.id)===String(p.category_id));
const el=$('#kixDetailContent');el.innerHTML='<article class="kix-detail-card"><div class="kix-detail-image"><img src="'+esc(image(p.image_url))+'" alt="'+esc(p.name)+'">'+(p.badge?'<span class="product-badge">'+esc(p.badge)+'</span>':'')+'</div><div class="kix-detail-info"><span class="eyebrow">KIX DIGITAL STORE'+(cat?' · '+esc(cat.name):'')+'</span><h1>'+esc(p.name)+'</h1><div class="kix-detail-price">'+fmt(p.price_iqd)+'</div><div class="kix-detail-description">'+esc(p.description||'منتج رقمي من Kix Store. راجع التفاصيل قبل إتمام الطلب.')+'</div><div class="kix-detail-facts"><div><b>التسليم</b><span>رقمي بعد تأكيد الطلب والدفع</span></div><div><b>الدعم</b><span>متاح عبر واتساب وتلغرام</span></div><div><b>ملاحظة</b><span>يمكنك كتابة المنصة أو المنطقة أو أي تفاصيل مطلوبة في ملاحظات الطلب</span></div></div><button id="kixDetailAdd" class="btn primary kix-detail-add">أضف إلى السلة +</button><a class="kix-detail-contact" href="index.html#contact">تحتاج مساعدة قبل الشراء؟ تواصل معنا</a></div></article>';
$('#kixDetailAdd').onclick=addCart;
const related=all.filter(x=>String(x.id)!==String(p.id)&&String(x.category_id)===String(p.category_id)).slice(0,4);
const extra=all.filter(x=>String(x.id)!==String(p.id)&&String(x.category_id)!==String(p.category_id)).slice(0,Math.max(0,4-related.length));
const list=related.concat(extra).slice(0,4);
if(list.length){$('#kixRelatedSection').hidden=false;$('#kixRelatedGrid').innerHTML=list.map(x=>'<article class="product-card"><a class="kix-related-link" href="product-detail.html?id='+encodeURIComponent(x.id)+'"><div class="product-image"><img loading="lazy" src="'+esc(image(x.image_url))+'" alt="'+esc(x.name)+'"></div><div class="product-info"><h3>'+esc(x.name)+'</h3><p>'+esc(x.description||'منتج رقمي من Kix Store')+'</p><div class="product-bottom"><span class="price">'+fmt(x.price_iqd)+'</span><span class="kix-related-open">التفاصيل ←</span></div></div></a></article>').join('')}
}
async function start(){
$('#kixDetailYear').textContent=new Date().getFullYear();
if(!id){$('#kixDetailContent').textContent='رابط المنتج غير مكتمل.';return}
if(!window.supabase||!cfg.supabaseUrl||!cfg.supabaseAnonKey){$('#kixDetailContent').textContent='تعذر الاتصال بالمتجر حالياً.';return}
const sb=window.supabase.createClient(cfg.supabaseUrl,cfg.supabaseAnonKey);
const results=await Promise.all([sb.from('products').select('*').eq('id',id).eq('active',true).maybeSingle(),sb.from('products').select('*').eq('active',true).order('sort_order').limit(100),sb.from('categories').select('id,name')]);
const pr=results[0],allr=results[1],cr=results[2];
if(pr.error||!pr.data){$('#kixDetailContent').textContent='هذا المنتج غير متاح حالياً أو تم إيقافه.';return}
all=allr.data||[];render(pr.data,cr.data||[])
}
document.addEventListener('DOMContentLoaded',start)
})();