"""Render index.html (the live web CV) from resume.json + stats/stats.json.

The page is complete static HTML (works without JavaScript, readable by recruiters and
search engines). A tiny script then refreshes the live numbers in the visitor's browser
from the latest stats file in the repo.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "resume.json")))
STATS = json.load(open(os.path.join(ROOT, "stats", "stats.json")))
PDF = "Wycliffe_Kipleting_Rotich_Resume_Public.pdf"
REPO = "https://github.com/wycliffRotich-dev/cv"
RAW_STATS = "https://raw.githubusercontent.com/wycliffRotich-dev/cv/main/stats/stats.json"


def live(text):
    """Replace {{stat}} with a span the browser script can refresh."""
    def sub(m):
        k = m.group(1)
        return '<span class="live" data-stat="%s">%s</span>' % (k, STATS.get(k, "?"))
    return re.sub(r"\{\{(\w+)\}\}", sub, text)


def esc(s):
    return html.escape(s, quote=True)


def contact():
    out = []
    for row in DATA["contact_rows"]:
        items = []
        for label, url in row:
            items.append('<a href="%s">%s</a>' % (esc(url), esc(label)) if url else "<span>%s</span>" % esc(label))
        out.append('<div class="contact-row">%s</div>' % '<i>|</i>'.join(items))
    return "\n".join(out)


def metrics():
    cells = []
    for m in DATA["metrics"]:
        cells.append('<div class="metric"><b>%s</b><span>%s</span></div>' % (live(m["value"]), esc(m["label"])))
    return "\n".join(cells)


def skills():
    return "\n".join('<div class="skill"><dt>%s</dt><dd>%s</dd></div>' % (esc(a), esc(b)) for a, b in DATA["skills"])


def jobs():
    out = []
    for j in DATA["experience"]:
        lis = "\n".join("<li>%s</li>" % live(b) for b in j["bullets"])
        out.append(
            '<article class="job"><header><h3>%s</h3><time>%s</time></header>'
            '<p class="org">%s</p><ul>%s</ul></article>' % (esc(j["title"]), esc(j["dates"]), esc(j["org"]), lis))
    return "\n".join(out)


def education():
    out = []
    for e in DATA["education"]:
        logo = ('<img class="logo" src="%s" alt="" onerror="this.remove()">' % esc(e["logo"])) if e.get("logo") else ""
        out.append(
            '<article class="job edu"><header><h3>%s</h3><time>%s</time></header>'
            '<p class="org">%s%s</p></article>' % (esc(e["title"]), esc(e["dates"]), esc(e["school"]), logo))
    return "\n".join(out)


CSS = """
:root{--ink:#0A1020;--amber:#F5A524;--teal:#0E9F8E;--text:#1F2937;--muted:#5B6678;--rule:#D9DEE8;--bg:#EEF1F6;--card:#fff;--soft:#F3F5F9;--indigo:#4F46E5}
@media (prefers-color-scheme:dark){:root{--text:#E5E9F2;--muted:#9AA8BE;--rule:#26314D;--bg:#070B16;--card:#0F1830;--soft:#16223F}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}
.hero{background:var(--ink);color:#fff;border-bottom:4px solid var(--amber)}
.wrap{max-width:900px;margin:0 auto;padding:0 24px}
.hero .wrap{padding-top:44px;padding-bottom:34px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px 32px}.hero .wrap>div{min-width:0}
h1{overflow-wrap:break-word;margin:0;font-size:clamp(28px,5vw,40px);line-height:1.1;font-weight:700;letter-spacing:-.01em}
.headline{color:var(--amber);font-weight:500;margin:8px 0 18px;font-size:clamp(14px,2.2vw,17px)}
.avail{text-align:right;color:#CBD5E1;font-size:13px;font-weight:500;line-height:1.7}
.contact-row{font-size:13.5px;color:#E2E8F0;margin:3px 0;display:flex;flex-wrap:wrap;align-items:center;row-gap:3px}
.contact-row i{color:var(--amber);font-style:normal;margin:0 10px}
.contact-row a{text-decoration:none;border-bottom:1px solid rgba(255,255,255,.25)}
.contact-row a:hover{border-color:var(--amber);color:#fff}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;grid-column:1/-1}
.btn{display:inline-block;background:var(--indigo);color:#fff;text-decoration:none;font-weight:600;font-size:13px;letter-spacing:.04em;text-transform:uppercase;padding:10px 18px;border-radius:6px}
.btn:hover{filter:brightness(1.12)}
main{padding:26px 0 56px}
.card{background:var(--card);border-radius:12px;padding:26px 30px;margin-bottom:18px;box-shadow:0 1px 2px rgba(10,16,32,.06)}
.metrics{display:grid;grid-template-columns:1fr 1fr 1fr 1.6fr;gap:0;background:var(--soft);border-top:3px solid var(--amber);border-radius:10px;margin-bottom:18px;overflow:hidden}
.metric{padding:16px 18px;border-right:1px solid var(--rule)}.metric:last-child{border:0}
.metric b{display:block;font-size:21px;white-space:nowrap;line-height:1.2;color:var(--text)}
.metric>span{display:block;font-size:12px;color:var(--muted);margin-top:4px;line-height:1.35}
.live{font-variant-numeric:tabular-nums}
.livebadge{display:inline-flex;align-items:center;gap:6px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 8px 2px}
.livebadge::before{content:"";width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 0 rgba(34,197,94,.6);animation:pulse 2s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 7px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
h2{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 14px;padding:2px 0 4px 11px;border-left:4px solid var(--amber);border-bottom:1px solid var(--rule)}
.skill{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:7px 0;border-bottom:1px solid var(--rule);font-size:14px}
.skill:last-child{border:0}.skill dt{font-weight:600}.skill dd{margin:0;color:var(--text)}
dl{margin:0}
.job{margin-bottom:22px}.job:last-child{margin-bottom:0}
.job header{display:flex;justify-content:space-between;gap:16px;align-items:baseline;flex-wrap:wrap}
.job h3{margin:0;font-size:16px}
.job time{color:var(--muted);font-weight:500;font-size:13px;white-space:nowrap}
.org{margin:2px 0 8px;color:var(--teal);font-weight:500;font-size:14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.logo{height:26px;width:auto;border-radius:3px;background:#fff;padding:2px}
ul{margin:0;padding-left:20px}li{margin:5px 0;font-size:14.5px}li::marker{color:var(--amber)}
.summary{font-size:15px}
footer{text-align:center;color:var(--muted);font-size:12.5px;padding:0 24px 40px}
footer a{color:var(--muted)}
@media (max-width:720px){.hero .wrap{grid-template-columns:minmax(0,1fr);padding-top:32px}.contact-row i{margin:0 8px}.avail{text-align:left}.metrics{grid-template-columns:repeat(2,1fr)}.metric:nth-child(2){border-right:0}.metric:nth-child(-n+2){border-bottom:1px solid var(--rule)}.card{padding:20px 18px}.skill{grid-template-columns:1fr;gap:2px}}
@media print{body{background:#fff;color:#000}.hero{-webkit-print-color-adjust:exact;print-color-adjust:exact}.actions,.livebadge,footer{display:none}.card{box-shadow:none;border:1px solid #ddd;break-inside:avoid-page}@page{size:A4;margin:12mm}}
"""

SCRIPT = """
(function () {
  var URL = "%s";
  function apply(s) {
    document.querySelectorAll("[data-stat]").forEach(function (el) {
      var v = s[el.getAttribute("data-stat")];
      if (typeof v === "number" && v > 0) el.textContent = v;
    });
  }
  fetch(URL + "?t=" + Math.floor(Date.now() / 60000), { cache: "no-store" })
    .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
    .then(apply)
    .catch(function () { /* keep the numbers baked in at build time */ });
})();
""" % RAW_STATS

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__NAME__ | Platform Engineer</title>
<meta name="description" content="__NAME__, platform engineer in Nairobi. Distributed systems, Python, AWS, Kubernetes. Creator of AetherGrid, an open-source AI workload orchestrator.">
<meta property="og:title" content="__NAME__ | Platform Engineer">
<meta property="og:description" content="Distributed systems, Python, AWS, Kubernetes. Creator of AetherGrid.">
<meta property="og:type" content="profile">
<meta property="og:image" content="https://wycliffrotich-dev.github.io/cv/assets/social-preview.png">
<meta name="theme-color" content="#0A1020">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>__CSS__</style>
</head>
<body>
<header class="hero"><div class="wrap">
  <div>
    <h1>__NAME__</h1>
    <p class="headline">__HEADLINE__</p>
    __CONTACT__
  </div>
  <div class="avail">__AVAIL__</div>
  <div class="actions">
    <a class="btn" href="__PDF__">Download PDF</a>
    <a class="btn" href="https://github.com/wycliffRotich-dev/aethergrid">AetherGrid on GitHub</a>
    <a class="btn" href="https://aethergrid-dashboard.onrender.com/">Live dashboard</a>
  </div>
</div></header>
<main class="wrap">
  <p class="livebadge">Live stats from the AetherGrid repository</p>
  <section class="metrics">__METRICS__</section>
  <section class="card"><h2>Professional summary</h2><p class="summary">__SUMMARY__</p></section>
  <section class="card"><h2>Technical skills</h2><dl>__SKILLS__</dl></section>
  <section class="card"><h2>Professional experience</h2>__JOBS__</section>
  <section class="card"><h2>Education</h2>__EDU__</section>
</main>
<footer>Built from <a href="__REPO__">one source file</a>. The PDF, this page and the stats rebuild automatically on every push.</footer>
<script>__SCRIPT__</script>
</body>
</html>
"""

page = (PAGE.replace("__CSS__", CSS).replace("__SCRIPT__", SCRIPT)
        .replace("__NAME__", esc(DATA["name"])).replace("__HEADLINE__", esc(DATA["headline"]))
        .replace("__CONTACT__", contact())
        .replace("__AVAIL__", "<br>".join(esc(a) for a in DATA["availability"]))
        .replace("__PDF__", PDF).replace("__REPO__", REPO)
        .replace("__METRICS__", metrics()).replace("__SUMMARY__", live(DATA["summary"]))
        .replace("__SKILLS__", skills()).replace("__JOBS__", jobs()).replace("__EDU__", education()))

out = os.path.join(ROOT, "index.html")
open(out, "w", encoding="utf-8").write(page)
print("HTML written:", out, len(page), "bytes")
