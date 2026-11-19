"""
eShop Compliance Audit — Static Site Generator (Zero-AI Paper-First Build)
Zero External CDNs, Strict CSP (No unsafe-inline), Self-Hosted Fonts, 100% Client-Side
"""

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
CONFIG = json.loads((ROOT / "site_config.json").read_text(encoding="utf-8"))

SITE_URL = CONFIG["CANONICAL_URL"]
WAITLIST_ORIGIN = CONFIG["WAITLIST_ENDPOINT"]
BRAND_NAME = CONFIG["BRAND_NAME"]
LAST_REVIEW = CONFIG["LAST_REVIEW_DATE"]
GOOGLE_VERIFY = "cddcb0945a7b4e49"

CSP_MAIN = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "font-src 'self'; "
    "img-src 'self' data:; "
    f"connect-src 'self' {WAITLIST_ORIGIN}; "
    f"form-action 'self' {WAITLIST_ORIGIN};"
)


def clean_and_prep_dist():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)


def transform_html(raw_html: str) -> str:
    raw_html = re.sub(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', raw_html)
    raw_html = re.sub(r'<script[^>]+cdn\.tailwindcss\.com[^>]*></script>', '', raw_html)
    raw_html = re.sub(r'<script[^>]+unpkg\.com[^>]*></script>', '', raw_html)

    csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{CSP_MAIN}">'
    gsc_meta = f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">'
    canonical_link = f'<link rel="canonical" href="{SITE_URL}/">'

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "name": f"{BRAND_NAME}",
                "url": f"{SITE_URL}/",
                "operatingSystem": "All modern browsers",
                "applicationCategory": "BusinessApplication",
                "inLanguage": "el",
                "isAccessibleForFree": True,
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "EUR"
                },
                "description": "Ανεξάρτητο εργαλείο τεχνικού προελέγχου κανονιστικής συμμόρφωσης Όρων Χρήσης & Επιστροφών για ελληνικά e-shops (Ν. 5317/2026, EmpCo, ODR 2024/3228, Omnibus, Γ.Ε.ΜΗ.).",
                "author": {"@type": "Organization", "name": "Conversionlogic"}
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Πότε είναι υποχρεωτικό το Κουμπί Υπαναχώρησης του Ν. 5317/2026 (Άρθρο 3ζα);",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Ισχύει για όλες τις συμβάσεις εξ αποστάσεως όπου ο καταναλωτής έχει δικαίωμα 14ήμερης αναιτιολόγητης υπαναχώρησης. Για άμεσα ψηφιακά downloads με ρητή προηγούμενη συγκατάθεση και αναγνώριση απώλειας δικαιώματος βάσει Άρθρου 3ιβ περ. ιγ' Ν. 2251/1994, εφαρμόζεται η νόμιμη εξαίρεση."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Γιατί πρέπει να διαγραφεί ο σύνδεσμος της ευρωπαϊκής πλατφόρμας ODR;",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Βάσει του Κανονισμού (ΕΕ) 2024/3228, η ευρωπαϊκή πλατφόρμα ODR καταργήθηκε οριστικά από 20/07/2025. Τα ελληνικά e-shops οφείλουν να παραπέμπουν στον Συνήγορο του Καταναλωτή και στο ECC Greece."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Τι ελέγχει η ΔΙ.Μ.Ε.Α. βάσει Οδηγίας EmpCo 2024/825 & Omnibus Ν. 4933/2022;",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Από 27/09/2026 απαιτείται εναρμονισμένη ανακοίνωση της 2ετούς νόμιμης εγγύησης και ενημέρωση για updates λογισμικού ψηφιακών συσκευών, ενώ κάθε έκπτωση τιμής πρέπει να αναγράφει τη χαμηλότερη τιμή των τελευταίων 30 ημερών."
                        }
                    }
                ]
            }
        ]
    }
    json_ld_script = f'<script type="application/ld+json">\n{json.dumps(json_ld, ensure_ascii=False, indent=2)}\n</script>'
    og_tags = (
        '<meta property="og:type" content="website">\n'
        '  <meta property="og:locale" content="el_GR">\n'
        '  <meta property="og:title" content="eShop Compliance Audit — Προέλεγχος 14 Σημείων ΔΙ.Μ.Ε.Α. &amp; Ν. 5317/2026">\n'
        '  <meta property="og:description" content="Τοπικός έλεγχος Όρων Χρήσης &amp; Επιστροφών ελληνικών e-shops (100% browser, 0 uploads): Κουμπί Υπαναχώρησης Άρθρο 3ζα, EmpCo 2024/825, κατάργηση ODR, Γ.Ε.ΜΗ. &amp; Omnibus.">\n'
        f'  <meta property="og:url" content="{SITE_URL}/">\n'
        '  <meta name="twitter:card" content="summary">\n'
        '  <meta name="twitter:title" content="eShop Compliance Audit — Κανονιστικός Προέλεγχος 2026">\n'
        '  <meta name="twitter:description" content="14 κανονιστικά σημεία ελέγχου (Ν. 5317/2026, EmpCo, ODR, Omnibus) τοπικά στον browser.">'
    )

    # Inject CSP FIRST inside <head>
    head_insert = f"\n  {csp_meta}\n  {gsc_meta}\n  {canonical_link}\n  {og_tags}\n  {json_ld_script}\n"
    raw_html = raw_html.replace('<head>', f'<head>{head_insert}', 1)
    return raw_html


