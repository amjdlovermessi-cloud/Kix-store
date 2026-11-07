from pathlib import Path
import sys
site=Path(sys.argv[1])
root=Path(__file__).resolve().parent.parent
for name in ('kix-coupons.css','kix-coupons.js','kix-admin-coupons.js'):
    src=root/name
    if not src.exists(): raise SystemExit(f'Missing coupon asset: {src}')
    (site/name).write_bytes(src.read_bytes())
index=site/'index.html'
html=index.read_text(encoding='utf-8')
if 'kix-coupons.js' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="kix-coupons.css"><script src="kix-coupons.js" defer></script></head>',1)
index.write_text(html,encoding='utf-8')
owner=site/'owner.html'
if not owner.exists(): raise SystemExit('Coupon patch: owner.html missing.')
oh=owner.read_text(encoding='utf-8')
if 'kix-admin-coupons.js' not in oh:
    oh=oh.replace('</head>','<link rel="stylesheet" href="kix-coupons.css"><script src="kix-admin-coupons.js" defer></script></head>',1)
owner.write_text(oh,encoding='utf-8')
print('Coupon storefront and admin assets injected.')
