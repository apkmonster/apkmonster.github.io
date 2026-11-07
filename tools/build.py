"""Rebuilds the ApkMonster static pages from the game list below."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://apkmonster.site"
YEAR = 2026

# ── AD CODE ──────────────────────────────────────────────────────────────────
# The site is generated, so ad code goes here, not into the .html files.
#
# 1. Network-wide scripts (PopAds popunder, PropellerAds Multitag / Onclick /
#    Push Notifications) go into HEAD_ADS. It is inserted before </head> on
#    every generated page.
# 2. Banner / In-Page Push code goes into SLOT_ADS under the slot name that
#    matches the ad block on the page (see the list below).
#
# Slot names and where they appear:
#   home-top        index: slim banner under the hero
#   home-mid        index: between the spotlight rail and the catalog
#   home-bottom     index: tall block before the "Made for phones" panel
#   game-buttons    game pages: banner under the Download buttons
#   game-gallery    game pages: slim banner under the screenshots
#   game-text       game pages: tall block after "About this port"
#   about-page      about page: tall block
#   safety-page     safety page: tall block
#   privacy-page    privacy page: banner
#   404-page        404 page: banner
#   sheet-banner    download modal: 320x250
#   sheet-slim      download modal: 320x50
#   sticky-bottom   every page: sticky bar above the bottom nav
#
# Leave a value as "" to keep the current "Ad space" placeholder.
HEAD_ADS = """
<script src="https://quge5.com/88/tag.min.js" data-zone="306683" async data-cfasync="false"></script>
"""

# In-Page Push / banner tag. Loaded once per page, right before app.js.
BODY_ADS = """
<script>(function(s){s.dataset.zone='12213533',s.src='https://nap5k.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>
"""

# Display banner tags. Paste each network tag once here and every mapped slot
# below reuses it. The same tag may be repeated in several blocks on a page,
# but check your network's rules and keep it to 2-3 banners per screen.
BANNER_250 = """
<script>
  atOptions = {
    'key' : 'cc42b9add9c366b716d379fc629b6fe5',
    'format' : 'iframe',
    'height' : 250,
    'width' : 300,
    'params' : {}
  };
</script>
<script src="https://bellnewyork.org/22/cc42b9add9c366b716d379fc629b6fe5"></script>
"""

BANNER_50 = """
<script>
  atOptions = {
    'key' : '2a051a0f40a04a57e892fd2dbd478b1e',
    'format' : 'iframe',
    'height' : 50,
    'width' : 320,
    'params' : {}
  };
</script>
<script src="https://bellnewyork.org/22/2a051a0f40a04a57e892fd2dbd478b1e"></script>
"""
SLOT_ADS = {
    "home-top": BANNER_50,
    "home-mid": BANNER_250,
    "home-bottom": BANNER_250,
    "game-buttons": BANNER_250,
    "game-gallery": BANNER_50,
    "game-text": BANNER_250,
    "about-page": BANNER_250,
    "safety-page": BANNER_250,
    "privacy-page": BANNER_250,
    "404-page": BANNER_250,
    "sheet-banner": "",
    "sheet-slim": "",
    "sticky-bottom": BANNER_50,
}

# To enable a download button, put the third-party URL into android_url / ios_url.
GAMES = [
    dict(slug="cyberpunk", title="Cyberpunk 2077 Mobile", cat="action", cat_label="Action",
         version="v1.0", updated="Nov 4, 2024", icon="cybericon.jpg", poster="cyberposter.jpg",
         blurb="Night City on your phone: gunfights, neon, and a full story campaign.",
         about="A short look at the Cyberpunk 2077 mobile port. The page collects the cover, screenshots, build size, and device requirements.",
         size="2.4 GB installer, about 32.2 GB cache after download",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1802032", ios_url="https://bearmobiles.com/1802032",
         shots=["cyber1.jpg", "cyber2.jpg", "cyber3.jpg", "cyber4.jpg", "cyber5.png"]),
    dict(slug="gta", title="GTA 5 Mobile", cat="action", cat_label="Action",
         version="v1.1", updated="Feb 27, 2024", icon="gta5logo.jpg", poster="postergta.jpg",
         blurb="An open-world Los Santos: three protagonists, cars, and a whole city on a mobile screen.",
         about="The GTA 5 Mobile page: poster, logo, gallery, and build specs.",
         size="1.3 GB installer, about 22 GB cache after download",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1747476", ios_url="https://bearmobiles.com/1747476",
         shots=["gta1.jpg", "gta2.jpg", "gta3.jpg", "gta4.jpg", "gta5.jpg", "gta6.jpg"]),
    dict(slug="beamng", title="BeamNG.drive Mobile", cat="sim", cat_label="Simulation",
         version="v2.0", updated="Dec 20, 2023", icon="bnn.jpg", poster="bn.jpg",
         blurb="Soft-body damage and crashes: real collision physics on your phone.",
         about="BeamNG.drive Mobile page with car screenshots and device requirements.",
         size="1.2 GB installer, about 9.3 GB cache after download",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1745059", ios_url="https://bearmobiles.com/1745059",
         shots=["b1.jpg", "b2.jpg", "b3.jpg", "b4.jpg", "b5.jpg", "bncar.jpg"]),
    dict(slug="tlou", title="The Last of Us Mobile", cat="action", cat_label="Action",
         version="v1.0", updated="Jun 13, 2024", icon="tlouicon.png", poster="tlouposter.jpg",
         blurb="Ellie and Joel's journey, packaged as a mobile port.",
         about="The Last of Us Mobile overview: poster, icon, and a set of screenshots.",
         size="3.2 GB plus about 28 GB cache",
         android="Snapdragon 8 Gen 1 or newer, 6 GB RAM",
         ios="iPhone 13 Pro or newer, iPad with M1 or M2",
         android_url="https://bearmobiles.com/1747479", ios_url="https://bearmobiles.com/1747479",
         shots=["tlou1.png", "tlou2.png", "tlou3.png", "tlou4.png", "TLOU5.png", "TLOU6.png", "TLOU7.png", "tlou8.png"]),
    dict(slug="ps3-emulator", title="PS3 Emulator Mobile", cat="tools", cat_label="Emulator",
         version="v1.0", updated="Jul 1, 2024", icon="ps3emulator.jpg", poster="ps3poster.jpg",
         blurb="A PlayStation 3 emulator for mobile devices.",
         about="Poster and interface screenshots. The app file is not hosted on this site.",
         size="82 MB",
         android="Snapdragon 8 Gen 1 or newer, 6 GB RAM",
         ios="iPhone 13 Pro or newer, iPad with M1 or M2",
         android_url="https://bearmobiles.com/1747480", ios_url="https://bearmobiles.com/1747480",
         shots=["psscreen.jpg", "psscreen2.jpg"]),
    dict(slug="assetto", title="Assetto Corsa Mobile", cat="racing", cat_label="Racing",
         version="v1.3", updated="Nov 24, 2023", icon="corsalog.jpg", poster="A1.jpg",
         blurb="Track racing with a focus on car handling.",
         about="The Assetto Corsa Mobile page: logo, track screenshots, and phone requirements.",
         size="1.2 GB installer, about 14 GB cache after download",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1747483", ios_url="https://bearmobiles.com/1747483",
         shots=["A3.jpg", "A4.jpg", "A8.jpg", "as1.jpg", "as2.jpg"]),
    dict(slug="ets2", title="ETS 2 Mobile", cat="sim", cat_label="Simulation",
         version="v1.0", updated="May 22, 2024", icon="iconets.jpg", poster="ets2.jpg",
         blurb="Long-haul trips across European roads.",
         about="Euro Truck Simulator 2 Mobile page with cab and road screenshots.",
         size="1.4 GB installer, about 10.6 GB cache after download",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1747484", ios_url="https://bearmobiles.com/1747484",
         shots=["ets1.jpg", "ets22.jpg", "ets3.jpg", "ets4.jpg", "ets5.jpg", "ets6.jpg"]),
    dict(slug="nfs-most-wanted", title="NFS Most Wanted 2005 Mobile", cat="racing", cat_label="Racing",
         version="v2.0", updated="Sep 28, 2023", icon="mwlogo.png", poster="mws.jpg",
         blurb="Police chases and the Blacklist in the city of Rockport.",
         about="The mobile port of Need for Speed: Most Wanted 2005, with cover art and screenshots.",
         size="1.87 GB",
         android="Android 7.1 or newer",
         ios="iOS 8 or newer",
         android_url="https://bearmobiles.com/1747487", ios_url="https://bearmobiles.com/1747487",
         shots=["nfs.jpg", "1.jpg", "2.jpg", "3.jpg", "5.jpg"]),
    dict(slug="nfs-underground-2", title="NFS Underground 2 Mobile", cat="racing", cat_label="Racing",
         version="v1.0.2", updated="Nov 7, 2023", icon="u2logo.jpg", poster="unders.jpg",
         blurb="Night street racing and tuning from Underground 2.",
         about="Need for Speed: Underground 2 Mobile: logo, poster, and requirements.",
         size="1.89 GB",
         android="Android 7.1 or newer",
         ios="iOS 8 or newer",
         android_url="https://bearmobiles.com/1747489", ios_url="https://bearmobiles.com/1747489",
         shots=["nfsu2.jpg", "001.jpg", "02.jpg"]),
    dict(slug="snowrunner", title="SnowRunner Mobile", cat="sim", cat_label="Simulation",
         version="v1.0", updated="Feb 24, 2024", icon="snowr.jpg", poster="snow.jpg",
         blurb="Mud, snow, and heavy trucks on rough terrain.",
         about="The SnowRunner Mobile page with route and vehicle screenshots.",
         size="12 GB",
         android="Snapdragon 845 or newer, 6 GB RAM",
         ios="iPhone XS Max or newer, any 2017 iPad or later, or any iPad Pro",
         android_url="https://bearmobiles.com/1747490", ios_url="https://bearmobiles.com/1747490",
         shots=["snow1.jpg", "snow2.jpg", "snow3.jpg", "snow4.jpg", "snow5.jpg"]),
]

# Kept for reference only. Not built into the site.
ARCHIVED_GAMES = [
    dict(slug="nfs-carbon", title="NFS Carbon Mobile", cat="racing", cat_label="Racing",
         version="v1.0", updated="Feb 24, 2024", icon="carico.png", poster="car1.jpg",
         blurb="Night canyons and crew races from Carbon.",
         about="Need for Speed: Carbon Mobile page with cover art, screenshots, and requirements.",
         size="2.2 GB",
         android="Android 7.1 or newer",
         ios="iOS 8 or newer",
         # temp, ios_url="https://bearmobiles.com/1802032",
         shots=["car2.jpg", "car3.jpg", "car4.jpg", "car5.jpg"]),
]


def ad_code(slot, placeholder):
    """Return the ad code configured for a slot, or the fallback markup."""
    code = SLOT_ADS.get(slot, "").strip()
    return code if code else placeholder


def ad(kind="mid", note="Banner", slot=""):
    code = SLOT_ADS.get(slot, "").strip()
    if not code:
        return ""
    height = {"slim": "ad slim", "mid": "ad", "tall": "ad tall"}[kind]
    return f'''<aside class="{height}" aria-label="Advertisement">
  <div class="ad-label"><span>Advertisement</span><span>{escape(note)}</span></div>
  <div class="ad-box" data-ad-slot="{escape(slot)}">{code}</div>
</aside>'''


def media(name):
    """Return the optimized WebP variant when it exists, else the original file."""
    stem = Path(name).stem
    if (ROOT / "assets" / "media" / "opt" / (stem + ".webp")).exists():
        return f"assets/media/opt/{stem}.webp"
    return f"assets/media/{name}"


def head(title, desc, robots=""):
    t = escape(title)
    d = escape(desc)
    robots_meta = f'\n<meta name="robots" content="{escape(robots)}">' if robots else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#07080c">
<title>{t}</title>
<meta name="description" content="{d}">{robots_meta}
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="ApkMonster">
<link rel="icon" href="Logoapkmonster/apkmonster-mark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="Logoapkmonster/apkmonster-mark.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
{HEAD_ADS}
</head>
<body>'''


def header(active):
    def on(name):
        return ' class="on"' if active == name else ""
    return f'''<header class="top"><div class="wrap">
  <a class="brand" href="index.html"><img src="Logoapkmonster/apkmonster-mark.svg" alt=""><div><b>ApkMonster</b><span>mobile ports</span></div></a>
  <nav><a href="index.html"{on("home")}>Home</a><a href="index.html#catalog"{on("games")}>Games</a><a href="about.html"{on("about")}>About</a><a href="safety.html"{on("safety")}>Safety</a></nav>
  <label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input id="q" type="search" placeholder="Search games" aria-label="Search games"></label>
</div></header>'''


def sheet():
    return f'''<div class="sheet" id="sheet">
  <div class="sheet-card">
    <div class="sheet-head"><h2 id="sheet-title">Download</h2><button class="x" type="button" data-close aria-label="Close">×</button></div>
    <p class="sheet-note">You are about to open an external download page. We do not control third-party sites or files. Please read our <a href="safety.html">Safety notice</a> before downloading.</p>
    {ad("mid", "320×250", "sheet-banner")}
    {ad("slim", "320×50", "sheet-slim")}
    <a class="dl android" id="sheet-go" href="#" target="_blank" rel="noopener noreferrer nofollow">Continue to download</a>
    <p class="sheet-missing" id="sheet-missing"></p>
    <button class="dl close" type="button" data-close>Close</button>
  </div>
</div>'''


def footer(active):
    def on(name):
        return ' class="on"' if active == name else ""
    sticky_code = SLOT_ADS.get("sticky-bottom", "").strip()
    sticky = f'''<div class="sticky-ad" aria-label="Advertisement">
  <div class="ad-box" data-ad-slot="sticky-bottom">{sticky_code}</div>
</div>''' if sticky_code else ""
    return f'''{sticky}
<footer class="site"><div class="wrap">
  <a class="brand" href="index.html"><img src="Logoapkmonster/apkmonster-mark.svg" alt=""><div><b>ApkMonster</b><span>mobile ports</span></div></a>
  <div class="links"><a href="index.html">Home</a><a href="index.html#catalog">Games</a><a href="about.html">About</a><a href="safety.html">Safety</a><a href="privacy.html">Privacy</a></div>
  <div>© {YEAR} ApkMonster. Game names and trademarks belong to their respective owners. We are not affiliated with their publishers.</div>
</div></footer>
<nav class="bnav">
  <a href="index.html"{on("home")}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 11l8-7 8 7v8a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1z"/></svg>Home</a>
  <a href="index.html#catalog"{on("games")}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>Games</a>
  <button id="nav-search" type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>Search</button>
  <a href="about.html"{on("about")}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 8h.01"/></svg>Info</a>
</nav>
{BODY_ADS}
<script src="assets/js/app.js" defer></script>
</body></html>'''


def card(g):
    name = escape(g["title"].lower())
    return f'''<a class="app" href="{g["slug"]}.html" data-cat="{g["cat"]}" data-name="{name}">
  <img src="{media(g["icon"])}" alt="" loading="lazy" decoding="async">
  <div><h3>{escape(g["title"])}</h3><div class="sub">{escape(g["version"])} · {escape(g["updated"])}</div>
  <div class="tags"><span class="tag">{escape(g["cat_label"])}</span><span class="tag v">Android</span><span class="tag v">iOS</span></div></div>
  <span class="go" aria-hidden="true">›</span>
</a>'''


def index():
    featured = GAMES[:4]
    feats = "\n".join(
        f'''<a class="feature" href="{g["slug"]}.html"><img class="cover" src="{media(g["poster"])}" alt="" loading="lazy" decoding="async"><div class="meta"><h3>{escape(g["title"])}</h3><p>{escape(g["blurb"])}</p></div></a>'''
        for g in featured
    )
    chips = [("all", "All"), ("action", "Action"), ("racing", "Racing"), ("sim", "Simulation"), ("tools", "Emulator")]
    chip_html = "\n".join(
        f'<button class="chip{" on" if c == "all" else ""}" type="button" data-cat="{c}">{label}</button>'
        for c, label in chips
    )
    html = head("ApkMonster — Mobile Game Ports", "A catalog of mobile ports of PC games, built for phones with clear ad placements.")
    html += header("home")
    html += f'''<main>
<section class="hero"><div class="wrap"><div class="hero-card"><div class="hero-copy">
  <div class="eyebrow">Mobile ports</div>
  <h1>Big games. <em>Pocket-sized.</em></h1>
  <p>A mobile-port catalog made for phones: big tap targets, a cover rail, and dedicated ad space on every screen.</p>
</div></div></div></section>
{ad("slim", "top of page", "home-top")}
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>In the spotlight</h2><a href="#catalog">All games</a></div>
  <div class="rail">{feats}</div>
</div></section>
{ad("mid", "between blocks", "home-mid")}
<section class="sec" id="catalog"><div class="wrap">
  <div class="sec-head"><h2>All games</h2></div>
  <div class="chips">{chip_html}</div>
  <div style="height:0.8rem"></div>
  <div class="grid">{"".join(card(g) for g in GAMES)}</div>
  <div class="empty">Nothing found. Try another name.</div>
</div></section>
{ad("tall", "before the footer", "home-bottom")}
<section class="sec"><div class="wrap"><div class="panel">
  <h2>Made for phones</h2>
  <div class="why">
    <div><b>Bottom navigation</b><span>Home, games, search, and info stay within thumb reach.</span></div>
    <div><b>Cards instead of tiny lists</b><span>Icon, version, and platforms are readable without zooming.</span></div>
    <div><b>Ads in their own blocks</b><span>Banners never cover buttons and are clearly labeled.</span></div>
    <div><b>Swipeable gallery</b><span>Screenshots scroll with a finger, no tiny arrows.</span></div>
  </div>
</div></div></section>
</main>'''
    html += footer("home")
    return html


def game_page(g):
    shots = "\n".join(f'<img src="{media(s)}" alt="" loading="lazy" decoding="async">' for s in g["shots"])
    others = [x for x in GAMES if x["slug"] != g["slug"]][:3]
    html = head(f'{g["title"]} — ApkMonster', g["blurb"])
    html += header("games")
    html += f'''<main class="page-hero"><div class="wrap">
  <a href="index.html#catalog" style="color:#d6ff4a;font-weight:650">← Back to catalog</a>
  <div class="poster" style="margin-top:0.7rem"><img src="{media(g["poster"])}" alt="" decoding="async" fetchpriority="high"></div>
  <div class="title-row">
    <img src="{media(g["icon"])}" alt="" decoding="async" fetchpriority="high">
    <div><h1>{escape(g["title"])}</h1><div class="kicker">{escape(g["version"])} · updated {escape(g["updated"])}</div></div>
  </div>
  <div class="facts">
    <div class="fact"><small>Size</small><b>{escape(g["size"])}</b></div>
    <div class="fact"><small>Catalog price</small><b>Free</b></div>
    <div class="fact"><small>Android</small><b>{escape(g["android"])}</b></div>
    <div class="fact"><small>iOS</small><b>{escape(g["ios"])}</b></div>
  </div>
  <div class="downloads">
    <button class="dl android" type="button" data-dl="Android · {escape(g["title"])}" data-url="{escape(g["android_url"])}"><img src="{media("android.png")}" alt="">Download for Android</button>
    <button class="dl ios" type="button" data-dl="iOS · {escape(g["title"])}" data-url="{escape(g["ios_url"])}"><img src="{media("apple.png")}" alt="">Download for iOS</button>
  </div>
</div>
{ad("mid", "below the buttons", "game-buttons")}
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>Screenshots</h2></div>
  <div class="shots">{shots}</div>
</div></section>
{ad("slim", "below the gallery", "game-gallery")}
<section class="sec"><div class="wrap"><div class="panel prose">
  <h2>About this port</h2>
  <p>{escape(g["about"])}</p>
  <p>{escape(g["blurb"])}</p>
</div></div></section>
{ad("tall", "in the text", "game-text")}
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>More in the catalog</h2></div>
  <div class="grid">{"".join(card(x) for x in others)}</div>
</div></section>
</main>'''
    html += footer("games")
    html += sheet()
    return html


def about():
    html = head("About — ApkMonster", "About ApkMonster — a catalog of mobile game ports.")
    html += header("about")
    html += f'''<main class="sec"><div class="wrap"><div class="panel prose">
  <h1>About ApkMonster</h1>
  <p>ApkMonster is a catalog of mobile game ports for phones: Cyberpunk 2077, GTA 5, BeamNG.drive, The Last of Us, a PS3 emulator, Assetto Corsa, ETS 2, Most Wanted 2005, Underground 2, and SnowRunner.</p>
  <p>Every page is designed for mobile: bottom navigation, large tap areas, swipeable galleries, and separate ad blocks at the top, between sections, within the text, and above the menu.</p>
  <p>ApkMonster is not affiliated with the game publishers or developers. All game names, logos, and trademarks belong to their respective owners. See our <a href="safety.html">Safety notice</a> for details about external links and downloads.</p>
</div></div>
{ad("tall", "about page", "about-page")}
</main>'''
    html += footer("about")
    return html


def safety():
    html = head("Safety — ApkMonster", "Safety notice: external links, third-party downloads, and responsibility.")
    html += header("safety")
    html += f'''<main class="sec"><div class="wrap"><div class="panel prose">
  <h1>Safety and external links</h1>
  <p>ApkMonster is an information catalog. Unless a page explicitly says otherwise, we do not host game files on this site.</p>
  <p>Some buttons and links may take you to third-party websites that host files, ads, or other content. Those sites are not owned or controlled by ApkMonster. We are not responsible for their content, downloads, security, or privacy practices.</p>
  <p>Download and install files only from sources you trust. Scan files with an antivirus before opening them. You use any third-party site or file at your own risk.</p>
  <p>A link to an external site does not mean we endorse that site or its content. Always check the address in your browser before entering personal or payment information.</p>
  <p>If you are a rights holder and believe that content on this site infringes your rights, or if you find a broken or malicious link, please contact the site administrator so it can be reviewed.</p>
</div></div>
{ad("tall", "safety page", "safety-page")}
</main>'''
    html += footer("safety")
    return html


def privacy():
    html = head("Privacy — ApkMonster", "How ApkMonster handles data and advertising.")
    html += header("about")
    html += f'''<main class="sec"><div class="wrap"><div class="panel prose">
  <h1>Privacy</h1>
  <p>This site is static. It does not create accounts and does not collect personal data. Search and filters run in your browser and are not sent anywhere.</p>
  <p>Ad blocks are currently empty. If an advertising network's code is added, that network may set its own cookies. When that happens, this page should list the network and link to its privacy policy.</p>
  <p>We do not sell or share personal data. For details about links to other sites, see our <a href="safety.html">Safety notice</a>.</p>
</div></div>
{ad("mid", "privacy page", "privacy-page")}
</main>'''
    html += footer("about")
    return html


def not_found():
    html = head("Page not found — ApkMonster", "The page you are looking for does not exist.", robots="noindex, nofollow")
    html += header("home")
    html += f'''<main class="sec"><div class="wrap"><div class="panel prose">
  <h1>Page not found</h1>
  <p>The page you are looking for does not exist or has been moved.</p>
  <p><a href="index.html">Back to the catalog</a></p>
</div></div>
{ad("mid", "404 page", "404-page")}
</main>'''
    html += footer("home")
    return html


def sitemap_xml():
    pages = [
        ("index.html", "1.0"),
        ("about.html", "0.5"),
        ("safety.html", "0.4"),
        ("privacy.html", "0.3"),
    ] + [(g["slug"] + ".html", "0.8") for g in GAMES]
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for name, priority in pages:
        loc = SITE_URL + "/" + ("" if name == "index.html" else name)
        out.append(f"  <url><loc>{escape(loc)}</loc><priority>{priority}</priority></url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def robots_txt():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def manifest_json():
    data = {
        "name": "ApkMonster — Mobile Game Ports",
        "short_name": "ApkMonster",
        "description": "A catalog of mobile ports of PC games, built for phones.",
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "background_color": "#07080c",
        "theme_color": "#07080c",
        "icons": [
            {
                "src": "Logoapkmonster/apkmonster-icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": "Logoapkmonster/apkmonster-icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main():
    (ROOT / "index.html").write_text(index(), encoding="utf-8")
    (ROOT / "about.html").write_text(about(), encoding="utf-8")
    (ROOT / "safety.html").write_text(safety(), encoding="utf-8")
    (ROOT / "privacy.html").write_text(privacy(), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap_xml(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    (ROOT / "manifest.webmanifest").write_text(manifest_json(), encoding="utf-8")
    keep = {"index.html", "about.html", "safety.html", "privacy.html", "404.html"}
    for g in GAMES:
        name = g["slug"] + ".html"
        (ROOT / name).write_text(game_page(g), encoding="utf-8")
        keep.add(name)
    for old in ROOT.glob("*.html"):
        if old.name not in keep:
            old.unlink()
            print("removed", old.name)
    print("pages", len(keep))


if __name__ == "__main__":
    main()
