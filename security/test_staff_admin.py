from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

root=Path(__file__).resolve().parent.parent
archive=root/"Kix-Store-Ready-to-Upload.zip"
patch=root/"security"/"patch_staff_admin.py"
with tempfile.TemporaryDirectory(prefix="kix-staff-test-") as tmp:
    site=Path(tmp)
    with zipfile.ZipFile(archive) as z:
        for name in ("admin.js","owner.html","kix-brand-refresh.css"):
            target=site/name
            target.write_bytes(z.read(name))
    subprocess.run([sys.executable,str(patch),str(site)],check=True,capture_output=True,text=True)
    admin=(site/"admin.js").read_text(encoding="utf-8")
    owner=(site/"owner.html").read_text(encoding="utf-8")
    css=(site/"kix-brand-refresh.css").read_text(encoding="utf-8")
    assert "store_staff" in admin
    assert "data-edit-price-only" in admin
    assert "applyStaffUI" in admin
    assert "kix-admin-staff.js" in owner
    assert (site/"kix-admin-staff.js").is_file()
    assert ".head-actions .owner-link{display:inline-flex!important" in css
    subprocess.run(["node","--check",str(site/"admin.js")],check=True,capture_output=True,text=True)
    subprocess.run(["node","--check",str(site/"kix-admin-staff.js")],check=True,capture_output=True,text=True)
print("Staff permissions and mobile owner link regression test passed.")
