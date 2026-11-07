(function(){
const endpoint='https://xtewgkfwivdonaaozbkc.supabase.co/functions/v1/manage-coupons';
const $=s=>document.querySelector(s);let editing=null;
function token(){
 for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!k||!k.startsWith('sb-')||!k.endsWith('-auth-token'))continue;try{const v=JSON.parse(localStorage.getItem(k));if(v.access_token)return v.access_token;}catch(_){}}
 return null;
}
async function api(method='GET',body){
 const t=token();if(!t)throw new Error('جلسة المالك غير موجودة. سجّل الدخول مجدداً.');
 const r=await fetch(endpoint,{method,headers:{Authorization:'Bearer '+t,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
 const d=await r.json();if(!r.ok)throw new Error(d.error||'تعذر تنفيذ العملية.');return d;
}
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function mount(){
 if($('#kixAdminCoupons'))return;
 const host=document.querySelector('main')||document.querySelector('.admin-container')||document.body;
 const box=document.createElement('section');box.id='kixAdminCoupons';box.className='kix-admin-coupons';
 box.innerHTML='<h2>🎟️ إدارة أكواد الخصم</h2><form id="kixCouponForm"><div class="kix-coupon-admin-grid"><label>كود الخصم<input name="code" required maxlength="32" placeholder="KIX10"></label><label>نوع الخصم<select name="discount_type"><option value="percent">نسبة مئوية %</option><option value="fixed">مبلغ ثابت بالدينار</option></select></label><label>قيمة الخصم<input name="discount_value" type="number" min="1" required></label><label>الحد الأدنى للطلب (د.ع)<input name="min_order_iqd" type="number" min="0" value="0"></label><label>أقصى خصم (د.ع)<input name="max_discount_iqd" type="number" min="1" placeholder="اختياري"></label><label>عدد الاستخدامات<input name="usage_limit" type="number" min="1" placeholder="غير محدود"></label><label>يبدأ في<input name="starts_at" type="datetime-local"></label><label>ينتهي في<input name="expires_at" type="datetime-local"></label><label><span>الحالة</span><select name="active"><option value="true">مفعّل</option><option value="false">متوقف</option></select></label></div><div class="kix-admin-coupon-actions"><button type="submit">حفظ الكوبون</button><button type="button" id="kixCouponReset" class="danger">إلغاء التعديل</button><span id="kixAdminCouponMsg"></span></div></form><div id="kixAdminCouponList" class="kix-coupon-list">جارٍ تحميل الأكواد...</div>';
 host.appendChild(box);
 box.querySelector('#kixCouponForm').addEventListener('submit',async e=>{
  e.preventDefault();const form=e.currentTarget;const f=new FormData(form),o=Object.fromEntries(f.entries());
  o.discount_value=Number(o.discount_value);o.min_order_iqd=Number(o.min_order_iqd||0);o.active=o.active==='true';
  o.max_discount_iqd=o.max_discount_iqd?Number(o.max_discount_iqd):null;o.usage_limit=o.usage_limit?Number(o.usage_limit):null;
  o.starts_at=o.starts_at?new Date(o.starts_at).toISOString():null;o.expires_at=o.expires_at?new Date(o.expires_at).toISOString():null;
  try{await api('POST',o);$('#kixAdminCouponMsg').textContent='تم حفظ الكوبون.';form.reset();editing=null;await load();}
  catch(err){$('#kixAdminCouponMsg').textContent=err.message;}
 });
 box.querySelector('#kixCouponReset').addEventListener('click',()=>{box.querySelector('form').reset();editing=null;$('#kixAdminCouponMsg').textContent='';});
}
async function load(){
 const list=$('#kixAdminCouponList');if(!list)return;
 try{const d=await api();list.innerHTML=(d.coupons||[]).map(c=>'<div class="kix-coupon-item"><div><strong>'+esc(c.code)+'</strong><small>'+(c.discount_type==='percent'?esc(c.discount_value)+'%':esc(c.discount_value)+' د.ع')+' · مستخدم '+esc(c.usage_count)+' / '+(c.usage_limit??'∞')+' · '+(c.active?'مفعّل':'متوقف')+'</small></div><div class="kix-admin-coupon-actions"><button type="button" data-edit="'+esc(c.id)+'">تعديل</button><button type="button" class="danger" data-delete="'+esc(c.id)+'">حذف</button></div></div>').join('')||'<p>لا توجد أكواد خصم بعد.</p>';
 list.querySelectorAll('[data-edit]').forEach(b=>b.addEventListener('click',()=>{const c=d.coupons.find(x=>x.id===b.dataset.edit);if(!c)return;const f=$('#kixCouponForm');for(const [k,v] of Object.entries(c)){if(f.elements[k])f.elements[k].value=(k==='starts_at'||k==='expires_at')?(v?new Date(v).toISOString().slice(0,16):''):String(v??'');}editing=c.id;$('#kixAdminCouponMsg').textContent='عدّل البيانات ثم احفظ. يتم تحديث الكود نفسه.';}));
 list.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',async()=>{if(!confirm('تأكيد حذف كود الخصم؟'))return;try{await api('DELETE',{id:b.dataset.delete});await load();}catch(e){alert(e.message);}}));
 }catch(e){list.textContent=e.message;}
}
function start(){mount();load();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();