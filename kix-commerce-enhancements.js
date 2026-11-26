(()=>{
'use strict';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const digits=s=>String(s||'').replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[۰-۹]/g,d=>'۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
const priceOf=card=>{const t=digits($('.price',card)?.textContent||'').replace(/[^\d]/g,'');return Number(t)||0};
let gridObserver=null,sortMode='default',busy=false,scheduled=false;
function ensureSort(){
 const filters=$('.filters');if(!filters||$('#kixProductSort'))return;
 const s=document.createElement('select');s.id='kixProductSort';s.setAttribute('aria-label','ترتيب المنتجات');
 s.innerHTML='<option value="default">الترتيب الافتراضي</option><option value="price-asc">السعر: الأقل أولاً</option><option value="price-desc">السعر: الأعلى أولاً</option><option value="name-asc">الاسم: أ إلى ي</option>';
 filters.append(s);s.addEventListener('change',()=>{sortMode=s.value;sortCards()});
}
function ensureDetailsDialog(){
 if($('#kixProductDetails'))return;
 const d=document.createElement('dialog');d.id='kixProductDetails';d.className='modal kix-product-dialog';
 d.innerHTML='<div class="modal-head"><h2 id="kixProductDetailsTitle">تفاصيل المنتج</h2><button type="button" class="close-modal" id="kixProductDetailsClose" aria-label="إغلاق">✕</button></div><p id="kixProductDetailsBody"></p><p class="fine-print">راجع شروط المنتج والضمان الظاهرة قبل إتمام الطلب. إذا عندك استفسار تواصل ويانا قبل الشراء.</p>';
 document.body.append(d);$('#kixProductDetailsClose').addEventListener('click',()=>d.close());
 d.addEventListener('click',e=>{if(e.target===d)d.close()});
}
function decorateCards(){
 const grid=$('#productGrid');if(!grid)return;
 $$('.product-card',grid).forEach(card=>{
  const img=$('img',card);if(img){img.loading='lazy';img.decoding='async';img.addEventListener('error',()=>{if(!img.dataset.kixFallback){img.dataset.kixFallback='1';img.src='assets/kix-logo.png';img.classList.add('kix-image-fallback')}},{once:true})}
  const p=$('.product-info p',card);
  if(p&&!p.dataset.kixFull){p.dataset.kixFull=(p.textContent||'').trim();p.classList.add('kix-card-summary')}
  if(p&&!$('.kix-details-button',card)){
   const b=document.createElement('button');b.type='button';b.className='kix-details-button';b.textContent='تفاصيل المنتج';
   b.addEventListener('click',()=>{ensureDetailsDialog();$('#kixProductDetailsTitle').textContent=$('h3',card)?.textContent||'تفاصيل المنتج';$('#kixProductDetailsBody').textContent=p.dataset.kixFull||p.textContent;$('#kixProductDetails').showModal()});
   const bottom=$('.product-bottom',card);if(bottom)card.querySelector('.product-info').insertBefore(b,bottom);
  }
  const price=$('.price',card);if(price){price.setAttribute('aria-label','السعر '+price.textContent.trim());price.classList.add('kix-price-clear')}
 });
}
function sortCards(){
 const grid=$('#productGrid');if(!grid||busy)return;
 const cards=$$('.product-card',grid);if(cards.length<2)return;
 const collator=new Intl.Collator('ar',{numeric:true,sensitivity:'base'});
 cards.sort((a,b)=>{
  if(sortMode==='price-asc')return priceOf(a)-priceOf(b);
  if(sortMode==='price-desc')return priceOf(b)-priceOf(a);
  if(sortMode==='name-asc')return collator.compare($('h3',a)?.textContent||'',$('h3',b)?.textContent||'');
  return 0;
 });
 busy=true;cards.forEach(c=>grid.append(c));requestAnimationFrame(()=>{busy=false});
}
function schedule(){
 if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;ensureSort();decorateCards();sortCards()});
}
function addTrustStrip(){
 const contact=$('#contact');if(!contact||$('#kixTrustAndPolicies'))return;
 const s=document.createElement('section');s.id='kixTrustAndPolicies';s.className='wrap kix-trust-panel';
 s.innerHTML='<div><span class="eyebrow">SHOP WITH CLARITY</span><h2>كل التفاصيل المهمة، <em>قبل الشراء</em></h2><p>اقرأ شروط المنتج والدفع والضمان حتى تعرف شنو تشتري، شلون تستلمه، وشنو حقوقك إذا صار خلل.</p></div><nav aria-label="معلومات المتجر"><a href="guarantee.html">الضمان والاسترداد</a><a href="payment.html">طرق الدفع والاستلام</a><a href="faq.html">الأسئلة الشائعة</a><a href="about.html">من نحن</a><a href="contact.html">تواصل معنا</a></nav>';
 contact.before(s);
}
function init(){
 ensureSort();ensureDetailsDialog();addTrustStrip();decorateCards();
 const grid=$('#productGrid');
 if(grid&&!gridObserver){gridObserver=new MutationObserver(schedule);gridObserver.observe(grid,{childList:true,subtree:false})}
 const search=$('#productSearch');if(search)search.setAttribute('aria-label','ابحث عن اسم المنتج أو وصفه');
 const filter=$('#categoryFilter');if(filter)filter.setAttribute('aria-label','تصفية حسب القسم');
}
document.addEventListener('DOMContentLoaded',init);
if(document.readyState!=='loading')init();
})();
