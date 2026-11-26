from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
patch = root / "security" / "patch_brand_refresh.py"
stylesheet = root / "kix-brand-refresh.css"
logo = root / "kix-symbol.svg"

with tempfile.TemporaryDirectory(prefix="kix-brand-test-") as temp:
    fixture = Path(temp)
    (fixture / "security").mkdir()
    shutil.copy2(patch, fixture / "security" / patch.name)
    shutil.copy2(stylesheet, fixture / stylesheet.name)
    shutil.copy2(logo, fixture / logo.name)

    site = fixture / "site"
    nested = site / "account" / "orders"
    nested.mkdir(parents=True)
    (site / "assets").mkdir()
    (site / "assets" / "kix-logo.png").write_bytes(b"legacy logo placeholder")
    (site / "index.html").write_text(
        '<html><head><title>Home</title><meta name="theme-color" content="#090b10"></head><body><a class="brand"><img src="assets/kix-logo.png"></a><section class="hero"><h1>ارتقِ بتجربتك<br><em>إلى المستوى التالي</em></h1><div class="hero-stage"><div class="stage-orbit"></div><button class="mascot-button"><img src="assets/kix-mascot-3d.png"></button><div class="coin">K</div></div></section></body></html>',
        encoding="utf-8",
    )
    (nested / "index.html").write_text(
        "<html><head><title>Orders</title></head><body></body></html>",
        encoding="utf-8",
    )

    command = [sys.executable, str(fixture / "security" / patch.name), str(site)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    home = (site / "index.html").read_text(encoding="utf-8")
    orders = (nested / "index.html").read_text(encoding="utf-8")

    assert 'href="kix-brand-refresh.css?v=20261126-3"' in home
    assert 'href="../../kix-brand-refresh.css?v=20261126-3"' in orders
    assert 'src="assets/kix-symbol.svg"' in home
    assert 'name="theme-color" content="#0B1020"' in home
    assert 'class="hero-visual"' in home
    assert "mascot-button" not in home
    assert "كل عالمك الرقمي" in home
    assert (site / "assets" / "kix-symbol.svg").is_file()
    assert (site / "favicon.svg").is_file()

    subprocess.run(command, check=True, capture_output=True, text=True)
    assert (site / "index.html").read_text(encoding="utf-8") == home
    assert (nested / "index.html").read_text(encoding="utf-8") == orders

print("Brand refresh regression test passed: nested pages, logo, homepage hero, theme color, and idempotency.")
