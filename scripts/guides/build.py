"""Build a Roamly guide page from a trip export + its editorial module.

    python3 scripts/guides/build.py tokyo_hakone

Writes guides/<slug>.html (static, crawlable HTML; the map is layered on with
MapKit JS) and resized photos into guides/img/. Itinerary cards follow the
app's BlockTimelineCard spec (Roamly/Views/ItineraryBlockCard.swift).
"""
import html, importlib, json, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(SITE, "guides")
SRC = os.path.expanduser("~/Desktop/roamly-guides-src/photos")
CRED = json.load(open(os.path.join(HERE, "photos.credits.json")))
TOKENS = json.load(open(os.path.join(HERE, "mapkit-tokens.json")))
APP_ID = "6737066181"
E = html.escape

# ItineraryBlockType.color / iconName (Roamly/Models/Itinerary.swift)
TYPE_COLOR = {"place": "#4FC4B0", "food": "#E7A684", "activity": "#7BC67E", "note": "#8B7D75",
              "flight": "#7B8CDE", "housing": "#B07CC6"}
GLYPH = {  # open stand-ins for mappin.circle.fill, fork.knife, figure.walk, note.text, airplane, bed.double.fill
    "place": '<path d="M12 2.5a6.5 6.5 0 0 0-6.5 6.5c0 4.6 6.5 12.5 6.5 12.5s6.5-7.9 6.5-12.5A6.5 6.5 0 0 0 12 2.5zm0 9a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/>',
    "food": '<path d="M7 2v8.5a2 2 0 0 0 1.5 1.94V22h2V12.44A2 2 0 0 0 12 10.5V2h-1.5v6h-1V2h-1v6h-1V2zm9.5 0c-1.7 0-3 2.2-3 5v5h2v10h2V2z"/>',
    "activity": '<path d="M13.5 5.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM9.8 8.9 7 23h2.1l1.8-8 2.1 2v6h2v-7.5l-2.1-2 .6-3A7.3 7.3 0 0 0 19 13v-2a5.1 5.1 0 0 1-4.4-2.5l-1-1.6a2.1 2.1 0 0 0-2.6-.8L6 8.3V13h2V9.6z"/>',
    "note": '<path d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm2 5v2h10V8zm0 4v2h10v-2zm0 4v2h7v-2z"/>',
    "flight": '<path d="M21 15.5v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V8.5l-8 5v2l8-2.5V18l-2 1.5V21l3.5-1 3.5 1v-1.5L13 18v-5z"/>',
    "housing": '<path d="M7 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm12-6h-8v7H3V5H1v15h2v-3h18v3h2v-9a4 4 0 0 0-4-4z"/>',
}
def glyph(kind, cls="g"): return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{GLYPH[kind]}</svg>'

# BlockTimelineCard.formatHour / formatDuration / minRowHeight
def fmt_hour(h):
    hh = int(h); m = int(round((h - hh) * 60)); h12 = 12 if hh % 12 == 0 else hh % 12
    ampm = "AM" if hh < 12 or hh == 24 else "PM"
    return f"{h12} {ampm}" if m == 0 else f"{h12}:{m:02d} {ampm}"
def fmt_dur(d):
    if d < 1: return f"{int(d * 60)}m"
    if d == int(d): return f"{int(d)}h"
    return f"{int(d)}h {int(round((d - int(d)) * 60))}m"
def min_row(d): return min(380, 92 + (max(0.5, d) - 1) * 56)
def money(n): return f"${n:,.0f}"

# ItineraryDay.timelineBlocks / stopNumbers
def timeline_blocks(day): return sorted([b for b in day["blocks"] if b["type"] not in ("flight", "housing")], key=lambda b: b["startHour"])
def stop_numbers(day):
    n = {}
    for i, b in enumerate(timeline_blocks(day)): n.setdefault(b["id"], i + 1)
    return n

# ---------- photos ----------
used = []
def photo_file(key, width, crop=None):
    src = os.path.join(SRC, key + ".jpg")
    out = f"{key}-{width}.jpg"
    dst = os.path.join(OUT, "img", out)
    im = Image.open(src)
    if crop:
        a, anchor = crop; h = int(im.width / a); top = int((im.height - h) * anchor)
        im = im.crop((0, top, im.width, top + h))
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if not os.path.exists(dst): im.convert("RGB").save(dst, quality=82, optimize=True, progressive=True)
    return out, im.width, im.height
