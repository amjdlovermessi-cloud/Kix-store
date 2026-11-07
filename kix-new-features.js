(()=>{const cfg=window.KIX_CONFIG||{},$=s=>document.querySelector(s);let client=null;
const money=n=>new Intl.NumberFormat('ar-IQ').format(Number(n||0))+' د.ع';
const cartRead=()=>{try{return JSON.parse(localStorage.getItem('kix-cart')||'[]')}catch(_){return []}};
const cartWrite=c=>localStorage.setItem('kix-cart',JSON.stringify(c));
const b64url=s=>btoa(unescape(encodeURIComponent(s))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const unb64=s=>decodeURIComponent(escape(atob(s.replace(/-/g,'+').replace(/_/g,'/'))));
async function getProducts(cart){if(!client)client=window.supabase.createClient(cfg.supabaseUrl,cfg.supabaseAnonKey);const ids=cart.map(x=>x.id).filter(Boolean);if(!ids.length)return[];const {data,error}=await client.from('products').select('id,name,price_iqd,image_url').in('id',ids);if(error)throw error;return data||[]}
function importShared(){const p=new URLSearchParams(location.search),raw=p.get('sharecart');if(!raw)return;try{const incoming=JSON.parse(unb64(raw));if(!Array.isArray(incoming)||!incoming.length)throw 0;const current=cartRead();for(const x of incoming){if(!x.id||!Number.isInteger(Number(x.qty))||Number(x.qty)<1)continue;const found=current.find(y=>String(y.id)===String(x.id));if(found)found.qty=Number(found.qty||1)+Number(x.qty);else current.push({id:x.id,qty:Number(x.qty)});}cartWrite(current);p.delete('sharecart');history.replaceState({},'',location.pathname+(p.size?'?'+p.toString():'')+location.hash);setTimeout(()=>location.reload(),250);}catch(_){console.warn('رابط السلة غير صالح');}}
function addShareButton(){
 if(location.pathname.endsWith('/owner.html'))return;
 const install=()=>{
  const visible=el=>!!(el&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).display!=='none');
  const candidates=[...document.querySelectorAll('[role="dialog"],dialog,.cart-modal,.cart-drawer,.cart-sidebar,#cartModal,#cartDrawer,[class*="cart" i]')].filter(visible);
  let host=candidates.find(el=>/إتمام الطلب|تأكيد الطلب|checkout/i.test(el.innerText||'')&&/السلة|المجموع|الإجمالي/.test(el.innerText||''));
  if(!host){const checkout=[...document.querySelectorAll('button,a,[role="button"],input[type="submit"]')].find(el=>visible(el)&&/إتمام الطلب|تأكيد الطلب|checkout/i.test(el.innerText||el.value||''));if(checkout){let p=checkout.parentElement;for(let i=0;p&&i<7;i++,p=p.parentElement){if(/السلة|المجموع|الإجمالي/.test(p.innerText||'')){host=p;break}}}}
  if(!host||host.querySelector('#kixShareCartInline'))return;
  const actions=document.createElement('div');actions.id='kixShareCartInline';actions.className='kix-share-inline';actions.innerHTML='<strong>مشاركة السلة</strong><button type="button" id="kixShareImageInline">حفظ صورة المنتجات</button><button type="button" id="kixShareLinkInline">مشاركة رابط السلة</button>';
  const checkout=[...host.querySelectorAll('button,a,[role="button"],input[type="submit"]')].find(el=>/إتمام الطلب|تأكيد الطلب|checkout/i.test(el.innerText||el.value||''));
  if(checkout&&checkout.parentElement)checkout.parentElement.insertBefore(actions,checkout);else host.appendChild(actions);
  actions.querySelector('#kixShareImageInline').onclick=()=>openShare('image');
  actions.querySelector('#kixShareLinkInline').onclick=()=>openShare('link');
 };
 install();new MutationObserver(install).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','aria-hidden']});
}
async function openShare(mode){const cart=cartRead();if(!cart.length){alert('السلة فارغة حالياً. أضف المنتجات أولاً.');return}let products=[];try{products=await getProducts(cart)}catch(e){alert('تعذر تحميل تفاصيل السلة.');return}const byId=new Map(products.map(p=>[String(p.id),p]));const rows=cart.map(x=>({id:x.id,qty:Number(x.qty||1),p:byId.get(String(x.id))})).filter(x=>x.p);if(!rows.length){alert('لم نعثر على المنتجات الموجودة في السلة.');return}
const url=new URL(location.href);url.search='';url.hash='';url.searchParams.set('sharecart',b64url(JSON.stringify(rows.map(x=>({id:x.id,qty:x.qty})))));
const modal=document.createElement('div');modal.className='kix-share-modal';modal.innerHTML='<div class="kix-share-card"><button class="kix-share-close" type="button">×</button><h3>شارك سلتك 🛒</h3><p>اختر طريقة المشاركة</p><div class="kix-share-actions"><button type="button" id="kixSaveCartImage">حفظ صورة المنتجات</button><button type="button" id="kixCopyCartLink">نسخ رابط السلة</button></div><div class="kix-share-preview"></div></div>';document.body.appendChild(modal);modal.querySelector('.kix-share-close').onclick=()=>modal.remove();modal.addEventListener('click',e=>{if(e.target===modal)modal.remove()});modal.querySelector('.kix-share-preview').innerHTML=rows.map(x=>'<div>'+String(x.p.name).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))+' × '+x.qty+' <b>'+money(Number(x.p.price_iqd)*x.qty)+'</b></div>').join('');
modal.querySelector('#kixCopyCartLink').onclick=async()=>{try{await navigator.clipboard.writeText(url.toString());modal.querySelector('#kixCopyCartLink').textContent='تم نسخ الرابط ✓'}catch(_){prompt('انسخ رابط السلة:',url.toString())}};
modal.querySelector('#kixSaveCartImage').onclick=()=>{const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');canvas.width=900;canvas.height=180+rows.length*105;ctx.fillStyle='#101015';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.fillStyle='#f5c15d';ctx.font='bold 42px Arial';ctx.fillText('KIX STORE',55,70);ctx.fillStyle='#fff';ctx.font='bold 28px Arial';ctx.fillText('قائمة المنتجات',55,120);let y=185,total=0;for(const x of rows){const price=Number(x.p.price_iqd)*x.qty;total+=price;ctx.fillStyle='#24212a';ctx.fillRect(45,y-38,810,82);ctx.fillStyle='#fff';ctx.font='bold 25px Arial';ctx.fillText(String(x.p.name).slice(0,38),70,y);ctx.font='22px Arial';ctx.fillStyle='#ccc';ctx.fillText('الكمية: '+x.qty,70,y+30);ctx.fillStyle='#f5c15d';ctx.textAlign='right';ctx.fillText(money(price),820,y+8);ctx.textAlign='left';y+=105;}ctx.fillStyle='#fff';ctx.font='bold 29px Arial';ctx.fillText('المجموع: '+money(total),55,y+15);ctx.fillStyle='#aaa';ctx.font='18px Arial';ctx.fillText('اطلبها من KIX STORE',55,y+55);const a=document.createElement('a');a.download='KIX-cart.png';a.href=canvas.toDataURL('image/png');a.click();};
}
function paymentUI(){
 if(location.pathname.endsWith('/owner.html'))return;
 const checkoutButton=[...document.querySelectorAll('button,input[type="submit"],[role="button"]')].find(el=>/إتمام الطلب|تأكيد الطلب|إرسال الطلب|checkout/i.test(el.innerText||el.value||''));
 const form=checkoutButton?.closest('form')||[...document.querySelectorAll('form')].find(f=>f.querySelector('[name="customer_name"],[name="phone"]'))||document.querySelector('form');
 if(!form)return;
 if(form.dataset.kixReceiptInit==='1')return;
 const select=form.querySelector('select[name="payment_method"]'),radios=[...form.querySelectorAll('input[name="payment_method"]')];
 let option=radios.find(r=>r.value==='asiacell_card');
 if(select){if(![...select.options].some(o=>o.value==='asiacell_card')){const op=document.createElement('option');op.value='asiacell_card';op.textContent='تحويل بطاقة ماستر كارد آسياسيل';select.appendChild(op)}}
 else{
  if(!option){
   const group=radios[0]?.closest('fieldset,[role="radiogroup"],.payment-methods,.payment-options')||radios[0]?.parentElement||form;
   const label=document.createElement('label');label.className='kix-card-payment-option';
   label.innerHTML='<input type="radio" name="payment_method" value="asiacell_card"><span>تحويل بطاقة ماستر كارد آسياسيل</span>';
   const submit=checkoutButton&&form.contains(checkoutButton)?checkoutButton:null;
   if(submit)form.insertBefore(label,submit);else group.appendChild(label);
   option=label.querySelector('input');
  }
 }
 let panel=form.querySelector('#kixReceiptPanel')||$('#kixReceiptPanel');
 if(!panel){panel=document.createElement('section');panel.id='kixReceiptPanel';panel.innerHTML='<div class="kix-card-number"><strong>رقم بطاقة آسياسيل ماستر كارد</strong><b dir="ltr">2427128562</b><button type="button" id="kixCopyCard">نسخ الرقم</button></div><p>حوّل المبلغ الإجمالي للطلب إلى الرقم أعلاه، ثم أرفق صورة قسيمة التحويل.</p><label class="kix-receipt-label">إرفاق قسيمة التحويل <input id="kixReceiptFile" type="file" accept="image/jpeg,image/png,image/webp"><small>صورة JPG أو PNG أو WEBP، بحد أقصى 5 ميغابايت</small></label><img id="kixReceiptPreview" alt="معاينة قسيمة التحويل" hidden>';const submit=checkoutButton&&form.contains(checkoutButton)?checkoutButton:null;if(submit)form.insertBefore(panel,submit);else form.appendChild(panel)}
 const method=()=>select?select.value:form.querySelector('input[name="payment_method"]:checked')?.value;
 const toggle=()=>{panel.hidden=method()!=='asiacell_card'};
 form.addEventListener('change',e=>{if(e.target.name==='payment_method')toggle()});form.dataset.kixReceiptInit='1';toggle();
 const copy=panel.querySelector('#kixCopyCard');if(copy&&!copy.dataset.bound){copy.dataset.bound='1';copy.onclick=async()=>{try{await navigator.clipboard.writeText('2427128562');copy.textContent='تم النسخ ✓'}catch(_){prompt('رقم البطاقة','2427128562')}}}
 const input=panel.querySelector('#kixReceiptFile');if(input&&!input.dataset.bound){input.dataset.bound='1';input.addEventListener('change',e=>{const file=e.target.files?.[0],img=panel.querySelector('#kixReceiptPreview');if(!file){img.hidden=true;return}if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>5*1024*1024){alert('اختر صورة JPG أو PNG أو WEBP لا يتجاوز حجمها 5 ميغابايت.');e.target.value='';img.hidden=true;return}img.src=URL.createObjectURL(file);img.hidden=false})}
}
async function fileBase64(file){return await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result).split(',')[1]);r.onerror=reject;r.readAsDataURL(file)})}
function interceptOrder(){const original=window.fetch.bind(window);window.fetch=async(input,init={})=>{const url=typeof input==='string'?input:input?.url||'';if(url.includes('/functions/v1/create-order')&&init.body){try{const body=JSON.parse(init.body);if(body.payment_method==='asiacell_card'){const file=$('#kixReceiptFile')?.files?.[0];if(!file)throw new Error('أرفق صورة قسيمة التحويل قبل تأكيد الطلب.');if(file.size>5*1024*1024)throw new Error('حجم صورة القسيمة أكبر من 5 ميغابايت.');body.receipt_mime=file.type;body.receipt_data=await fileBase64(file);init={...init,body:JSON.stringify(body)}}}catch(e){if(e instanceof Error&&e.message.includes('قسيمة')){alert(e.message);return new Response(JSON.stringify({error:e.message}),{status:400,headers:{'Content-Type':'application/json'}})}}const response=await original(input,init);try{const clone=response.clone(),data=await clone.json();if(data.order?.order_number)showOrderCopy(data.order.order_number)}catch(_){}return response};return original(input,init)}}
function showOrderCopy(code){const scan=()=>{const nodes=[...document.querySelectorAll('body *')].filter(el=>el.children.length===0&&el.textContent.includes(code));if(!nodes.length)return false;const target=nodes[0].parentElement;if(target.querySelector('[data-kix-copy-order]'))return true;const b=document.createElement('button');b.dataset.kixCopyOrder='1';b.className='kix-copy-order';b.textContent='نسخ كود الطلب';b.onclick=async()=>{try{await navigator.clipboard.writeText(code);b.textContent='تم نسخ الكود ✓'}catch(_){prompt('كود الطلب',code)}};target.appendChild(b);return true};if(scan())return;const observer=new MutationObserver(()=>{if(scan())observer.disconnect()});observer.observe(document.body,{childList:true,subtree:true});setTimeout(()=>observer.disconnect(),12000)}
function adminSearch(){const host=$('#adminOrders');if(!host||$('#kixOrderSearch'))return;const input=document.createElement('input');input.id='kixOrderSearch';input.placeholder='ابحث بكود الطلب KIX-...';input.type='search';input.className='kix-order-search';host.parentElement.insertBefore(input,host);input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();host.querySelectorAll('.admin-row').forEach(row=>row.hidden=q&&!row.textContent.toLowerCase().includes(q))})}
function init(){importShared();addShareButton();paymentUI();adminSearch();if(window.supabase&&cfg.supabaseUrl&&cfg.supabaseAnonKey&&!client)client=window.supabase.createClient(cfg.supabaseUrl,cfg.supabaseAnonKey)}
document.addEventListener('DOMContentLoaded',()=>{init();interceptOrder();new MutationObserver(()=>{paymentUI();adminSearch()}).observe(document.body,{childList:true,subtree:true})});
})();
// KIX Store feature bundle v2
