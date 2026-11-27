from pathlib import Path
import re
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
js = (root / "kix-commerce-enhancements.js").read_text(encoding="utf-8")
patch = (root / "security" / "patch_commerce_experience.py").read_text(encoding="utf-8")

assert "const cards=$$('.product-card',grid);" in js, "Sorting must collect all cards as an array"
assert "const sorted=cards.slice().sort(compare);" in js, "Sorting must sort a copy of the cards array"
assert "const cards=$('.product-card',grid);" not in js, "Regression: querySelector returns only one card"
assert "price-asc" in js and "price-desc" in js, "Both price sort directions must be present"
assert "name-asc" in js and "name-desc" in js, "Both alphabetical directions must be present"
assert "Intl.Collator('ar'" in js, "Arabic-aware alphabetical sorting must be used"
assert "Number.POSITIVE_INFINITY" in js, "Missing prices must sort after priced products"
assert "kix-commerce-enhancements.js?v=20261127-2" in patch
assert "kix-commerce-enhancements.css?v=20261127-2" in patch
print("KIX product sorting regression checks passed.")