def short_artist(raw):
    """Commons 'Artist' fields can hold a photographer's whole usage note; keep just the name."""
    a = re.sub(r"\s+", " ", raw or "").strip()
    a = re.sub(r"^(this )?photo (was )?taken by\s+", "", a, flags=re.I)
    a = re.sub(r"\s+on Flickr\b.*$", "", a, flags=re.I)        # "Joe Mabel on Flickr as Joe Mabel from Seattle, US"
    a = re.sub(r"\s+from\s+[A-Z][^,]*(,.*)?$", "", a)          # "John Menard from Phoenix, USA"
    a = re.split(r"(?<=[a-z])\.\s", a)[0].rstrip(".")           # first sentence only
    if len(a) > 40: a = a[:38].rsplit(" ", 1)[0] + "…"
    return a or "Unknown"

def credit(key):
    c = CRED[key]
    return f"{E(short_artist(c['artist']))} · {E(c['license'])}"
def figure(key, cap, width):
    used.append(key)
    f, w, h = photo_file(key, width)
    return (f'<figure class="ph" style="--ar:{w / h:.4f}"><img src="img/{f}" width="{w}" height="{h}" alt="{E(cap)}" loading="lazy" decoding="async">'
            f'<figcaption>{E(cap)}<span>{credit(key)}</span></figcaption></figure>')
def photos(items):
    if not items: return ""
    if len(items) == 1: return figure(*items[0], 1600)
    return '<div class="ph-row">' + "".join(figure(k, c, 1200) for k, c in items) + "</div>"

# ---------- itinerary (app-faithful) ----------
def card(b, num, last):
    col = TYPE_COLOR[b["type"]]
    cost = b.get("costUSD")
    pills = (f'<span class="cap cost">{"Free" if cost == 0 else money(cost)}</span>' if cost is not None else "") + \
            f'<span class="cap dur">{fmt_dur(b["durationHours"])}</span>'
    badge = f'<span class="badge">{num}</span>' if num else ""
    hero = ""
    if b.get("hero"):
        hero = f'<img class="hero-img" src="img/blocks/{b["hero"]["file"]}" alt="" loading="lazy" decoding="async"><span class="hero-cr">{E(b["hero"].get("attribution") or "")}</span>'
    pin = ' data-pinned="1"' if b.get("mapPlace") else ""
    details = f'<p>{E(b["details"])}</p>' if b.get("details") else ""
    return (f'<li class="row" id="b-{b["id"][:8].lower()}" data-block="{b["id"]}"{pin} style="--c:{col};min-height:{min_row(b["durationHours"]):.0f}px">'
            f'<div class="gut"><span class="t0">{fmt_hour(b["startHour"])}</span><span class="t1">{fmt_hour(b["startHour"] + b["durationHours"])}</span></div>'
            f'<div class="rail{" last" if last else ""}"><span class="disc">{glyph(b["type"])}{badge}</span></div>'
            f'<div class="card"><div class="ttl"><b>{E(b["title"])}</b>{pills}</div>'
            f'{details}{hero}</div></li>')

def hotel_for(trip, day):
    d = (day.get("date") or "")[:10]
    for h in trip["hotels"]:
        if h["checkIn"][:10] <= d < h["checkOut"][:10]: return h["name"]
    return None

def day_section(i, day, ed, trip, last_chip="Fly home"):
    blocks = timeline_blocks(day); nums = stop_numbers(day)
    cost = sum((b.get("costUSD") or 0) for b in day["blocks"])
    hotel = hotel_for(trip, day)
    stay = (f'<span class="chip stay">{glyph("housing")}{E(hotel)}</span>' if hotel else f'<span class="chip muted">{E(last_chip)}</span>')
    edit = f'<a class="ask" href="#make-it-yours"><span aria-hidden="true">✦</span>Ask Roamly: “{E(ed["edit"])}”</a>' if ed.get("edit") else ""
    rows = "".join(card(b, nums.get(b["id"]), k == len(blocks) - 1) for k, b in enumerate(blocks))
    return f'''<section class="day" id="day-{i + 1}" data-day="{i}">
<header class="dh"><div class="dh-row"><h2>Day {i + 1}</h2><span class="pill">Day <b>{money(cost)}</b></span></div>
<p class="dt">{E(ed["title"])}</p><div class="dh-meta"><span class="chip area">{glyph("place")}{E(ed["area"])}</span>{stay}</div></header>
{photos(ed.get("before"))}
<div class="prose">{"".join(f"<p>{p}</p>" for p in ed["prose"])}</div>
<div class="daymap" data-day="{i}" aria-label="Map of day {i + 1}"></div>
<ol class="timeline">{rows}</ol>
{edit}{photos(ed.get("after"))}{f'<div class="tip">{ed["tip"]}</div>' if ed.get("tip") else ""}
</section>'''

