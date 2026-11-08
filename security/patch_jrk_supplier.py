from pathlib import Path
import shutil, sys

site = Path(sys.argv[1])
repo = Path(__file__).resolve().parent.parent
owner = next(site.rglob("owner.html"), None)
if owner is None:
    raise SystemExit("owner.html not found in extracted site")
target = owner.parent
for name in ("supplier.html", "jrk-supplier.js", "jrk-supplier.css"):
    source = repo / name
    if not source.exists():
        raise SystemExit(f"Missing supplier asset: {source}")
    shutil.copy2(source, target / name)

html = owner.read_text(encoding="utf-8")
link = '<a href="supplier.html" class="kix-jrk-supplier-link">كتالوج المورد Jrk AI</a>'
style = '<style>.kix-jrk-supplier-link{position:fixed;z-index:9999;left:16px;bottom:16px;background:#ed2638;color:#fff!important;padding:12px 16px;border-radius:12px;text-decoration:none;font:700 13px system-ui;box-shadow:0 6px 24px #0008}</style>'
if "supplier.html" not in html:
    if "</body>" in html:
        html = html.replace("</body>", style + link + "\n</body>", 1)
    else:
        html += style + link
    owner.write_text(html, encoding="utf-8")
print("Jrk AI supplier catalog page installed.")
