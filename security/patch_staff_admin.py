from pathlib import Path
import re

root=Path("site")
staff_source=Path("kix-admin-staff.js")
(root/"kix-admin-staff.js").write_text(staff_source.read_text(encoding="utf-8"),encoding="utf-8")
admin=root/"admin.js"
src=admin.read_text(encoding="utf-8")
src=src.replace("let cats=[],products=[];","let cats=[],products=[],permissions={manage_products:false,edit_prices:false,manage_orders:false},isOwner=false;")
m=re.search(r"async function enter\(\)\{.*?\}\nasync function loadProducts",src)
if not m: raise SystemExit("admin enter() not found")
enter="""async function enter(){let {data:{user}}=await sb.auth.getUser();let {data:profile,error}=await sb.from('profiles').select('role,display_name').eq('id',user.id).single();if(error){await sb.auth.signOut();showError('تعذر التحقق من صلاحيات الحساب.');return;}isOwner=profile?.role==='owner';if(isOwner){permissions={manage_products:true,edit_prices:true,manage_orders:true};}else{let {data:staff}=await sb.from('store_staff').select('permissions,active').eq('user_id',user.id).maybeSingle();if(!staff?.active){await sb.auth.signOut();showError('هذا الحساب ليس لديه صلاحية إدارة.');return;}permissions={manage_products:staff.permissions?.manage_products===true,edit_prices:staff.permissions?.edit_prices===true,manage_orders:staff.permissions?.manage_orders===true};if(!Object.values(permissions).some(Boolean)){await sb.auth.signOut();showError('لم يمنحك المالك أي صلاحية بعد.');return;}}$('#loginCard').hidden=true;$('#adminPanel').hidden=false;$('#adminIdentity').textContent='مرحباً '+(profile.display_name||user.email)+' · '+(isOwner?'مالك المتجر':'أدمن المتجر');applyStaffUI();const jobs=[];if(permissions.manage_products||permissions.edit_prices)jobs.push(loadProducts());if(permissions.manage_products)jobs.push(loadCategories());if(permissions.manage_orders)jobs.push(loadOrders());if(isOwner)jobs.push(loadSettings());await Promise.all(jobs);}
function applyStaffUI(){const show=(tab,yes)=>{const b=document.querySelector('.admin-tabs [data-tab="'+tab+'"]');if(b)b.hidden=!yes;const pane=document.getElementById('pane-'+tab);if(pane)pane.hidden=!yes;};show('products',permissions.manage_products||permissions.edit_prices);show('categories',permissions.manage_products);show('orders',permissions.manage_orders);show('settings',isOwner);const add=$('#addProduct');if(add)add.hidden=!permissions.manage_products;const cat=$('#addCategory');if(cat)cat.hidden=!permissions.manage_products;}
async function loadProducts"""
src=src[:m.start()]+enter+src[m.end():]
src=src.replace('<div class="row-actions"><button data-edit-product="\${p.id}">تعديل</button><button class="danger" data-delete-product="\${p.id}">حذف</button></div>','<div class="row-actions">\${permissions.manage_products?\\'<button data-edit-product="\\'+p.id+\\'">تعديل</button><button class="danger" data-delete-product="\\'+p.id+\\'">حذف</button>\\':permissions.edit_prices?\\'<button data-edit-price="\\'+p.id+\\'">تعديل السعر</button>\\':\\'\\'}</div>')
needle="$('#adminProducts').querySelectorAll('[data-delete-product]').forEach(b=>b.onclick=()=>deleteProduct(b.dataset.deleteProduct));}"
replacement="""$('#adminProducts').querySelectorAll('[data-delete-product]').forEach(b=>b.onclick=()=>deleteProduct(b.dataset.deleteProduct));$('#adminProducts').querySelectorAll('[data-edit-price]').forEach(b=>b.onclick=async()=>{let p=products.find(x=>x.id===b.dataset.editPrice);if(!p)return;let raw=prompt('السعر الجديد بالدينار العراقي:',String(p.price_iqd));if(raw===null)return;let price=Number(String(raw).replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[^0-9]/g,''));if(!Number.isSafeInteger(price)||price<0)return toast('أدخل سعراً صحيحاً.');let {error}=await sb.from('products').update({price_iqd:price}).eq('id',p.id);if(error)return toast(error.message);toast('تم تحديث السعر');loadProducts();});}"""
if needle not in src: raise SystemExit("product handlers not found")
src=src.replace(needle,replacement,1)
src=src.replace("$('#addProduct').onclick=()=>{","$('#addProduct').onclick=()=>{if(!permissions.manage_products)return;")
src=src.replace("$('#addCategory').onclick=()=>{","$('#addCategory').onclick=()=>{if(!permissions.manage_products)return;")
src=src.replace("$('#settingsForm').onsubmit=saveSettings;","$('#settingsForm').onsubmit=e=>{if(!isOwner){e.preventDefault();return;}saveSettings(e);};")
admin.write_text(src,encoding="utf-8")
owner=root/"owner.html"
html=owner.read_text(encoding="utf-8")
if "kix-admin-staff.js" not in html:
 html=html.replace('<script src="admin.js" defer></script>','<script src="admin.js" defer></script><script src="kix-admin-staff.js?v=20261127-1" defer></script>')
owner.write_text(html,encoding="utf-8")
cssfile=root/"kix-brand-refresh.css"
css=cssfile.read_text(encoding="utf-8")
css+="""
/* Keep the owner entry point reachable from compact storefront headers. */
@media(max-width:650px){.head-actions .owner-link{display:inline-flex!important;align-items:center;white-space:nowrap;padding:6px 8px!important;font-size:10px!important;border-radius:9px}.head-actions{gap:6px!important}}
"""
cssfile.write_text(css,encoding="utf-8")
