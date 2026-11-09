from pathlib import Path
import re
import sys

site = Path(sys.argv[1])
index = site / "index.html"
if not index.exists():
    raise SystemExit("KIX performance patch: index.html not found")

html = index.read_text(encoding="utf-8")
# Stop loading the optional WebGL/Three.js mascot runtime. Keep the existing
# mascot image and its surrounding layout as a static brand logo.
html, removed_js = re.subn(
    r'<script\b(?=[^>]*\bsrc=["\'][^"\']*kix-mascot-3d\.js(?:\?[^"\']*)?["\'])[^>]*>\s*</script>',
    '',
    html,
    flags=re.I
)
html = re.sub(
    r'<link\b(?=[^>]*\bhref=["\'][^"\']*kix-mascot-3d\.css(?:\?[^"\']*)?["\'])[^>]*>',
    '',
    html,
    flags=re.I
)
asset = site / "kix-store-performance.css"
asset.write_text("""/* KIX lightweight mascot and readable category headings */
#mascotButton,.mascot-button,.mascot-button.flip{
  cursor:default!important;
  pointer-events:none!important;
  animation:none!important;
  transform:none!important;
  transition:none!important;
  filter:drop-shadow(0 8px 16px rgba(255,15,55,.12))!important;
}
#mascotButton img,.mascot-button img,.mascot-button:hover img,.mascot-button.flip img{
  display:block!important;visibility:visible!important;opacity:1!important;
  animation:none!important;transform:none!important;transition:none!important;
}
#kixMascotCanvas,.mascot-button canvas{display:none!important}
#categoryGrid .category-card strong{
  display:block!important;
  color:#f4c45e!important;
  font-family:"Cairo","Tajawal",Arial,sans-serif!important;
  font-weight:800!important;
  font-size:18px!important;
  line-height:1.55!important;
  text-shadow:0 1px 5px rgba(0,0,0,.78)!important;
  opacity:1!important;
}
#categoryGrid .category-card small{
  color:#d6cbd5!important;
  font-family:"Cairo","Tajawal",Arial,sans-serif!important;
  font-weight:600!important;
  font-size:13px!important;
}
@media(max-width:768px){
  #categoryGrid .category-card strong{font-size:14px!important}
  #categoryGrid .category-card small{font-size:11px!important}
}
""", encoding="utf-8")
tag = '<link rel="stylesheet" href="kix-store-performance.css?v=20261109-2">'
for old, new in (
    ('kix-currency.js', 'kix-currency.js?v=20261109-2'),
    ('kix-coupons.js', 'kix-coupons.js?v=20261109-2'),
    ('kix-new-features.js?v=20261107-5', 'kix-new-features.js?v=20261109-2'),
):
    html = html.replace('src="' + old + '"', 'src="' + new + '"')

if "kix-store-performance.css" not in html and "</head>" in html:
    html = html.replace("</head>", tag + "\n</head>", 1)
index.write_text(html, encoding="utf-8")

# The actual storefront mascot is a CSS-animated button, not the optional 3D module.
store_js = site / "store.js"
if store_js.exists():
    source = store_js.read_text(encoding="utf-8")
    source, count = re.subn(r'function\s+initMascot\s*\(\)\s*\{.*?\}', 'function initMascot(){}', source, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("Could not safely disable mascot click animation in store.js")
    store_js.write_text(source, encoding="utf-8")
print(f"KIX lightweight storefront styles installed; removed mascot runtime tags: {removed_js}.")
