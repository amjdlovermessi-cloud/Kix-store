from pathlib import Path
import re
import sys

site = Path(sys.argv[1]).resolve()
index = site / "index.html"
if not index.is_file():
    raise SystemExit("Marketplace refinement: index.html not found")

repo_root = Path(__file__).resolve().parent.parent
stylesheet = repo_root / "kix-marketplace-refinement.css"
if not stylesheet.is_file():
    raise SystemExit(f"Missing marketplace stylesheet: {stylesheet}")
(site / "kix-marketplace-refinement.css").write_bytes(stylesheet.read_bytes())

html = index.read_text(encoding="utf-8")
html = html.replace(
    '<meta name="description" content="Kix Store، وجهتك للألعاب والاشتراكات والمنتجات الرقمية.">',
    '<meta name="description" content="وجهتك للمنتجات والخدمات الرقمية: ألعاب، اشتراكات مشاهدة، أدوات ذكاء اصطناعي، إنتاجية وتعلّم.">'
)
html = html.replace('<title>Kix Store | Play · Buy · Enjoy</title>', '<title>Kix Store | اكتشف عالمك الرقمي</title>')
html = html.replace(
    '<div class="announcement"><span class="pulse"></span> عالمك الرقمي يبدأ من Kix Store <b>✦</b> ألعاب واشتراكات وبطاقات رقمية</div>',
    '<div class="announcement"><span class="pulse"></span> وجهتك لكل ما هو رقمي <b>✦</b> ألعاب، مشاهدة، ذكاء اصطناعي، إنتاجية وتعلّم</div>'
)
html = html.replace('✦ اختيارات رقمية واضحة وتجربة أسهل', 'اختيارات أكثر. تفاصيل أوضح. تجربة شراء أسهل.')
html = html.replace('منتجات <em>Kix</em>', 'اكتشف ما يناسبك')
html = html.replace('اختَر منتجك وأضفه إلى السلة.', 'من الترفيه إلى أدوات العمل والتعلّم، اكتشف خدماتك الرقمية بمكان واحد.')

board = """<div class="hero-visual marketplace-board" aria-label="مجالات المتجر الرقمية">
        <div class="marketplace-board-head"><span>YOUR DIGITAL WORLD</span><b>01 / 05</b></div>
        <div class="marketplace-board-feature"><div class="marketplace-feature-copy"><small>DISCOVER MORE</small><strong>مساحة واحدة<br>لاحتمالات أكثر</strong><span>اختَر. استمتع. أنجز.</span></div><div class="marketplace-orbit-art" aria-hidden="true"><i></i><i></i><i></i><b>K</b></div></div>
        <div class="marketplace-board-list">
          <div><span class="marketplace-index">01</span><span class="marketplace-glyph">G</span><span class="marketplace-label"><strong>الألعاب والبطاقات</strong><small>GAMES & DIGITAL CARDS</small></span><b>↗</b></div>
          <div><span class="marketplace-index">02</span><span class="marketplace-glyph violet">S</span><span class="marketplace-label"><strong>المشاهدة والترفيه</strong><small>STREAMING & ENTERTAINMENT</small></span><b>↗</b></div>
          <div><span class="marketplace-index">03</span><span class="marketplace-glyph mint">AI</span><span class="marketplace-label"><strong>الذكاء الاصطناعي</strong><small>AI & SMART TOOLS</small></span><b>↗</b></div>
          <div><span class="marketplace-index">04</span><span class="marketplace-glyph">P</span><span class="marketplace-label"><strong>الإنتاجية والبرامج</strong><small>PRODUCTIVITY & SOFTWARE</small></span><b>↗</b></div>
          <div><span class="marketplace-index">05</span><span class="marketplace-glyph violet">L</span><span class="marketplace-label"><strong>التعلّم والمعرفة</strong><small>LEARNING & KNOWLEDGE</small></span><b>↗</b></div>
        </div>
      </div>"""
if "marketplace-board" not in html:
    html, count = re.subn(
        r'<div class="hero-visual" aria-hidden="true">[\s\S]*?(?=</section>)',
        board, html, count=1
    )
    if count != 1:
        raise SystemExit("Marketplace refinement: homepage hero visual was not found")

# The new shared stylesheet controls the footer cards, so remove their legacy red inline styles.
html = re.sub(r'<style>\.kix-instagram-footer\{[\s\S]*?</style>', '', html, count=1)
html = re.sub(r'<style>\.kix-social-footer\{[\s\S]*?</style>', '', html, count=1)

css_tag = '<link rel="stylesheet" href="kix-marketplace-refinement.css?v=20261127-1">'
if "kix-marketplace-refinement.css" not in html:
    html = re.sub(r'</head\s*>', css_tag + "\n</head>", html, count=1, flags=re.I)
index.write_text(html, encoding="utf-8")
print("Marketplace refinement installed: category-led hero, broader messaging, and shared footer styling.")
