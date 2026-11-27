from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
patch = root / "security" / "patch_marketplace_refinement.py"
stylesheet = root / "kix-marketplace-refinement.css"
with tempfile.TemporaryDirectory(prefix="kix-market-test-") as tmp:
    site = Path(tmp)
    (site / "index.html").write_text("""<!doctype html><html><head><meta name="description" content="Kix Store، وجهتك للألعاب والاشتراكات والمنتجات الرقمية."><title>Kix Store | Play · Buy · Enjoy</title></head><body><div class="announcement"><span class="pulse"></span> عالمك الرقمي يبدأ من Kix Store <b>✦</b> ألعاب واشتراكات وبطاقات رقمية</div><section class="hero wrap"><div class="hero-copy"><h1>كل عالمك الرقمي</h1><div class="hero-note">✦ اختيارات رقمية واضحة وتجربة أسهل</div></div><div class="hero-visual" aria-hidden="true"><div class="hero-mark"><img src="assets/kix-symbol.svg"></div></div></section><h2>منتجات <em>Kix</em></h2><p>اختَر منتجك وأضفه إلى السلة.</p><section class="kix-instagram-footer"><style>.kix-instagram-footer{color:red}</style></section><section class="kix-social-footer"><style>.kix-social-footer{color:red}</style></section></body></html>""", encoding="utf-8")
    (site / "kix-marketplace-refinement.css").write_text(stylesheet.read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run([sys.executable, str(patch), str(site)], check=True, capture_output=True, text=True)
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "marketplace-board" in html
    assert "marketplace-board-list" not in html
    assert "الألعاب والبطاقات" not in html
    assert "assets/kix-mascot-3d.png" in html
    assert "kix-marketplace-refinement.css?v=20261127-3" in html
    assert "وجهتك لكل ما هو رقمي" in html
    assert "اكتشف ما يناسبك" in html
    assert "rgba(255,55,75" not in html
    before = html
    subprocess.run([sys.executable, str(patch), str(site)], check=True, capture_output=True, text=True)
    assert (site / "index.html").read_text(encoding="utf-8") == before
print("Marketplace refinement regression test passed.")
