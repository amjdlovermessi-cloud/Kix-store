from pathlib import Path
import sys

site = Path(sys.argv[1])
pages = list(site.rglob("*.html"))
if not pages:
    raise SystemExit("KIX redesign foundation: no HTML pages found")

root = Path(__file__).resolve().parent.parent
source = root / "kix-brand-refresh.css"
if not source.exists():
    raise SystemExit(f"Missing visual foundation stylesheet: {source}")
(site / "kix-brand-refresh.css").write_bytes(source.read_bytes())

tag = '<link rel="stylesheet" href="kix-brand-refresh.css?v=20261125-1">'
updated = 0
for page in pages:
    html = page.read_text(encoding="utf-8")
    if "kix-brand-refresh.css" in html:
        continue
    if "</head>" not in html:
        continue
    html = html.replace("</head>", tag + "\n</head>", 1)
    # Add a consistent mobile browser theme color without disturbing existing metadata.
    if 'name="theme-color"' not in html:
        html = html.replace("</head>", '<meta name="theme-color" content="#090b10">\n</head>', 1)
    page.write_text(html, encoding="utf-8")
    updated += 1

print(f"KIX visual foundation installed on {updated} HTML pages.")
