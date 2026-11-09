(function(){
const URL='https://xtewgkfwivdonaaozbkc.supabase.co/functions/v1/';
let applied=null;
const money=n=>new Intl.NumberFormat('ar-IQ').format(Number(n||0))+' د.ع';
function subtotal(){
 const root=document.querySelector('#checkoutModal,#checkoutSection,.checkout-modal,.checkout-section,[id*="checkout"],[class*="checkout"]')||document;
 const candidates=[...root.querySelectorAll('[id*="total"],[class*="total"],[id*="Total"],[class*="Total"]')];
 let values=candidates.map(el=>Number((el.textContent||'').replace(/[^0-9]/g,''))).filter(n=>Number.isSafeInteger(n)&&n>0);
 if(!values.length){const text=root.innerText||'';values=(text.match(/[0-9][0-9,٬. ]{2,}/g)||[]).map(s=>Number(s.replace(/[^0-9]/g,''))).filter(n=>Number.isSafeInteger(n)&&n>0);}
 return values.length?Math.max(...values):0;
}
function init(){
 const anchor=document.getElementById('paymentInstructions');
 if(!anchor||document.getElementById('kixCouponBox'))return;
 const box=document.createElement('section');box.id='kixCouponBox';box.className='kix-coupon-box';
 box.innerHTML='<div class="kix-coupon-title">🎟️ عندك كود خصم؟</div><div class="kix-coupon-row"><input id="kixCouponInput" maxlength="32" placeholder="اكتب كود الخصم" autocomplete="off"><button id="kixCouponApply" type="button">تطبيق الكود</button></div><div id="kixCouponMessage" class="kix-coupon-msg">أدخل الكود واضغط تطبيق قبل تأكيد الطلب.</div><div id="kixCouponSavings" class="kix-coupon-savings"></div>';
 anchor.parentNode.insertBefore(box,anchor);
 box.querySelector('#kixCouponApply').addEventListener('click',async()=>{
  const code=box.querySelector('#kixCouponInput').value.trim().toUpperCase();
  const msg=box.querySelector('#kixCouponMessage'),save=box.querySelector('#kixCouponSavings'),btn=box.querySelector('#kixCouponApply');
  const amount=subtotal();
  if(!code){msg.textContent='اكتب كود الخصم أولاً.';return;}
  if(!amount){msg.textContent='أضف المنتجات إلى السلة وافتح صفحة إكمال الطلب أولاً.';return;}
  btn.disabled=true;msg.textContent='جارٍ التحقق من الكود...';save.style.display='none';
  try{
   const res=await fetch(URL+'validate-coupon',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code,subtotal_iqd:amount})});
   const data=await res.json();if(!res.ok||!data.valid)throw new Error(data.error||'الكود غير صالح.');
   applied=data.code;msg.textContent='تم تطبيق كود الخصم بنجاح.';msg.classList.add('success');
   save.textContent='وفّرت '+money(data.discount_iqd)+'، المجموع بعد الخصم '+money(data.total_iqd);save.style.display='block';
  }catch(e){applied=null;msg.textContent=e.message||'تعذر التحقق من الكود.';msg.classList.remove('success');}
  finally{btn.disabled=false;}
 });
}
const originalFetch=window.fetch.bind(window);
window.fetch=function(input,init){
 const url=typeof input==='string'?input:(input&&input.url)||'';
 if(applied&&url.includes('/functions/v1/create-order')&&init&&init.body){
  try{const body=JSON.parse(init.body);body.coupon_code=applied;init={...init,body:JSON.stringify(body)};}catch(_){}
 }
 return originalFetch(input,init);
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
// The checkout paymentInstructions container exists in the initial page markup.
// No global DOM observer is needed to mount the coupon box.
})();