def generate_privacy_page():
    csp_priv = "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; connect-src 'self';"
    privacy_html = f"""<!DOCTYPE html>
<html lang="el">
<head>
  <meta http-equiv="Content-Security-Policy" content="{csp_priv}">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Πολιτική Απορρήτου &amp; Νομική Σημείωση | {BRAND_NAME}</title>
  <meta name="description" content="Πολιτική απορρήτου, GDPR συγκατάθεση, εξαιρέσεις Άρθρου 3ιβ Ν. 2251/1994 και νομική σημείωση μη επίσημου εργαλείου.">
  <link rel="canonical" href="{SITE_URL}/privacy.html">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main class="legal-card">
    <span class="brand-kicker">Conversionlogic · Legal Documentation</span>
    <h1>Πολιτική Απορρήτου &amp; Νομική Σημείωση</h1>
    <p>Το <strong>{BRAND_NAME}</strong> λειτουργεί ως ανεξάρτητο διαγνωστικό εργαλείο προελέγχου σε καθεστώς <strong>0€ Validation Mode</strong> (χωρίς πωλήσεις ή χρηματικές συναλλαγές).</p>
    <h2>1. Τοπική Επεξεργασία, Μηδενική Αποθήκευση &amp; Μηδενικά Cookies</h2>
    <ul>
      <li>Τα κείμενα πολιτικών που επικολλάτε αναλύονται αποκλειστικά τοπικά στον browser σας και <strong>δεν αποθηκεύονται</strong> ούτε σε servers ούτε σε <code>localStorage</code>.</li>
      <li>Δεν χρησιμοποιούνται cookies παρακολούθησης, analytics ή εξωτερικές γραμματοσειρές/CDNs.</li>
    </ul>
    <h2>2. Λίστα Αναμονής (GDPR Άρθρο 6 παρ. 1α)</h2>
    <p>Η εγγραφή email στη λίστα αναμονής είναι προαιρετική, απαιτεί ρητή επιλογή του μη προεπιλεγμένου πλαισίου συγκατάθεσης και χρησιμοποιείται αποκλειστικά για ενημερώσεις συμμόρφωσης e-shop. Μπορείτε να ζητήσετε διαγραφή οποτεδήποτε.</p>
    <h2>3. Καθεστώς Μητρώου &amp; Μη Επίσημη Ιδιότητα</h2>
    <p>Το εργαλείο δεν συνδέεται με τη Γενική Γραμματεία Καταναλωτή ή το Γ.Ε.ΜΗ., εξετάζει μόνο το επικολλημένο κείμενο (όχι το ζωντανό checkout), και η απουσία ευρήματος δεν συνιστά επίσημη βεβαίωση συμμόρφωσης. Οι διατάξεις Ν. 5317/2026 (Άρθρο 3ζα Ν. 2251/1994, ΦΕΚ 10/07/2026), Οδ. EmpCo 2024/825 (εφαρμογή 27/09/2026) &amp; Κανονισμού ΕΕ 2024/3228 αποτυπώνονται ως εν ισχύ πλαίσιο 2026, με επιφύλαξη των εξαιρέσεων του Άρθρου 3ιβ Ν. 2251/1994.</p>
    <p><strong>Τελευταία Αναθεώρηση Μητρώου:</strong> {LAST_REVIEW}</p>
    <a href="/" class="legal-back">&larr; Επιστροφή στον Έλεγχο Συμμόρφωσης</a>
  </main>
</body>
</html>"""
    (DIST / "privacy.html").write_text(privacy_html, encoding="utf-8")


def generate_sitemap():
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{LAST_REVIEW}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE_URL}/privacy.html</loc>
    <lastmod>{LAST_REVIEW}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>
</urlset>
"""
    (DIST / "sitemap.xml").write_text(sitemap.strip(), encoding="utf-8")


def generate_robots():
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    (DIST / "robots.txt").write_text(robots.strip(), encoding="utf-8")


def generate_gsc_verification_file():
    (DIST / f"google{GOOGLE_VERIFY}.html").write_text(f"google-site-verification: google{GOOGLE_VERIFY}.html", encoding="utf-8")


def generate_headers():
    headers = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: geolocation=(), camera=(), microphone=()
"""
    (DIST / "_headers").write_text(headers, encoding="utf-8")


def create_zip():
    zip_path = ROOT / "site.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in sorted(DIST.rglob("*")):
            if file.is_file():
                zipf.write(file, arcname=file.relative_to(DIST).as_posix())
    print(f"Created Cloudflare ZIP: {zip_path} ({zip_path.stat().st_size:,} bytes)")


def build():
    print(f"Building {BRAND_NAME} Static Site...")
    clean_and_prep_dist()

    shutil.copy2(ROOT / "styles.css", DIST / "styles.css")
    shutil.copy2(ROOT / "engine.js", DIST / "engine.js")
    shutil.copy2(ROOT / "app.js", DIST / "app.js")
    if (ROOT / "assets").exists():
        shutil.copytree(ROOT / "assets", DIST / "assets")

    raw_html = (ROOT / "index_template.html").read_text(encoding="utf-8")
    transformed = transform_html(raw_html)
    (DIST / "index.html").write_text(transformed, encoding="utf-8")

    generate_privacy_page()
    generate_sitemap()
    generate_robots()
    generate_gsc_verification_file()
    generate_headers()
    create_zip()
    print("Build Complete!")


if __name__ == "__main__":
    build()
