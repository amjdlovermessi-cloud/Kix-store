from pathlib import Path
import sys

root = Path(sys.argv[1])
admin = root / 'admin.js'
html = root / 'owner.html'
js = admin.read_text(encoding='utf-8')
old_js = "async function saveCategory(e){e.preventDefault();let f=e.currentTarget,d=new FormData(f),payload={name:d.get('name'),subtitle:d.get('subtitle'),image_url:d.get('image_url'),sort_order:Number(d.get('sort_order')||0),active:true};let id=f.dataset.id,q=id?sb.from('categories').update(payload).eq('id',id):sb.from('categories').insert(payload);let {error}=await q;if(error)return toast(error.message);delete f.dataset.id;$('#categoryDialog').close();toast('تم حفظ القسم');await loadCategories();}"
new_js = "async function saveCategory(e){e.preventDefault();let f=e.currentTarget,d=new FormData(f),id=f.dataset.id,old=cats.find(x=>x.id===id),image=d.get('image'),url=old?.image_url||'assets/categories/ps5.webp';if(image?.size){if(!['image/png','image/jpeg','image/webp'].includes(image.type))return toast('اختر صورة PNG أو JPG أو WEBP فقط');if(image.size>6291456)return toast('حجم الصورة يجب ألا يتجاوز 6 ميغابايت');let ext=image.type==='image/jpeg'?'jpg':image.type.split('/')[1],path='categories/'+crypto.randomUUID()+'.'+ext;let {error}=await sb.storage.from('product-images').upload(path,image,{upsert:false,contentType:image.type});if(error)return toast(error.message);let {data}=sb.storage.from('product-images').getPublicUrl(path);url=data.publicUrl;}let payload={name:d.get('name'),subtitle:d.get('subtitle'),image_url:url,sort_order:Number(d.get('sort_order')||0),active:true};let q=id?sb.from('categories').update(payload).eq('id',id):sb.from('categories').insert(payload);let {error}=await q;if(error)return toast(error.message);delete f.dataset.id;$('#categoryDialog').close();toast('تم حفظ القسم');await loadCategories();}"
if old_js not in js: raise SystemExit('Could not locate saveCategory')
js = js.replace(old_js, new_js, 1)
h = html.read_text(encoding='utf-8')
old_field = '<label>رابط صورة الأيقونة<input name="image_url" placeholder="assets/categories/ps5.webp"></label>'
new_field = '<label class="wide">صورة القسم من الاستوديو<input name="image" type="file" accept="image/png,image/jpeg,image/webp"></label>'
if old_field not in h: raise SystemExit('Could not locate category image field')
h = h.replace(old_field, new_field, 1)
admin.write_text(js, encoding='utf-8')
html.write_text(h, encoding='utf-8')
