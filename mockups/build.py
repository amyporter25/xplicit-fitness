# Assembles mockup pages from ../homepage + src/ pieces.
#   python3 build.py              -> rebuild mockups + share/level-up-ghl.html
#   python3 build.py --homepage   -> also write the teen section into the real ../homepage
import re, sys, base64, pathlib
here = pathlib.Path(__file__).parent
home_path = here.parent / "homepage"
src = lambda n: (here / "src" / n).read_text()
wrap = lambda title, body: f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title></head>\n<body>\n{body}\n</body></html>\n'
inline = lambda n: "data:image/jpeg;base64," + base64.b64encode((here / "img" / f"{n}.jpg").read_bytes()).decode()

teen_css, page_css = src("teen.css"), src("level-up.css")

# Full-width fix that finds whatever GHL section holds this code, so it survives GHL re-assigning IDs
GHL_ANY_SECTION = """
/* GHL FULL-WIDTH FIX that works whatever ID GHL gives the section */
.c-section:has(#xpl),
.c-section:has(#xpl) > .inner,
.c-row:has(#xpl),
.c-row:has(#xpl) > .inner,
.c-column:has(#xpl),
.c-column:has(#xpl) > .inner,
.c-custom-code:has(#xpl),
.custom-code-container:has(#xpl){
  max-width:100% !important;
  width:100% !important;
  margin:0 !important;
  padding:0 !important;
}
"""

# The teen pieces are fenced with markers so the real homepage can be rebuilt without double-inserting
CSS_A, CSS_B = "/* TEEN-SECTION-START */", "/* TEEN-SECTION-END */"
HTML_A, HTML_B = "<!-- TEEN-SECTION-START -->", "<!-- TEEN-SECTION-END -->"
NAV = '\n        <a href="#teens">Teens</a>'

def strip_teens(h):
    for a, b in [(CSS_A, CSS_B), (HTML_A, HTML_B)]:
        if a in h:
            h = h[:h.index(a)] + h[h.index(b) + len(b):].lstrip("\n")
    return h.replace(NAV, "")

def add_teens(h, girl_src, page_link):
    h = h.replace("</style>", CSS_A + GHL_ANY_SECTION + teen_css + CSS_B + "\n</style>", 1)
    marker = "<!-- FAQ (below pricing"
    assert marker in h
    section = src("teen-section.html").replace("img/teen-girl.jpg", girl_src).replace('href="level-up.html"', f'href="{page_link}"')
    h = h.replace(marker, HTML_A + "\n" + section + HTML_B + "\n\n" + marker, 1)
    return h.replace('<a href="#pricing">Pricing</a>', '<a href="#pricing">Pricing</a>' + NAV, 1)

base = strip_teens(home_path.read_text())

# 1) Homepage mockup
(here / "homepage-with-teens.html").write_text(wrap("Xplicit Fitness", add_teens(base, "img/teen-girl.jpg", "level-up.html")))

# 1b) The real homepage (GHL code): image inlined, button goes to the live /teens page
if "--homepage" in sys.argv:
    home_path.write_text(add_teens(base, inline("teen-girl"), "/teens"))

# 2) Level Up page: homepage head + CSS, new body
head = base[:base.index("</style>")].replace("section-E3mBxZh8yN", "section-Ysa8i5UVcF") + GHL_ANY_SECTION + teen_css + page_css + "</style>\n"
logo = re.search(r'class="logo"[^>]*><img src="([^"]+)"', base).group(1)
body = src("level-up-body.html").replace("{{LOGO}}", logo)
(here / "level-up.html").write_text(wrap("Teen Boxing + Strength | Level Up | Xplicit Fitness", head + body))

# 3) GHL-ready Level Up (images inlined, no html/body wrapper) -> share/level-up-ghl.html
ghl = head + body
for n in ["teen-boy", "teen-girl", "teen-coach"]:
    ghl = ghl.replace(f"img/{n}.jpg", inline(n))
ghl = ghl.replace('href="homepage-with-teens.html"', 'href="/"')
ghl = ghl[ghl.index("-->") + 3:].lstrip()  # drop the homepage's header comment (describes the popup)
banner = """<!-- ============================================================
     XPLICIT FITNESS -- LEVEL UP (teen program) page
     SELF-CONTAINED: paste into a GHL Custom Code element in a
     full-width, single-column section with padding set to 0.
     ============================================================ -->
"""
(here / "share").mkdir(exist_ok=True)
(here / "share" / "level-up-ghl.html").write_text(banner + ghl + "\n")
print("built")
