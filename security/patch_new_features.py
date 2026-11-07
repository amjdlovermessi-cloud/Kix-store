from pathlib import Path
import sys
site=Path(sys.argv[1]); root=Path(__file__).resolve().parent.parent
for name in ('kix-new-features.js','kix-new-features.css'):
 src=root/name
 if not src.exists(): raise SystemExit(f'Missing {src}')
 (site/name).write_bytes(src.read_bytes())
for name in ('index.html','owner.html'):
 p=site/name; html=p.read_text(encoding='utf-8')
 html=html.replace('href="kix-new-features.css"','href="kix-new-features.css?v=20261107-4"')
 html=html.replace('src="kix-new-features.js"','src="kix-new-features.js?v=20261107-4"')
 if 'kix-new-features.js' not in html:
  html=html.replace('</head>','<link rel="stylesheet" href="kix-new-features.css?v=20261107-4"><script src="kix-new-features.js?v=20261107-4" defer></script></head>',1)
 p.write_text(html,encoding='utf-8')
print('KIX cart sharing, receipt UI, order code copy and admin search installed.')
