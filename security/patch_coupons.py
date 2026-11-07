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
if 'id="kixCouponBox"' not in html:
    marker='<div id="paymentInstructions"'
    if marker not in html: raise SystemExit('Coupon patch: paymentInstructions anchor missing from storefront.')
    markup='<section id="kixCouponBox" class="kix-coupon-box"><div class="kix-coupon-title">🎟️ عندك كود خصم؟</div><div class="kix-coupon-row"><input id="kixCouponInput" maxlength="32" placeholder="اكتب كود الخصم"><button id="kixCouponApply" type="button">تطبيق الكود</button></div><div id="kixCouponMessage" class="kix-coupon-msg">أدخل الكود واضغط تطبيق قبل تأكيد الطلب.</div><div id="kixCouponSavings" class="kix-coupon-savings"></div></section>'
    html=html.replace(marker,markup+marker,1)
index.write_text(html,encoding='utf-8')
owner=site/'owner.html'
if not owner.exists(): raise SystemExit('Coupon patch: owner.html missing.')
oh=owner.read_text(encoding='utf-8')
if 'kix-admin-coupons.js' not in oh:
    oh=oh.replace('</head>','<link rel="stylesheet" href="kix-coupons.css"><script src="kix-admin-coupons.js" defer></script></head>',1)
owner.write_text(oh,encoding='utf-8')
print('Coupon storefront and admin assets injected.')
