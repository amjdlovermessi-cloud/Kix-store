from pathlib import Path
import os
import re
import sys

site = Path(sys.argv[1]).resolve()
pages = sorted(site.rglob("*.html"))
if not pages:
    raise SystemExit("KIX visual refresh: no HTML pages found")

repo_root = Path(__file__).resolve().parent.parent
source = repo_root / "kix-brand-refresh.css"
if not source.is_file():
    raise SystemExit(f"Missing visual foundation stylesheet: {source}")

target = site / "kix-brand-refresh.css"
target.write_bytes(source.read_bytes())

updated = 0
already_linked = 0
skipped = []
for page in pages:
    html = page.read_text(encoding="utf-8")
    if "kix-brand-refresh.css" in html:
        already_linked += 1
        continue
    if not re.search(r"</head\s*>", html, flags=re.I):
        skipped.append(str(page.relative_to(site)))
        continue

    relative_css = Path(os.path.relpath(target, page.parent)).as_posix()
    tag = f'<link rel="stylesheet" href="{relative_css}?v=20261125-4">'
    html, count = re.subn(r"</head\s*>", tag + "\n</head>", html, count=1, flags=re.I)
    if count != 1:
        skipped.append(str(page.relative_to(site)))
        continue
    if not re.search(r"""<meta\s+name=["']theme-color["']""", html, flags=re.I):
        html = re.sub(
            r"</head\s*>",
            '<meta name="theme-color" content="#090b10">\n</head>',
            html,
            count=1,
            flags=re.I,
        )
    page.write_text(html, encoding="utf-8")
    updated += 1

print(f"KIX visual refresh installed. Updated: {updated}; already linked: {already_linked}; skipped: {len(skipped)}.")
if skipped:
    print("Pages without a usable head element: " + ", ".join(skipped))
