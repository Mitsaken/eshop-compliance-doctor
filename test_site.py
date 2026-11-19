"""
eShop Compliance Audit — Automated Zero-AI & E2E Test Suite
"""

import http.server
import re
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

DIST_DIR = Path(__file__).parent / "dist"
PORT = 8999
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def start_server():
    class ReusableTCP(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCP(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def test_static_and_design_lint():
    print("[Test 1/5] Verifying Zero-AI Design Lint, Self-Hosted Fonts & Strict CSP...")
    assert (DIST_DIR / "index.html").exists(), "index.html missing"
    assert (DIST_DIR / "styles.css").exists(), "styles.css missing"
    assert (DIST_DIR / "engine.js").exists(), "engine.js missing"
    assert (DIST_DIR / "app.js").exists(), "app.js missing"
    assert (DIST_DIR / "privacy.html").exists(), "privacy.html missing"
    assert (DIST_DIR / "_headers").exists(), "_headers missing"
    assert "eshop-compliance-doctor.pages.dev" in (DIST_DIR / "sitemap.xml").read_text(encoding="utf-8")

    font_bytes = sum(f.stat().st_size for f in (DIST_DIR / "assets" / "fonts").glob("*.woff2"))
    assert 10000 < font_bytes <= 150000, f"Font payload budget exceeded: {font_bytes} B"

    index_html = (DIST_DIR / "index.html").read_text(encoding="utf-8")
    styles_css = (DIST_DIR / "styles.css").read_text(encoding="utf-8")
    for bad in ["cdn.tailwindcss.com", "unpkg.com", "fonts.googleapis.com", "fonts.gstatic.com", "unsafe-inline", "onclick=", "payhip.com", "29€", "69€", "animate-pulse", "blur-3xl"]:
        assert bad not in index_html, f"Forbidden token in index.html: {bad}"
    assert "linear-gradient" not in styles_css, "Gradients forbidden in Zero-AI CSS"
    assert not EMOJI_RE.search(index_html), "Emojis forbidden in HTML UI"
    assert "eShop Compliance Audit" in index_html, "New Audit brand title missing"
    print(f"   -> PASS: Pure Light Dossier, {font_bytes:,}B self-hosted WOFF2, strict CSP (0 unsafe-inline).")


def test_e2e_playwright():
    httpd = start_server()
    time.sleep(0.3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 800}, permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            console_errs = []
            page.on("pageerror", lambda e: console_errs.append(str(e)))
            page.on("console", lambda m: console_errs.append(m.text) if m.type == "error" else None)

            external_requests = []
            page.on("request", lambda req: external_requests.append(req.url) if not req.url.startswith(f"http://127.0.0.1:{PORT}") and not req.url.startswith("data:") else None)

            print("[Test 2/5] Verifying Strict CSP, Self-Hosted Fonts Loaded & 0 Network Leaks...")
            page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")
            assert len(external_requests) == 0, f"External requests detected: {external_requests}"
            bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
            assert bg == "rgb(245, 245, 243)", f"Expected #F5F5F3 paper bg, got {bg}"
            loaded_fonts = page.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
            assert any("IBM Plex Sans" in f for f in loaded_fonts), f"Self-hosted Plex font not loaded: {loaded_fonts}"
            print(f"   -> PASS: 0 external leaks, loaded fonts={loaded_fonts}, paper bg={bg}.")

            print("[Test 3/5] Verifying 1-Click Samples, Active 2026 Statutes, Scope Disclaimer & Synonyms...")
            page.click("button[data-sample='compliant']")
            page.wait_for_timeout(200)
            assert int(page.locator("#scoreValue").inner_text()) >= 90
            assert page.locator("#statCritical").inner_text() == "0"
            assert "EL-ESH-02" in page.inner_text("#resultsContainer")
            assert "Εν Ισχύ" in page.inner_text("#resultsContainer")
            assert "Draft" not in page.inner_text("#resultsContainer")
            assert page.locator("#scopeDisclaimerBanner").is_visible()
            assert page.locator("#achEpistemicPanel").is_visible()
            assert "0 διαψεύσεις" in page.inner_text("#achRefuteSummary")
            assert "Εκκρεμείς Υποθέσεις" in (page.locator("#achEpistemicPanel").text_content() or "")

            # Conditional Art. 3za vs 3ib check
            dig_checks = page.evaluate("""() => {
                const txt = 'Εταιρεια Digital, ΓΕΜΗ 123, ΑΦΜ 123456789, εδρα Αθηνα. Δηλωνω οτι με την προηγουμενη ρητη συγκαταθεση μου στην αμεση παροχη ψηφιακου περιεχομενου αποδεχομαι την απωλεια του δικαιωματος υπαναχωρησης.';
                const rDig = window.eshopComplianceEngine.auditPolicy(txt, { storeType: 'digital_waived' }).results;
                const rPhys = window.eshopComplianceEngine.auditPolicy(txt, { storeType: 'physical' }).results;
                return {
                    digPass: rDig.find(x => x.id === 'electronic_withdrawal_button_2026')?.passed === true,
                    physFail: rPhys.find(x => x.id === 'electronic_withdrawal_button_2026')?.passed === false
                };
            }""")
            assert dig_checks["digPass"] and dig_checks["physFail"], f"Conditional Art 3za/3ib logic failed: {dig_checks}"

            syn_ok = page.evaluate("""() => {
                const sample = 'Εταιρεια ΑΒΓ, ΓΕΜΗ 123456, ΑΦΜ 123456789, εδρα Αθηνα. Δικαιωμα ακυρωσης παραγγελιας εντος 14 ημερων με επιστροφη χρηματων στο αρχικο μεσο πληρωμης και ηλεκτρονικη φορμα ακυρωσης (κουμπι ακυρωσης).';
                const r = window.eshopComplianceEngine.auditPolicy(sample).results;
                return ['withdrawal_14_days', 'electronic_withdrawal_button_2026', 'refund_deadline_method', 'gemi_and_tax_details']
                    .every(id => r.find(x => x.id === id)?.passed === true);
            }""")
            assert syn_ok, "Greek synonym / unaccented matching failed!"

            page.click("button[data-sample='illegal_refund']")
            page.wait_for_timeout(200)
            assert int(page.locator("#scoreValue").inner_text()) < 60
            crit_illegal = int(page.locator("#statCritical").inner_text())
            assert crit_illegal >= 2
            assert page.locator("#criticalWarningBanner").is_visible()
            assert "κρίσιμες διαψεύσεις" in page.inner_text("#achRefuteSummary")
            assert page.locator("#proWaitlistAdvice").count() == 1
            assert not EMOJI_RE.search(page.inner_text("body")), "Emojis rendered in DOM findings!"

            md = page.evaluate("window.eshopComplianceEngine.generateMarkdownReport(window.eshopComplianceEngine.auditPolicy(document.getElementById('policyInput').value), 'TestStore')")
            assert not EMOJI_RE.search(md), "Emojis present in exported Markdown report!"
            assert "Όριο Ελέγχου" in md
            print("   -> PASS: 14-point registry, Active 2026 statutes, synonyms, scope banner & zero emojis verified.")

            print("[Test 4/5] Verifying Filter Tabs, Copy Action & Waitlist GDPR Guard...")
            page.click("#filter-critical")
            page.wait_for_timeout(150)
            assert len(page.locator(".audit-item-card").all()) >= crit_illegal

            copy_btn = page.locator("button[id^='copy-btn-']").first
            copy_btn.click()
            page.wait_for_timeout(150)
            assert "Αντιγράφηκε" in copy_btn.inner_text()

            consent_cb = page.locator("#proWaitlistConsent")
            assert not consent_cb.is_checked(), "Consent checkbox must start unchecked"
            page.locator("#proWaitlistEmail").fill("shop@example.com")
            page.locator("#proWaitlistBtn").click()
            assert "συγκατάθεσ" in page.locator("#proWaitlistMsg").inner_text().lower()
            assert len(external_requests) == 0
            print("   -> PASS: Filters, clause copy & GDPR Waitlist guard verified.")

            print("[Test 5/5] Verifying Mobile 390px & 320px Zero Horizontal Overflow...")
            for width in (390, 320):
                page.set_viewport_size({"width": width, "height": 844})
                page.wait_for_timeout(200)
                diff = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                assert diff <= 0, f"Horizontal overflow @ {width}px: {diff}px"
            assert not console_errs, f"Console/CSP errors: {console_errs}"
            print("   -> PASS: 390px & 320px viewports clean (0px overflow, 0 CSP/console errors).")

            browser.close()
    finally:
        httpd.shutdown()
    print("\nALL 5 P4 ZERO-AI AUDIT TEST SUITES PASSED!")


if __name__ == "__main__":
    test_static_and_design_lint()
    test_e2e_playwright()
