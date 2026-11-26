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
logo_source = repo_root / "kix-symbol.svg"
if not source.is_file():
    raise SystemExit(f"Missing visual foundation stylesheet: {source}")
if not logo_source.is_file():
    raise SystemExit(f"Missing geometric logo asset: {logo_source}")

target = site / "kix-brand-refresh.css"
target.write_bytes(source.read_bytes())
assets = site / "assets"
assets.mkdir(parents=True, exist_ok=True)
logo_target = assets / "kix-symbol.svg"
logo_target.write_bytes(logo_source.read_bytes())
(site / "favicon.svg").write_bytes(logo_source.read_bytes())

updated = 0
already_linked = 0
skipped = []
for page in pages:
    html = page.read_text(encoding="utf-8")
    relative_css = Path(os.path.relpath(target, page.parent)).as_posix()
    css_tag = f'<link rel="stylesheet" href="{relative_css}?v=20261126-1">'
    if "kix-brand-refresh.css" in html:
        html = re.sub(
            r'<link\b[^>]*href=["\'][^"\']*kix-brand-refresh\.css[^"\']*["\'][^>]*>',
            css_tag,
            html,
            count=1,
            flags=re.I,
        )
        already_linked += 1
    else:
        if not re.search(r"</head\s*>", html, flags=re.I):
            skipped.append(str(page.relative_to(site)))
            continue
        html = re.sub(r"</head\s*>", css_tag + "\n</head>", html, count=1, flags=re.I)

    relative_logo = Path(os.path.relpath(logo_target, page.parent)).as_posix()
    html = re.sub(
        r'(?P<before>src=["\'])(?:\./)?assets/kix-logo\.png(?P<after>["\'])',
        lambda m: m.group("before") + relative_logo + m.group("after"),
        html,
        flags=re.I,
    )

    if re.search(r'<meta\s+name=["\']theme-color["\']', html, flags=re.I):
        html = re.sub(
            r'(<meta\s+name=["\']theme-color["\']\s+content=["\'])[^"\']*(["\'][^>]*>)',
            r'\g<1>#0B1020\g<2>',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = re.sub(
            r"</head\s*>",
            '<meta name="theme-color" content="#0B1020">\n</head>',
            html,
            count=1,
            flags=re.I,
        )
    page.write_text(html, encoding="utf-8")
    updated += 1

print(f"KIX visual evolution installed. Updated: {updated}; already linked: {already_linked}; skipped: {len(skipped)}.")
if skipped:
    print("Pages without a usable head element: " + ", ".join(skipped))
