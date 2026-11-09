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
    r'<script\\b(?=[^>]*\\bsrc=["\'][^"\']*kix-mascot-3d\\.js(?:\\?[^"\']*)?["\'])[^>]*>\\s*</script>',
    '',
    html,
    flags=re.I
)
html = re.sub(
    r'<link\\b(?=[^>]*\\bhref=["\'][^"\']*kix-mascot-3d\\.css(?:\\?[^"\']*)?["\'])[^>]*>',
    '',
    html,
    flags=re.I
)
asset = site / "kix-store-performance.css"
asset.write_text("/* KIX lightweight mascot and readable category headings */\n.hero-stage .mascot-button{\n  cursor:default!important;\n  pointer-events:none!important;\n  filter:drop-shadow(0 8px 16px rgba(255,15,55,.12))!important;\n  animation:none!important;\n}\n.hero-stage .mascot-button > img{\n  display:block!important;visibility:visible!important;opacity:1!important;\n  transform:none!important;transition:none!important;\n}\n#kixMascotCanvas,.hero-stage .mascot-button canvas{display:none!important}\n#categoryGrid h2,#categoryGrid h3,#categoryGrid h4,\n#categoryGrid .category-name,#categoryGrid .category-title,\n#categories h2,#categories h3,#categories h4,\n.category-card h2,.category-card h3,.category-card h4,\n.category-item h2,.category-item h3,.category-item h4,\n.categories-grid h2,.categories-grid h3,.categories-grid h4{\n  color:#f4c45e!important;\n  font-family:\"Cairo\",\"Tajawal\",Arial,sans-serif!important;\n  font-weight:800!important;\n  letter-spacing:0!important;\n  line-height:1.55!important;\n  text-shadow:0 1px 5px rgba(0,0,0,.72)!important;\n  opacity:1!important;\n}\n#categoryGrid a,#categoryGrid button,\n#categories a,.category-card,.category-item{\n  color:#f4c45e;\n}\n@media(min-width:769px){\n  #categoryGrid h2,#categoryGrid h3,#categoryGrid h4,\n  #categoryGrid .category-name,#categoryGrid .category-title,\n  #categories h2,#categories h3,#categories h4,\n  .category-card h2,.category-card h3,.category-card h4,\n  .category-item h2,.category-item h3,.category-item h4,\n  .categories-grid h2,.categories-grid h3,.categories-grid h4{\n    font-size:18px!important;\n  }\n}\n@media(max-width:768px){\n  #categoryGrid h2,#categoryGrid h3,#categoryGrid h4,\n  #categoryGrid .category-name,#categoryGrid .category-title,\n  #categories h2,#categories h3,#categories h4,\n  .category-card h2,.category-card h3,.category-card h4,\n  .category-item h2,.category-item h3,.category-item h4,\n  .categories-grid h2,.categories-grid h3,.categories-grid h4{\n    font-size:15px!important;\n  }\n}\n", encoding="utf-8")
tag = '<link rel="stylesheet" href="kix-store-performance.css?v=20261109-1">'
if "kix-store-performance.css" not in html and "</head>" in html:
    html = html.replace("</head>", tag + "\\n</head>", 1)
index.write_text(html, encoding="utf-8")
print(f"KIX lightweight storefront styles installed; removed mascot runtime tags: {removed_js}.")
