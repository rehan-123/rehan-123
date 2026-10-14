"""Builds the SVG visuals for the GitHub profile README.

Usage: python3 build.py <fonts-dir>
<fonts-dir> holds fontsource woff2 files for IBM Plex Sans and Cascadia Code.
Edit the data blocks below and re-run to update numbers or projects.
"""

import base64
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

FONTS = Path(sys.argv[1])
OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

FILES = {
    ("plex", 400): "ibm-plex-sans-latin-400-normal.woff2",
    ("plex", 500): "ibm-plex-sans-latin-500-normal.woff2",
    ("plex", 600): "ibm-plex-sans-latin-600-normal.woff2",
    ("plex", 700): "ibm-plex-sans-latin-700-normal.woff2",
    ("mono", 400): "cascadia-code-latin-400-normal.woff2",
    ("mono", 700): "cascadia-code-latin-700-normal.woff2",
}
_fonts = {k: TTFont(FONTS / v) for k, v in FILES.items()}

# ---- palette ---------------------------------------------------------------
NIGHT = "#0B1730"
NIGHT2 = "#0F2245"
PANEL = "#0B1A35"
LINE = "#23406F"
ICE = "#EAF1FB"
SOFT = "#CFDBEE"
MIST = "#A9BBD8"
CYAN = "#38C8F0"
GREEN = "#3FD07A"
AMBER = "#F5C451"
CHIP = "#13284D"
CHIPLINE = "#2A4C80"

ICONS = {
    "shield": '<path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .6-7.96A6 6 0 0 0 6.2 9.2 4.5 4.5 0 0 0 7 18z"/>',
    "server": '<rect x="4" y="4" width="16" height="6" rx="1.5"/><rect x="4" y="14" width="16" height="6" rx="1.5"/><path d="M8 7h.01M8 17h.01M12 7h4M12 17h4"/>',
    "database": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3.5 17.5l3 3 5.8-5.8a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "network": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M10.7 7.2l-4.4 9.6M13.3 7.2l4.4 9.6M7.5 19h9"/>',
    "candles": '<path d="M6 3.5v4M6 15v5.5M12 2.5v3M12 13v4.5M18 6v4.5M18 17v3.5"/><rect x="4.3" y="7.5" width="3.4" height="7.5" rx="0.6"/><rect x="10.3" y="5.5" width="3.4" height="7.5" rx="0.6"/><rect x="16.3" y="10.5" width="3.4" height="6.5" rx="0.6"/>',
    "cube": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    "bolt": '<path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z"/><path d="M13 7.5l-3.5 5h3l-1 4 3.5-5h-3z"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "pin": '<path d="M12 21s-6-5.6-6-11a6 6 0 0 1 12 0c0 5.4-6 11-6 11z"/><circle cx="12" cy="10" r="2"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5l5 5"/>',
    "pulse": '<path d="M2.5 12.5h4.5l2.2-5.5 4.6 11 2.4-5.5h5.3"/>',
    "tag": '<path d="M3.5 12.6V4.5a1 1 0 0 1 1-1h8.1l8 8-9 9z"/><circle cx="8.2" cy="8.2" r="1.5"/>',
    "report": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h7M9 16h5"/>',
    "pause": '<circle cx="12" cy="12" r="9"/><path d="M10 9v6M14 9v6"/>',
    "apple": '<path d="M15.5 3.5c-1.2.1-2.6.9-3.2 2-.5.9-.7 1.9-.6 2.8 1.3.1 2.6-.7 3.3-1.8.5-.9.7-2 .5-3z"/><path d="M12 8.8c-1-.6-2.4-1-3.6-.8C6.2 8.4 4.8 10.5 5 13.4c.2 3.3 2.3 7 4.4 7.1.9 0 1.6-.5 2.6-.5s1.7.5 2.6.5c2.1-.1 4-3.6 4.4-6-1.9-.8-2.9-2.6-2.6-4.6.2-1 .8-1.9 1.6-2.4-1.7-1.5-4.1-1.3-6 .3z"/>',
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def measure(text, fam="plex", w=400, size=16):
    f = _fonts[(fam, w)]
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    total = 0
    for ch in text:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g else upm * 0.5
    return total / upm * size


def wrap(text, width, fam="plex", w=400, size=16):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if measure(trial, fam, w, size) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.body, self.css, self.defs = [], [], []
        self.used = {}

    def text(self, x, y, s, fam="plex", w=400, size=16, fill=ICE, anchor="start", extra="", cls=""):
        self.used.setdefault((fam, w), set()).update(s)
        family = ("P" if fam == "plex" else "M") + (f" {cls}" if cls else "")
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        self.body.append(
            f'<text x="{x:.1f}" y="{y:.1f}" class="{family}" font-weight="{w}" '
            f'font-size="{size}" fill="{fill}"{a} {extra}>{esc(s)}</text>'
        )

    def icon(self, name, x, y, size=24, stroke="#fff", sw=1.8):
        k = size / 24
        self.body.append(
            f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'
        )

    def raw(self, s):
        self.body.append(s)

    def fontcss(self):
        out = []
        for (fam, w), chars in sorted(self.used.items()):
            f = TTFont(FONTS / FILES[(fam, w)])
            o = subset.Options()
            o.flavor = "woff2"
            o.layout_features = ["kern"]
            o.hinting = False
            sub = subset.Subsetter(o)
            sub.populate(text="".join(sorted(chars | {" "})))
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = "woff2"
            f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            name = "PlexSub" if fam == "plex" else "CascadiaSub"
            out.append(
                f"@font-face{{font-family:'{name}';font-weight:{w};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
            )
        return "".join(out)

    def save(self, name):
        css = (
            self.fontcss()
            + ".P{font-family:'PlexSub','IBM Plex Sans','Segoe UI',system-ui,-apple-system,sans-serif}"
            + ".M{font-family:'CascadiaSub','Cascadia Code',Consolas,'SFMono-Regular',Menlo,monospace;"
            "white-space:pre}"
            + "".join(self.css)
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.title)}">'
            f"<title>{esc(self.title)}</title><style>{css}</style>"
            f"<defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>"
        )
        (OUT / name).write_text(svg)
        return OUT / name