def build(name):
    global used
    used = []
    ed = importlib.import_module(name)
    trip = json.load(open(os.path.join(HERE, ed.TRIP)))
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    act = sum((b.get("costUSD") or 0) for d in trip["days"] for b in d["blocks"])
    hot = sum(h["costUSD"] or 0 for h in trip["hotels"]); total = act + hot
    each = total / (trip.get("travelerCount") or 1)
    app = f"https://apps.apple.com/app/id{APP_ID}?ct={ed.CT}"
    # "Open this trip" goes to the published trip's share page, which opens Roamly (or the App Store).
    open_url = trip.get("shareUrl") or (f"https://share.roamly.us/p/{trip['publishedId']}" if trip.get("publishedId") else app)
    days = "".join(day_section(i, d, ed.DAYS[i], trip, getattr(ed, "LAST_DAY_CHIP", "Fly home")) for i, d in enumerate(trip["days"]))
    flights_note = getattr(ed, "FLIGHTS_NOTE", None) or (
        f"Flights are separate: Roamly priced round trips at about {money(trip['flightsUSD'] / (trip.get('travelerCount') or 1))} per person."
        if trip.get("flightsUSD") else "")
    make_title = getattr(ed, "MAKE_TITLE", "Open the trip. Change it by asking.")
    make_body = getattr(ed, "MAKE_BODY", "In Roamly, this guide is a living plan: every stop on a map, a timeline for each day, and a running total. Tell the trip companion what you want different and it rewrites those days and keeps the rest.")
    if getattr(ed, "VIDEO", None):
        screen = (f'<video src="{ed.VIDEO[0]}" poster="{ed.VIDEO[1]}" autoplay muted loop playsinline preload="metadata" '
                  f'aria-label="Screen recording: this trip being generated in Roamly"></video>')
    else:
        screen = '<div class="rec"><b>Screen recording goes here</b>8–10 s loop of this trip in Roamly.</div>'

    strip = "".join(f'<a class="dc" href="#day-{i + 1}" data-day="{i}"><small>DAY</small><span>{i + 1}</span></a>' for i in range(len(trip["days"])))
    glance = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v.format(total=money(total)))}</dd></div>" for k, v in ed.GLANCE)
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a.format(total=money(total), each=money(each)))}</p></details>" for q, a in ed.FAQ)
    hero_f, hw, hh = photo_file(ed.HERO[0], 2400, ed.HERO[2]); used.append(ed.HERO[0])
    hotels = "".join(f"<tr><td>{E(h['name'])}</td><td>{E(h['city'] or '')}</td><td class='n'>{money(h['costUSD'] or 0)}</td></tr>" for h in trip["hotels"])
    seen = list(dict.fromkeys(used))
    credits = "".join(f'<li><a href="{E(CRED[k]["page"])}">{E(CRED[k]["file"])}</a>, {E(short_artist(CRED[k]["artist"]))}, '
                      f'<a href="{E(CRED[k].get("licurl") or CRED[k]["page"])}">{E(CRED[k]["license"])}</a></li>' for k in seen)
    qr = open(os.path.join(HERE, "qr", ed.SLUG + ".svg")).read()
    mapdata = {"days": [{"city": d["city"], "country": d["country"], "latitude": d["latitude"], "longitude": d["longitude"],
                         "blocks": [{k: b.get(k) for k in ("id", "type", "title", "startHour", "mapPlace")} for b in d["blocks"]]}
                        for d in trip["days"]]}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.format(total=money(total), each=money(each))}} for q, a in ed.FAQ]}
    art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": ed.TITLE, "description": ed.DESCRIPTION,
              "image": [f"https://roamly.us/guides/img/{hero_f}"], "dateModified": "2026-10-19",
              "author": {"@type": "Person", "name": "Alex Manning", "url": "https://roamly.us/about.html"},
              "publisher": {"@type": "Organization", "name": "Roamly", "url": "https://roamly.us"}}
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(ed.SEO_TITLE)}</title><meta name="description" content="{E(ed.DESCRIPTION)}">
<link rel="canonical" href="https://roamly.us/guides/{ed.SLUG}">
<meta name="apple-itunes-app" content="app-id={APP_ID}, app-argument={open_url}">
<meta property="og:type" content="article"><meta property="og:title" content="{E(ed.TITLE)}"><meta property="og:description" content="{E(ed.DESCRIPTION)}">
<meta property="og:image" content="https://roamly.us/guides/img/{hero_f}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../assets/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,400;9..144,500;9..144,600;9..144,700&family=Nunito:wght@500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/guide.css">
<script type="application/ld+json">{json.dumps(art_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head><body>
<header class="site"><div class="site-in"><a class="brand" href="../index.html"><img src="../assets/icon.png" alt="" width="34" height="34"><span>Roamly</span></a>
<nav><a href="../index.html">Home</a><a href="#top">Guides</a><a class="get" href="{app}" aria-haspopup="dialog" aria-controls="get-pop">Get the app</a></nav>
<div class="get-pop" id="get-pop" role="dialog" aria-label="Get Roamly on your iPhone" hidden><div class="qr">{qr}</div>
<div><b>Get Roamly on your iPhone</b><span>Point your iPhone camera at the code. It's free, and this trip opens with it.</span></div></div></div></header>
<main id="top">
<div class="head"><div class="crumbs">{" <span>›</span> ".join(E(c) for c in ed.CRUMBS)}</div>
<h1>{E(ed.TITLE)}</h1><p class="dek">{E(ed.DEK)}</p>
<div class="byline"><img src="../assets/alex-capri.jpg" alt="" width="44" height="44"><div><b>Alex Manning</b><span>Founder of Roamly · Updated {ed.UPDATED} · {ed.READ_MIN} min read</span></div></div></div>
<figure class="hero"><img src="img/{hero_f}" width="{hw}" height="{hh}" alt="{E(ed.HERO[1])}" fetchpriority="high"><figcaption>{E(ed.HERO[1])}<span>{credit(ed.HERO[0])}</span></figcaption></figure>
<div class="layout"><article class="main">
<dl class="glance">{glance}</dl>
<div class="prose intro">{"".join(f"<p>{p}</p>" for p in ed.INTRO)}</div>
<aside class="cta"><div class="cta-copy"><div class="eyebrow">This trip is in Roamly</div><h3><a class="trip-link" href="{open_url}">Get this exact itinerary, then change anything</a></h3>
<p>Every stop, time and cost from this guide, on a map you can edit. Swap a dinner, shift the dates, or ask the trip companion to make a day lighter.</p>
<a class="btn" href="{open_url}">Open this trip in Roamly</a><div class="fine">Free on iPhone</div></div>
<div class="handoff" hidden><div class="qr">{qr}</div><div><b>Open it on your iPhone</b><span>Point your camera at the code. The trip opens in Roamly.</span></div></div></aside>
<div class="plan-head"><h2>The plan, day by day</h2><p>The trip exactly as it appears in Roamly. Hover an entry to find it on the map.</p></div>
{days}
<section class="prose" id="cost"><h2>What this week costs</h2>
<p>These are the estimates Roamly attached to each entry when it built the trip. {E(flights_note)}</p>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Where</th><th class="n">Estimate</th></tr></thead><tbody>{hotels}
<tr><td>Food, sights and transport</td><td>Every entry above</td><td class="n">{money(act)}</td></tr>
<tr class="total"><td>On the ground</td><td>{money(each)} per person</td><td class="n">{money(total)}</td></tr></tbody></table></div>
{ed.PRACTICAL}</section>
<section class="make" id="make-it-yours"><div class="make-copy"><div class="eyebrow">Make it yours</div><h2>{E(make_title)}</h2>
<p>{E(make_body)}</p>
<a class="btn" href="{open_url}">Open this trip in Roamly</a>
<div class="handoff" hidden><div class="qr">{qr}</div><div><b>On a computer?</b><span>Scan with your iPhone camera to open the trip.</span></div></div></div>
<div class="phone"><div class="screen">{screen}</div></div></section>
<section class="prose faq"><h2>Questions people ask</h2>{faq}</section>
<details class="credits"><summary>Photo credits</summary><ol>{credits}</ol><p>Entry photos come from the trip in Roamly (Wikimedia Commons). Map © Apple.</p></details>
</article>
<aside class="side" aria-label="Trip map"><div class="sheet">
<div class="sheet-head"><div><b>{E(ed.TRIP_LABEL)}</b><span class="pill">Trip <b>{money(total)}</b></span></div><nav class="strip" aria-label="Jump to day">{strip}</nav></div>
<div class="bigmap" id="bigmap"></div></div></aside>
</div></main>
<footer class="foot"><span>© 2026 Roamly</span><span>Prices are estimates and change. Check opening hours before you go.</span></footer>
<script src="https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js" crossorigin async onload="window.__mk && window.__mk()"></script>
<script src="assets/roamly-map.js"></script>
<script>window.ROAMLY_TRIP={json.dumps(mapdata, ensure_ascii=False)};window.MAPKIT_TOKENS={json.dumps(TOKENS)};</script>
<script src="assets/guide.js"></script>
</body></html>'''
    path = os.path.join(OUT, ed.SLUG + ".html")
    open(path, "w").write(page)
    print(f"{path}  {len(page) // 1024} KB · photos {len(seen)} · em-dashes {page.count(chr(8212))} · total {money(total)}")

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "tokyo_hakone")
