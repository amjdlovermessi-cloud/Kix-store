from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
patch = root / "security" / "patch_brand_refresh.py"
stylesheet = root / "kix-brand-refresh.css"

with tempfile.TemporaryDirectory(prefix="kix-brand-test-") as temp:
    fixture = Path(temp)
    (fixture / "security").mkdir()
    shutil.copy2(patch, fixture / "security" / patch.name)
    shutil.copy2(stylesheet, fixture / stylesheet.name)

    site = fixture / "site"
    nested = site / "account" / "orders"
    nested.mkdir(parents=True)
    (site / "index.html").write_text(
        "<html><head><title>Home</title></head><body></body></html>",
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

    assert 'href="kix-brand-refresh.css?v=20261125-3"' in home
    assert 'href="../../../kix-brand-refresh.css?v=20261125-3"' in orders
    assert home.count('name="theme-color"') == 1
    assert orders.count('name="theme-color"') == 1
    assert (site / "kix-brand-refresh.css").is_file()

    second = subprocess.run(command, check=True, capture_output=True, text=True)
    assert (site / "index.html").read_text(encoding="utf-8") == home
    assert (nested / "index.html").read_text(encoding="utf-8") == orders
    assert "already linked: 2" in second.stdout

print("Brand refresh regression test passed: root page, nested page, theme color, and idempotency.")