def card_bg(s, x, y, w, h, r=16, gid="cardg"):
    if not any(gid in d for d in s.defs):
        s.defs.append(
            f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{NIGHT2}"/><stop offset="1" stop-color="{NIGHT}"/></linearGradient>'
        )
    s.raw(
        f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" rx="{r}" '
        f'fill="url(#{gid})" stroke="{LINE}"/>'
    )


# =============================================================================
# 1. BANNER
# =============================================================================
def banner():
    W, H = 1000, 300
    s = Svg(W, H, "Rehan Khan, Advanced System Administrator, New Delhi, India.")
    s.defs.append(
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A1630"/>'
        f'<stop offset="1" stop-color="#0F2650"/></linearGradient>'
        f'<radialGradient id="glow" cx="0.18" cy="0.2" r="0.6"><stop offset="0" stop-color="{CYAN}" '
        f'stop-opacity="0.22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
        f'<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<path d="M28 0H0V28" fill="none" stroke="#FFFFFF" stroke-opacity="0.05"/></pattern>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
    )
    s.raw('<g clip-path="url(#frame)">')
    s.raw(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    s.raw(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    s.raw(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    s.raw("</g>")
    s.raw(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>')

    X = 48
    s.text(X, 74, "PS C:\\>", "mono", 400, 15, AMBER)
    s.text(X + measure("PS C:\\> ", "mono", 400, 15), 74, "whoami", "mono", 400, 15, MIST)
    s.text(X - 2, 134, "Rehan Khan", "plex", 700, 56, ICE)
    s.text(X, 172, "Advanced System Administrator", "plex", 500, 22, SOFT)

    # --- rotating typing strip ---
    sx, sy, sw, sh = X, 196, 500, 44
    s.raw(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="#081227" stroke="{LINE}"/>')
    FS = 16
    cw = 1200 / 2048 * FS
    s.text(sx + 18, sy + 28, ">", "mono", 700, FS, GREEN)
    tx = sx + 18 + 2 * cw
    lines = [
        "automating Windows infra with PowerShell",
        "AD · Entra ID · Microsoft 365 · Backup & DR",
        "L2/L3 escalations for US-based clients",
        "building AI-assisted NOC tooling",
    ]
    cycle, slot = 16.0, 25.0
    css = s.css
    css.append(
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        "@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}"
        "@keyframes ring{0%{r:4;opacity:.7}100%{r:11;opacity:0}}"
        ".cov,.cur{opacity:0}"
        "@media (prefers-reduced-motion:reduce){.tl1,.tl2,.tl3{display:none}"
        f".cur0{{opacity:1;transform:translateX({len(lines[0])*cw:.2f}px)}}}}"
    )
    s.defs.append(
        f'<clipPath id="typearea"><rect x="{tx-1:.1f}" y="{sy+4}" width="{sx+sw-tx-10:.1f}" height="{sh-8}"/></clipPath>'
    )
    for k, line in enumerate(lines):
        s.text(tx, sy + 28, line, "mono", 400, FS, ICE, cls=f"tl{k}")
        n = len(line)
        w = n * cw
        a = k * slot
        t_end = a + 8.0
        hold = a + 20.0
        e_end = a + 23.0
        kf = (
            f"@keyframes c{k}{{0%{{transform:translateX(0)}}"
            f"{a:.2f}%{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{t_end:.2f}%{{transform:translateX({w:.2f}px);animation-timing-function:linear}}"
            f"{hold:.2f}%{{transform:translateX({w:.2f}px);animation-timing-function:steps({n},end)}}"
            f"{e_end:.2f}%{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}"
        )
        vis = (
            f"@keyframes v{k}{{0%{{opacity:0}}{a:.2f}%{{opacity:0}}{a+0.01:.2f}%{{opacity:1}}"
            f"{e_end+1.5:.2f}%{{opacity:1}}{e_end+1.51:.2f}%{{opacity:0}}100%{{opacity:0}}}}"
        )
        css.append(kf + vis)
        css.append(
            "@media (prefers-reduced-motion:no-preference){"
            f".tl{k}{{animation:v{k} {cycle}s infinite}}"
            f".cov{k}{{opacity:1;animation:c{k} {cycle}s infinite,v{k} {cycle}s infinite}}"
            f".cur{k}{{animation:c{k} {cycle}s infinite,v{k} {cycle}s infinite}}}}"
        )
        s.raw(
            f'<g clip-path="url(#typearea)"><rect class="cov cov{k}" x="{tx:.1f}" y="{sy+6}" '
            f'width="{w:.2f}" height="{sh-12}" fill="#081227"/></g>'
        )
    s.raw('<g style="animation:blink 1.05s infinite">')
    for k in range(len(lines)):
        s.raw(
            f'<rect class="cur cur{k}" x="{tx:.1f}" y="{sy+12}" width="{cw*0.62:.1f}" height="20" '
            f'rx="1.5" fill="{CYAN}"/>'
        )
    s.raw("</g>")

    s.icon("pin", X - 3, 252, 20, MIST, 1.8)
    s.text(X + 22, 268, "New Delhi, India  ·  ~6 years in MSP and enterprise IT", "plex", 400, 16, MIST)

    # --- fleet status panel ---
    px, py, pw, ph = 592, 36, 364, 228
    s.raw(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="{PANEL}" '
          f'fill-opacity="0.92" stroke="{LINE}"/>')
    s.text(px + 20, py + 32, "Fleet status", "plex", 600, 15, ICE)
    lx = px + pw - 20
    s.text(lx, py + 32, "live", "plex", 500, 13, GREEN, anchor="end")
    dot_x = lx - measure("live", "plex", 500, 13) - 10
    s.raw(f'<circle cx="{dot_x:.1f}" cy="{py+27.5}" r="4" fill="{GREEN}"/>')
    s.raw(f'<circle cx="{dot_x:.1f}" cy="{py+27.5}" r="4" fill="none" stroke="{GREEN}" '
          f'style="animation:ring 2s ease-out infinite"/>')
    s.raw(f'<line x1="{px+16}" y1="{py+48}" x2="{px+pw-16}" y2="{py+48}" stroke="{LINE}"/>')
    rows = [
        ("AD / Entra ID", "Hybrid identity", None),
        ("Microsoft 365", "200+ tenants", None),
        ("FastPatch", "600+ endpoints · 99%", 11),
        ("Backup & DR", "Veeam · Spanning · Acronis", None),
    ]
    TICKS, TW, TG = 14, 5, 3
    bx = px + pw - 20 - (TICKS * (TW + TG) - TG)
    for i, (lab, val, warn) in enumerate(rows):
        ry = py + 76 + i * 40
        s.raw(f'<circle cx="{px+24}" cy="{ry-5}" r="4" fill="{GREEN}" '
              f'style="animation:pulse 2.4s ease-in-out {i*0.6:.1f}s infinite"/>')
        s.text(px + 38, ry, lab, "plex", 500, 15.5, ICE)
        s.text(px + 38, ry + 19, val, "plex", 400, 13.5, MIST)
        for t in range(TICKS):
            col = AMBER if warn == t else GREEN
            op = 1 if warn == t else 0.85
            s.raw(f'<rect x="{bx + t*(TW+TG)}" y="{ry-12}" width="{TW}" height="22" rx="1.5" '
                  f'fill="{col}" fill-opacity="{op}"/>')
    s.save("banner.svg")


# =============================================================================
# 2. PROJECT CARDS
# =============================================================================
CARDS = [
    dict(file="proj-meridian.svg", name="meridian", pill="Public",
         pillc=GREEN, icon="compass", g=("#A78BFA", "#4F6BFF"),
         desc="Decision-first paper-trading terminal for Indian equities: specialist agents, "
              "a chief decision agent, risk engine and approval-gated execution.",
         langs=[("Python", "#3572A5"), ("TypeScript", "#3178C6")], stat="1,320 tests passing",
         link=True),
    dict(file="proj-ecom-autopilot.svg", name="ecom-autopilot", pill="Public",
         pillc=GREEN, icon="cube", g=("#F5C451", "#F07B3F"),
         desc="Decision engine and operating layer for selling on Indian marketplaces, from "
              "landed-cost economics and compliance to listings, orders and measured profit.",
         langs=[("Python", "#3572A5"), ("React", "#61DAFB")], stat="1,029 tests passing",
         link=True),
    dict(file="proj-technical-analysis-agent.svg", name="technical-analysis-agent", pill="Public",
         pillc=GREEN, icon="candles", g=("#38C8F0", "#2F6BFF"),
         desc="Technical-analysis specialist for a multi-agent investment platform: ~24 "
              "indicators, market-structure engines and risk-managed entries.",
         langs=[("Python", "#3572A5")], stat="240 tests passing", link=True),
    dict(file="proj-fastpatch.svg", name="FastPatch", pill="Live in production",
         pillc=GREEN, icon="bolt", g=("#3FD07A", "#119E8E"),
         desc="Self-healing patch remediation for Kaseya VSA fleets: finds failed Windows "
              "updates, names the cause, applies the approved fix and proves it landed.",
         langs=[("PowerShell", "#5391FE")], stat="600+ machines · 99% success",
         link=True),
]


def card(c):
    W, H = 480, 252
    s = Svg(W, H, f"{c['name']}: {c['desc']} {c['stat']}.")
    card_bg(s, 0, 0, W, H)
    gid = "eg"
    s.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
                  f'<stop offset="0" stop-color="{c["g"][0]}"/><stop offset="1" stop-color="{c["g"][1]}"/>'
                  f"</linearGradient>")
    s.raw(f'<rect x="28" y="28" width="60" height="60" rx="15" fill="url(#{gid})"/>')
    s.icon(c["icon"], 40, 40, 36, "#FFFFFF", 1.7)
    s.text(106, 54, c["name"], "plex", 600, 24, ICE)
    pw = measure(c["pill"], "plex", 500, 12.5) + 22
    s.raw(f'<rect x="106.5" y="66.5" width="{pw:.1f}" height="23" rx="11.5" fill="none" '
          f'stroke="{c["pillc"]}" stroke-opacity="0.7"/>')
    s.text(106 + 11, 82.5, c["pill"], "plex", 500, 12.5, c["pillc"])
    if c.get("link"):
        vx = 106 + pw + 8
        lab = c.get("link_label", "View on GitHub")
        vw = measure(lab, "plex", 500, 12.5) + 22
        s.raw(f'<rect x="{vx+0.5:.1f}" y="66.5" width="{vw:.1f}" height="23" rx="11.5" '
              f'fill="{CYAN}" fill-opacity="0.14" stroke="{CYAN}" stroke-opacity="0.7"/>')
        s.text(vx + 11, 82.5, lab, "plex", 500, 12.5, CYAN)
    dl = wrap(c["desc"], W - 56, "plex", 400, 16)
    assert len(dl) <= 3, (c["name"], dl)
    for i, ln in enumerate(dl):
        s.text(28, 128 + i * 24, ln, "plex", 400, 16, "#B9C8DF")
    s.raw(f'<line x1="28" y1="{H-58}" x2="{W-28}" y2="{H-58}" stroke="{LINE}"/>')
    fy = H - 26
    x = 28
    for lang, col in c["langs"]:
        s.raw(f'<circle cx="{x+6}" cy="{fy-5}" r="6" fill="{col}"/>')
        s.text(x + 18, fy, lang, "plex", 500, 14, SOFT)
        x += 18 + measure(lang, "plex", 500, 14) + 18
    stat_w = measure(c["stat"], "plex", 500, 14)
    if c.get("stat_plain"):
        s.text(W - 28, fy, c["stat"], "plex", 500, 14, MIST, anchor="end")
    else:
        s.text(W - 28, fy, c["stat"], "plex", 500, 14, GREEN, anchor="end")
        s.icon("check", W - 28 - stat_w - 22, fy - 15, 18, GREEN, 2.4)
    s.save(c["file"])


# =============================================================================
# 3. INFRASTRUCTURE STACK GRID
# =============================================================================
STACK = [
    ("Identity & access", "shield", ["Active Directory", "Entra ID", "Group Policy", "ADCS / PKI",
                                      "Kerberos / NTLM", "DNS / DHCP"]),
    ("Backup & DR", "database", ["Veeam", "Spanning", "Acronis", "Unitrends", "ShadowProtect SPX",
                                 "Datto", "AWS Backup"]),
    ("Microsoft 365", "cloud", ["Exchange Online", "SharePoint", "Intune", "Graph API"]),
    ("MSP & endpoints", "wrench", ["Kaseya VSA", "ConnectWise Automate", "ScreenConnect", "IT Glue",
                                   "Jamf Pro"]),
    ("Virtualization", "server", ["VMware", "Hyper-V clusters", "RDS", "FSLogix"]),
    ("Network & security", "network", ["FortiGate", "SonicWall"]),
]


def stack():
    W, GAP, CWID = 1000, 20, 490
    CH, CPAD, CFS = 32, 14, 15
    inner = CWID - 48

    def layout(chips):
        rows, cur, cw = [], [], 0
        for ch in chips:
            w = measure(ch, "plex", 500, CFS) + 2 * CPAD
            if cur and cw + 10 + w > inner:
                rows.append(cur)
                cur, cw = [], 0
            cur.append((ch, w))
            cw += (10 if cw else 0) + w
        rows.append(cur)
        return rows

    lays = [layout(c) for _, _, c in STACK]
    heights = []
    for r in range(0, len(STACK), 2):
        n = max(len(lays[r]), len(lays[r + 1]))
        heights.append(84 + n * (CH + 10) + 12)
    H = sum(heights) + GAP * (len(heights) - 1)
    s = Svg(W, H, "Infrastructure stack. " + " ".join(
        f"{t}: {', '.join(c)}." for t, _, c in STACK))
    y = 0
    for r, h in enumerate(heights):
        for col in range(2):
            i = r * 2 + col
            title, icon, _ = STACK[i]
            x = col * (CWID + GAP)
            card_bg(s, x, y, CWID, h, 14)
            s.raw(f'<rect x="{x+24}" y="{y+22}" width="40" height="40" rx="10" fill="{CHIP}" stroke="{CHIPLINE}"/>')
            s.icon(icon, x + 32, y + 30, 24, CYAN, 1.8)
            s.text(x + 80, y + 48, title, "plex", 600, 19, ICE)
            cy = y + 80
            for row in lays[i]:
                cx = x + 24
                for ch, w in row:
                    s.raw(f'<rect x="{cx+0.5:.1f}" y="{cy+0.5}" width="{w-1:.1f}" height="{CH-1}" '
                          f'rx="{CH/2}" fill="{CHIP}" stroke="{CHIPLINE}"/>')
                    s.text(cx + CPAD, cy + 21, ch, "plex", 500, CFS, SOFT)
                    cx += w + 10
                cy += CH + 10
        y += h + GAP
    s.save("stack-grid.svg")


# =============================================================================
# 4. CERTIFICATIONS
# =============================================================================
CERTS = [
    ("AZ-800", "Windows Server Hybrid Core Infrastructure", "Microsoft"),
    ("AZ-801", "Windows Server Hybrid Advanced Services", "Microsoft"),
    ("MD-102", "Endpoint Administrator", "Microsoft"),
    ("VMCE", "Veeam Certified Engineer", "Veeam"),
    ("CWA", "Automate Certified Professional", "ConnectWise"),
    ("JCA", "Jamf Certified Associate", "Jamf"),
]


def certs():
    W, COLS, GAP, BH = 1000, 3, 20, 104
    BW = (W - GAP * (COLS - 1)) / COLS
    rows = (len(CERTS) + COLS - 1) // COLS
    H = rows * BH + (rows - 1) * GAP
    s = Svg(W, H, "Certifications: " + "; ".join(f"{c} {n} ({o})" for c, n, o in CERTS) + ".")
    s.defs.append(f'<linearGradient id="hx" x1="0" y1="0" x2="1" y2="1">'
                  f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{GREEN}"/></linearGradient>')
    for i, (code, name, org) in enumerate(CERTS):
        x = (i % COLS) * (BW + GAP)
        y = (i // COLS) * (BH + GAP)
        card_bg(s, x, y, BW, BH, 14)
        cx, cy, r = x + 58, y + BH / 2, 38
        pts = " ".join(
            f"{cx + r*__import__('math').cos(__import__('math').radians(a)):.1f},"
            f"{cy + r*__import__('math').sin(__import__('math').radians(a)):.1f}"
            for a in range(-90, 270, 60)
        )
        s.raw(f'<polygon points="{pts}" fill="{CHIP}" stroke="url(#hx)" stroke-width="2.5"/>')
        fs = 14 if len(code) > 4 else 17
        s.text(cx, cy + fs * 0.36, code, "mono", 700, fs, ICE, anchor="middle")
        tx = x + 112
        lines = wrap(name, BW - 112 - 18, "plex", 600, 15.5)
        base = cy - (len(lines) * 20 + 18) / 2 + 15
        for k, ln in enumerate(lines):
            s.text(tx, base + k * 20, ln, "plex", 600, 15.5, ICE)
        s.text(tx, base + len(lines) * 20 + 4, org, "plex", 400, 13.5, MIST)
    s.save("cert-badges.svg")


# =============================================================================
# 5. REPO HEADER BANNERS
# =============================================================================
REPOS = [
    dict(out="repo-meridian.svg", name="meridian", icon="compass", g=("#A78BFA", "#4F6BFF"),
         tag=["Decision-first paper-trading terminal", "for Indian equities (NSE)"],
         chips=["FastAPI", "React", "TypeScript", "pandas", "Pydantic"],
         stat="1,293 backend + 27 frontend tests passing",
         flow_title="How a trade happens",
         flow=[["Technical", "News", "Strategy", "Scanner", "Risk"],
               ["Chief Decision Agent"], ["Your approval"], ["Paper broker + journal"]]),
    dict(out="repo-ecom-autopilot.svg", name="ecom-autopilot", icon="cube", g=("#F5C451", "#F07B3F"),
         tag=["Decision engine and operating layer", "for Indian marketplace selling"],
         chips=["Python", "FastAPI", "React", "Vite", "Event sourcing"],
         stat="1,029 tests passing · ruff clean",
         flow_title="From idea to measured profit",
         flow=[["Landed cost", "3-scenario economics", "Compliance"], ["Human approval"],
               ["Listings", "Inventory", "Orders"], ["Settlement → profit feedback"]]),
    dict(out="repo-technical-analysis-agent.svg", name="technical-analysis-agent", icon="candles",
         g=("#38C8F0", "#2F6BFF"),
         tag=["Technical-analysis specialist agent", "for stocks and crypto"],
         chips=["Python", "FastAPI", "Pydantic", "pandas", "Ollama"],
         stat="240 tests passing · fully offline",
         flow_title="Analysis pipeline",
         flow=[["OHLCV data", "Validation"], ["~24 indicators", "Market structure", "Volume"],
               ["Confluence + confidence"], ["Entry · stop · targets"]]),
]


def repo_banner(r):
    import math
    W, H = 1280, 400
    s = Svg(W, H, f"{r['name']}: {' '.join(r['tag'])}. {r['stat']}.")
    s.defs.append(
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A1630"/>'
        '<stop offset="1" stop-color="#0F2650"/></linearGradient>'
        f'<radialGradient id="glow" cx="0.12" cy="0.15" r="0.55"><stop offset="0" stop-color="{r["g"][0]}" '
        f'stop-opacity="0.22"/><stop offset="1" stop-color="{r["g"][0]}" stop-opacity="0"/></radialGradient>'
        '<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
        '<path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity="0.05"/></pattern>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
        f'<linearGradient id="eg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{r["g"][0]}"/>'
        f'<stop offset="1" stop-color="{r["g"][1]}"/></linearGradient>'
    )
    s.raw('<g clip-path="url(#frame)">')
    for f in ("bg", "grid", "glow"):
        s.raw(f'<rect width="{W}" height="{H}" fill="url(#{f})"/>')
    s.raw("</g>")
    s.raw(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{LINE}"/>')

    X = 64
    s.raw(f'<rect x="{X}" y="60" width="76" height="76" rx="19" fill="url(#eg)"/>')
    s.icon(r["icon"], X + 15, 75, 46, "#FFFFFF", 1.6)
    name_fs = 50 if len(r["name"]) < 16 else 40
    s.text(X + 98, 112, r["name"], "plex", 700, name_fs, ICE)
    for i, ln in enumerate(r["tag"]):
        s.text(X, 196 + i * 34, ln, "plex", 400, 26, SOFT)
    cx = X
    cy = 268
    for ch in r["chips"]:
        w = measure(ch, "plex", 500, 15) + 28
        s.raw(f'<rect x="{cx+0.5:.1f}" y="{cy+0.5}" width="{w-1:.1f}" height="33" rx="16.5" '
              f'fill="{CHIP}" stroke="{CHIPLINE}"/>')
        s.text(cx + 14, cy + 22, ch, "plex", 500, 15, SOFT)
        cx += w + 10
    s.icon("check", X - 2, 322, 22, GREEN, 2.4)
    s.text(X + 28, 340, r["stat"], "plex", 500, 17, GREEN)

    # flow panel
    px, py, pw, ph = 696, 40, 540, 320
    s.raw(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" fill="{PANEL}" '
          f'fill-opacity="0.92" stroke="{LINE}"/>')
    s.text(px + 24, py + 38, r["flow_title"], "plex", 600, 18, ICE)
    rows = r["flow"]
    top, bottom = py + 58, py + ph - 14
    step = (bottom - top) / len(rows)
    CH = 40
    centers = []
    for i, row in enumerate(rows):
        ry = top + i * step + (step - CH) / 2
        widths = [measure(c, "plex", 500, 16) + 28 for c in row]
        assert sum(widths) + 8 * (len(row) - 1) <= pw - 32, row
        total = sum(widths) + 8 * (len(row) - 1)
        rx = px + (pw - total) / 2
        last = i == len(rows) - 1
        for c, w in zip(row, widths):
            stroke = GREEN if last else (r["g"][0] if len(row) == 1 else CHIPLINE)
            fill = "#0F2B2A" if last else CHIP
            s.raw(f'<rect x="{rx+0.5:.1f}" y="{ry+0.5:.1f}" width="{w-1:.1f}" height="{CH-1}" rx="9" '
                  f'fill="{fill}" stroke="{stroke}" stroke-opacity="{1 if len(row)==1 or last else 0.9}"/>')
            s.text(rx + 14, ry + 26, c, "plex", 500, 16, ICE if len(row) == 1 or last else SOFT)
            rx += w + 8
        centers.append((ry, ry + CH))
    # connectors with a travelling pulse
    s.css.append("@keyframes flow{from{stroke-dashoffset:24}to{stroke-dashoffset:0}}")
    for i in range(len(rows) - 1):
        y1 = centers[i][1] + 3
        y2 = centers[i + 1][0] - 3
        xm = px + pw / 2
        s.raw(f'<line x1="{xm}" y1="{y1:.1f}" x2="{xm}" y2="{y2:.1f}" stroke="{CYAN}" stroke-width="2" '
              f'stroke-dasharray="4 8" stroke-linecap="round" style="animation:flow 1.2s linear infinite"/>')
        s.raw(f'<path d="M{xm-5} {y2-6:.1f}l5 6 5-6" fill="none" stroke="{CYAN}" stroke-width="2" '
              f'stroke-linecap="round" stroke-linejoin="round"/>')
    s.css.append("@media (prefers-reduced-motion:reduce){line{animation:none!important}}")
    s.save(r["out"])


banner()
for r in REPOS:
    repo_banner(r)
for c in CARDS:
    card(c)
stack()
certs()
for p in sorted(OUT.glob("*.svg")):
    print(f"{p.name:40s} {p.stat().st_size/1024:6.1f} KB")
