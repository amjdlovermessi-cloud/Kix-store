from pathlib import Path
import sys,re
site=Path(sys.argv[1])
root=Path(__file__).resolve().parent.parent
for name in ('kix-order-enhancements.js','kix-order-enhancements.css'):
    src=root/name
    if not src.exists(): raise SystemExit(f'Missing order enhancement asset: {src}')
    (site/name).write_bytes(src.read_bytes())
index=next(site.rglob('index.html'))
html=index.read_text(encoding='utf-8')
if 'kix-order-enhancements.js' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-order-enhancements.css"><script src="kix-order-enhancements.js" defer></script></head>',1)
index.write_text(html,encoding='utf-8')
owner=next(site.rglob('owner.html'))
html=owner.read_text(encoding='utf-8')
if 'kix-order-enhancements.js' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-order-enhancements.css"><script src="kix-order-enhancements.js" defer></script></head>',1)
owner.write_text(html,encoding='utf-8')
coupon=site/'kix-coupons.js'
if coupon.exists():
    js=coupon.read_text(encoding='utf-8')
    js=js.replace('const amount=subtotal();','const amount=Number(window.KIX_CART_SUBTOTAL||subtotal());')
    js=js.replace("save.textContent='وفّرت '+money(data.discount_iqd)+'، المجموع بعد الخصم '+money(data.total_iqd);save.style.display='block';","save.textContent='وفّرت '+money(data.discount_iqd)+'، المجموع بعد الخصم '+money(data.total_iqd);save.dataset.discount=String(data.discount_iqd||0);save.dataset.total=String(data.total_iqd||0);save.style.display='block';window.dispatchEvent(new Event('kix-coupon-updated'));")
    js=js.replace('applied=null;msg.textContent=e.message','applied=null;save.dataset.discount="0";window.dispatchEvent(new Event(\'kix-coupon-updated\'));msg.textContent=e.message')
    coupon.write_text(js,encoding='utf-8')
print('KIX checkout totals and expandable admin order details installed.')
