from pathlib import Path
import sys

site = Path(sys.argv[1])
index_files = list(site.rglob("index.html"))
store_files = list(site.rglob("store.js"))
if len(index_files) != 1 or len(store_files) != 1:
    raise SystemExit("Expected exactly one index.html and one store.js in the extracted site.")

index = index_files[0]
html = index.read_text(encoding="utf-8")
needle = '<div id="paymentInstructions"'
trap = '<div aria-hidden="true" style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden"><label>اترك هذا الحقل فارغاً<input name="website" type="text" tabindex="-1" autocomplete="off"></label></div>'
if 'name="website"' not in html:
    if needle not in html:
        raise SystemExit("Checkout form insertion point was not found.")
    html = html.replace(needle, trap + needle, 1)
    index.write_text(html, encoding="utf-8")

store = store_files[0]
js = store.read_text(encoding="utf-8")
old = "payment_method:f.get('payment_method'),items"
new = "payment_method:f.get('payment_method'),website:f.get('website'),items"
if new not in js:
    if old not in js:
        raise SystemExit("Checkout payload insertion point was not found.")
    js = js.replace(old, new, 1)
    store.write_text(js, encoding="utf-8")

print("Checkout honeypot patch applied.")
