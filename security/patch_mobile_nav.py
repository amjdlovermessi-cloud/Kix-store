from pathlib import Path
import sys

site = Path(sys.argv[1])
index = site / "index.html"
if not index.exists():
    raise SystemExit("Mobile navigation patch failed: index.html not found")

js = r"""
(() => {
  if (window.__kixMobileNavCloseInstalled) return;
  window.__kixMobileNavCloseInstalled = true;

  const isMobile = () => window.matchMedia("(max-width: 768px)").matches;
  const isOpen = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" &&
      el.getAttribute("aria-expanded") === "true";
  };

  document.addEventListener("click", (event) => {
    if (!isMobile()) return;
    const link = event.target.closest("a");
    if (!link) return;

    const href = link.getAttribute("href") || "";
    const isSectionLink = href.startsWith("#") ||
      /^(الرئيسية|الأقسام|المنتجات|طريقة الشراء|تواصل معنا)$/.test(link.textContent.trim());
    if (!isSectionLink) return;

    requestAnimationFrame(() => {
      const toggles = [
        ...document.querySelectorAll(
          '[aria-expanded="true"], .menu-toggle, .nav-toggle, .hamburger, ' +
          '.navbar-toggler, #menuToggle, #navToggle, [aria-label*="menu" i]'
        )
      ];

      const toggle = toggles.find((el) =>
        el.matches('button, [role="button"]') &&
        (el.getAttribute("aria-expanded") === "true" ||
         /menu|nav|hamburger|toggle/i.test((el.id || "") + " " + (el.className || "")))
      );

      if (toggle && isOpen(toggle)) {
        toggle.click();
        return;
      }

      const menus = document.querySelectorAll(
        "nav, .nav-menu, .navbar-menu, .mobile-menu, .menu-panel, .dropdown-menu"
      );
      for (const menu of menus) {
        const rect = menu.getBoundingClientRect();
        const style = getComputedStyle(menu);
        const visible = rect.width > 0 && rect.height > 0 &&
          style.display !== "none" && style.visibility !== "hidden";
        if (!visible || !menu.contains(link)) continue;
        menu.classList.remove("active", "open", "show", "expanded");
        menu.setAttribute("aria-hidden", "true");
        break;
      }
    });
  }, true);
})();
""".strip()

asset = site / "kix-mobile-nav.js"
asset.write_text(js + "\n", encoding="utf-8")
html = index.read_text(encoding="utf-8")
tag = '<script src="kix-mobile-nav.js" defer></script>'
if "kix-mobile-nav.js" not in html:
    if "</body>" in html:
        html = html.replace("</body>", tag + "\n</body>", 1)
    else:
        html += "\n" + tag + "\n"
    index.write_text(html, encoding="utf-8")

print("Mobile navigation close-on-selection patch installed.")
