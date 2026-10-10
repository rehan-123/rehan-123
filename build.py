"""Generates the PowerShell-session SVGs for the GitHub profile README.

Every pane is one slice of the same console. Only the hero animates.
Run: python3 build.py <path-to-cascadia-woff2-dir>
"""

import base64
import hashlib
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

FONT_DIR = Path(sys.argv[1])
OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

# ---- tokens -------------------------------------------------------------
W = 880
FS = 14
CW = 1200 / 2048 * FS  # Cascadia Code advance width at 14px
LH = 22
PADX = 24
BASE = 16  # baseline offset inside a line box

C = {
    "bg": "#012456",      # Windows PowerShell 5.1 console blue
    "fg": "#EEEDF0",      # its default foreground
    "cmd": "#F9F1A5",     # PSReadLine: command
    "par": "#9DABC2",     # PSReadLine: parameter / operator
    "str": "#61D6D6",     # PSReadLine: string
    "var": "#3FD07A",     # PSReadLine: variable
    "com": "#7FB38A",     # PSReadLine: comment
    "acc": "#3FD07A",     # PS7 FormatAccent / TableHeader (bold green)
    "ok": "#3FD07A",
    "pbg": "#00707A",     # Write-Progress background (DarkCyan)
    "pfg": "#F9F1A5",     # Write-Progress foreground (Yellow)
    "chrome": "#0A1A36",
    "chromefg": "#C3CDDF",
    "edge": "#2A4A80",
}
MAXC = int((W - 2 * PADX) / CW)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def font_face(text_regular, text_bold):
    css = []
    for weight, text in ((400, text_regular), (700, text_bold)):
        if not text:
            continue
        src = FONT_DIR / f"cascadia-code-latin-{weight}-normal.woff2"
        f = TTFont(src)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = []
        opts.hinting = False
        sub = subset.Subsetter(opts)
        sub.populate(text="".join(sorted(set(text + " "))))
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(
            f"@font-face{{font-family:'CascadiaSub';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(css)


class Pane:
    """A slice of console. lines: list of segment lists [(text, colorkey, bold)]."""

    def __init__(self, chrome=False, title=""):
        self.chrome = chrome
        self.title = title
        self.lines = []      # (segments, attrs)
        self.blocks = []     # (line_index, n_lines, fill, attrs) background blocks
        self.extra = []      # raw svg drawn above text (covers, cursors)
        self.css = []

    def add(self, *segs, cls=None):
        norm = []
        for s in segs:
            if isinstance(s, str):
                norm.append((s, "fg", False))
            elif len(s) == 2:
                norm.append((s[0], s[1], False))
            else:
                norm.append(s)
        width = sum(len(t) for t, _, _ in norm)
        assert width <= MAXC, f"line too wide ({width}>{MAXC}): {''.join(t for t,_,_ in norm)}"
        self.lines.append((norm, cls))
        return len(self.lines) - 1

    def blank(self, cls=None):
        return self.add("", cls=cls)

    @property
    def top(self):
        return (38 if self.chrome else 0) + 18

    def y(self, i):
        return self.top + i * LH

    def x(self, col):
        return PADX + col * CW

    def height(self):
        return self.top + len(self.lines) * LH + 14

    def render(self, path, alt):
        H = round(self.height())
        reg = "".join(t for segs, _ in self.lines for t, _, b in segs if not b)
        bold = "".join(t for segs, _ in self.lines for t, _, b in segs if b)
        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(alt)}">',
            f"<title>{esc(alt)}</title>",
            "<style>",
            font_face(reg + self.title, bold),
            "text{font-family:'CascadiaSub','Cascadia Code','Cascadia Mono',Consolas,"
            "'SFMono-Regular',Menlo,monospace;font-size:14px;white-space:pre;}",
            ".t{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;font-size:12.5px;}",
            "@keyframes show{from{opacity:0}to{opacity:1}}",
            "@keyframes blink{0%{opacity:1}50%{opacity:0}}",
            *self.css,
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}}",
            "</style>",
            "<defs><clipPath id='console'>"
            f"<rect x='1' y='{38 if self.chrome else 1}' width='{W-2}' "
            f"height='{H-(38 if self.chrome else 1)-1}' rx='9'/></clipPath></defs>",
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
            f'fill="{C["bg"]}" stroke="{C["edge"]}"/>',
        ]
        if self.chrome:
            out += [
                f'<path d="M0.5 38V10.5a10 10 0 0 1 10-10h{W-21}a10 10 0 0 1 10 10V38z" '
                f'fill="{C["chrome"]}"/>',
                f'<line x1="0.5" y1="38" x2="{W-0.5}" y2="38" stroke="{C["edge"]}"/>',
                f'<text class="t" x="18" y="24" fill="{C["chromefg"]}">{esc(self.title)}</text>',
                # Windows caption buttons: minimise, maximise, close
                f'<g stroke="{C["chromefg"]}" stroke-width="1" fill="none">'
                f'<line x1="{W-133}" y1="19.5" x2="{W-123}" y2="19.5"/>'
                f'<rect x="{W-87.5}" y="14.5" width="10" height="10"/>'
                f'<line x1="{W-42}" y1="14" x2="{W-31}" y2="25"/>'
                f'<line x1="{W-31}" y1="14" x2="{W-42}" y2="25"/></g>',
            ]
        for i, n, fill, attrs in self.blocks:
            out.append(
                f'<rect x="{PADX-10}" y="{self.y(i)}" width="{W-2*PADX+20}" '
                f'height="{n*LH}" fill="{C[fill]}" {attrs}/>'
            )
        for i, (segs, cls) in enumerate(self.lines):
            if not segs or all(t == "" for t, _, _ in segs):
                continue
            n = sum(len(t) for t, _, _ in segs)
            tl = n * CW
            spans = "".join(
                f'<tspan fill="{C[c]}"{" font-weight=\"700\"" if b else ""}>{esc(t)}</tspan>'
                for t, c, b in segs
            )
            ca = f' class="{cls}"' if cls else ""
            out.append(
                f'<text x="{PADX}" y="{self.y(i)+BASE}" textLength="{tl:.2f}" '
                f'lengthAdjust="spacing" xml:space="preserve"{ca}>{spans}</text>'
            )
        out.append('<g clip-path="url(#console)">')
        out += self.extra
        out.append("</g></svg>")
        path.write_text("\n".join(out))
        return path


def thumb(s):
    return hashlib.sha1(s.encode()).hexdigest().upper()


PROMPT = ("PS C:\\> ", "fg")


def cmd_segments(parts):
    """parts: list of (text, kind) where kind in cmd/par/str/var/fg."""
    return [(t, k) for t, k in parts]


# =========================================================================
# 1. HERO — animated
# =========================================================================
hero = Pane(chrome=True, title="Administrator: Windows PowerShell")
cmd1 = [
    ("Get-ADUser", "cmd"), (" rehan.khan ", "fg"), ("-Properties", "par"), (" * ", "fg"),
    ("|", "par"), (" ", "fg"), ("fl", "cmd"), (" Name", "fg"), (",", "par"), ("Title", "fg"),
    (",", "par"), ("Company", "fg"), (",", "par"), ("Office", "fg"), (",", "par"),
    ("Info", "fg"), (",", "par"), ("MemberOf", "fg"),
]
cmd2 = [("Invoke-FastPatch", "cmd"), (" -Fleet", "par"), (" Production", "fg")]

L = {}
L["c1"] = hero.add(PROMPT, *cmd1)
hero.blank()


def fl(label, value, width=8, cls=None, cont=False):
    if cont:
        return hero.add(" " * (width + 3) + value, cls=cls)
    return hero.add((label.ljust(width), "acc", True), (" : ", "fg"), (value, "fg"), cls=cls)


out_rows = [
    ("Name", "Rehan Khan", False),
    ("Title", "Advanced System Administrator", False),
    ("Company", "IT By Design", False),
    ("Office", "New Delhi, India", False),
    ("Info", "~6 years in MSP and enterprise IT. I own L2/L3 escalations for US-based", False),
    ("", "clients and mentor the engineers coming up behind me.", True),
    ("MemberOf", "{Windows Server, AD / Entra ID, Microsoft 365, Virtualization,", False),
    ("", "Backup & DR, Automation}", True),
]
out_idx = []
for k, (lab, val, cont) in enumerate(out_rows):
    cls = f"o{k}"
    if lab == "Name":
        out_idx.append(
            hero.add(("Name".ljust(8), "acc", True), (" : ", "fg"), ("Rehan Khan", "fg", True), cls=cls)
        )
    else:
        out_idx.append(fl(lab, val, cls=cls, cont=cont))
hero.blank()
L["c2"] = hero.add(PROMPT, *cmd2, cls="p2")
hero.blank()
BAR_N = 80
L["pg"] = hero.add((" Invoke-FastPatch", "pfg"), cls="pg")
hero.add(("    Patching production endpoints through Kaseya VSA", "pfg"), cls="pg")
L["bar"] = hero.add(("    [" + "o" * BAR_N + "]", "pfg"), cls="pg")
hero.blank()
hero.blocks.append((L["pg"], 4, "pbg", 'class="pg"'))
hero.blank()
res = [("Endpoints", "600+"), ("Success", "99%"), ("Next", "macOS support")]
res_idx = []
for k, (lab, val) in enumerate(res):
    res_idx.append(hero.add((lab.ljust(9), "acc", True), (" : ", "fg"), (val, "fg"), cls=f"r{k}"))
hero.blank()
L["end"] = hero.add(PROMPT, cls="pend")

# ---- timeline ----
css = hero.css
plen = len(PROMPT[0])
n1 = sum(len(t) for t, _ in cmd1)
n2 = sum(len(t) for t, _ in cmd2)
T1, D1 = 0.5, n1 * 0.018
T_out = T1 + D1 + 0.3
T_p2 = T_out + len(out_rows) * 0.06 + 0.3
T2, D2 = T_p2 + 0.35, n2 * 0.028
T_pg = T2 + D2 + 0.25
T_bar, D_bar = T_pg + 0.15, 2.2
T_res = T_bar + D_bar + 0.2
T_end = T_res + len(res) * 0.1 + 0.2


def show(cls, t):
    css.append(f".{cls}{{animation:show .01s {t:.2f}s both}}")


for k in range(len(out_rows)):
    show(f"o{k}", T_out + k * 0.06)
show("p2", T_p2)
show("pg", T_pg)
for k in range(len(res)):
    show(f"r{k}", T_res + k * 0.1)
show("pend", T_end)


def typing(name, line, n, t0, dur, fill="bg", col0=plen, cursor=True, cursor_from=None, gcls=""):
    x0 = hero.x(col0)
    y0 = hero.y(line)
    w = n * CW
    css.append(
        f"@keyframes {name}{{from{{opacity:1;transform:translateX(0)}}"
        f"to{{opacity:1;transform:translateX({w:.2f}px)}}}}"
        f".{name}{{opacity:0;animation:{name} {dur:.2f}s steps({n}) {t0:.2f}s both}}"
    )
    hero.extra.append(
        f'<clipPath id="k{name}"><rect x="{x0:.2f}" y="{y0}" width="{w:.2f}" height="{LH}"/></clipPath>'
        f'<g clip-path="url(#k{name})" class="{gcls}"><rect class="{name}" x="{x0:.2f}" y="{y0}" '
        f'width="{w:.2f}" height="{LH}" fill="{C[fill]}"/></g>'
    )
    if cursor:
        cf = t0 if cursor_from is None else cursor_from
        css.append(
            f"@keyframes {name}c{{from{{transform:translateX({-(t0-cf)/dur*0:.0f}px)}}"
            f"to{{transform:translateX({w:.2f}px)}}}}"
            f"@keyframes {name}v{{from{{opacity:1}}to{{opacity:1}}}}"
            f".{name}c{{opacity:0;animation:{name}c {dur:.2f}s steps({n}) {t0:.2f}s both,"
            f"{name}v {t0+dur-cf:.2f}s linear {cf:.2f}s}}"
        )
        hero.extra.append(
            f'<rect class="{name}c" x="{x0:.2f}" y="{y0+BASE+2}" width="{CW:.2f}" height="3" fill="{C["fg"]}"/>'
        )


typing("ty1", L["c1"], n1, T1, D1, cursor_from=0.0)
typing("ty2", L["c2"], n2, T2, D2, cursor_from=T_p2)
typing("bar", L["bar"], BAR_N, T_bar, D_bar, fill="pbg", col0=5, cursor=False, gcls="pg")

# final blinking underline cursor
css.append(
    f".endc{{animation:show .01s {T_end:.2f}s both,blink 1.1s steps(1) {T_end:.2f}s infinite}}"
)
hero.extra.append(
    f'<rect class="endc" x="{hero.x(plen):.2f}" y="{hero.y(L["end"])+BASE+2}" '
    f'width="{CW:.2f}" height="3" fill="{C["fg"]}"/>'
)

hero.render(
    OUT / "hero.svg",
    "PowerShell console. Get-ADUser rehan.khan returns: Name Rehan Khan; Title Advanced System "
    "Administrator; Company IT By Design; Office New Delhi, India; about 6 years in MSP and "
    "enterprise IT, owning L2/L3 escalations and mentoring engineers; focus areas Windows Server, "
    "AD and Entra ID, Microsoft 365, virtualization, backup and DR, automation. Then "
    "Invoke-FastPatch runs: 600+ endpoints patched at 99% success, macOS support next.",
)

# =========================================================================
# 2. TOOLS — Format-Table
# =========================================================================
tools = Pane()
tools.add(
    PROMPT, ("Get-Module", "cmd"), (" -ListAvailable ", "par"), ("| ", "par"), ("?", "cmd"),
    (" Author ", "fg"), ("-eq", "par"), (" 'Rehan Khan' ", "str"), ("| ", "par"),
    ("ft", "cmd"), (" Name", "fg"), (",", "par"), ("Platform", "fg"), (",", "par"),
    ("Purpose", "fg"),
)
tools.blank()
rows = [
    ("FastPatch", "Kaseya VSA, production", "Patch classification + remediation, 600+ machines, 99%"),
    ("SpanningAuditor", "Spanning API, 200+ M365 orgs", "Read-only backup coverage audit across the fleet"),
    ("EWSHardcore", "Exchange Online, fleet-wide", "EWS audit + remediation for the EWS retirement"),
    ("SBHIT", "SharePoint, Graph delta API", "Backup health on 3M+ items / 2.1 TB, DuckDB analysis"),
    ("FSLogixToolkit", "RDS / FSLogix hosts", "Read-only profile health checks and forensics"),
    ("DeviceDiag", "Windows endpoints", "Leftover MDM, Autopilot and RMM, hardware, licensing"),
]
w1 = max(len(r[0]) for r in rows) + 2
w2 = max(len(r[1]) for r in rows) + 2
tools.add(("Name".ljust(w1), "acc", True), ("Platform".ljust(w2), "acc", True), ("Purpose", "acc", True))
tools.add(("----".ljust(w1), "acc", True), ("--------".ljust(w2), "acc", True), ("-------", "acc", True))
for a, b, c in rows:
    tools.add((a.ljust(w1), "cmd"), (b.ljust(w2), "fg"), (c, "fg"))
tools.blank()
tools.add(("# Internal NOC tooling, built in PowerShell 7 and Python. Source isn't public.", "com"))
tools.render(
    OUT / "tools.svg",
    "Internal tools: FastPatch, Kaseya VSA patch classification and remediation, 600+ machines at "
    "99%; SpanningAuditor, read-only Spanning backup coverage audit across 200+ Microsoft 365 "
    "tenants; EWSHardcore, Exchange Online EWS audit and remediation; SBHIT, SharePoint backup "
    "health via Graph delta API on 3M+ items; FSLogix health and forensics toolkit; DeviceDiag, "
    "endpoint audit for leftover MDM, Autopilot and RMM.",
)

# =========================================================================
# 3. PROJECT — technical-analysis-agent (public, linked)
# =========================================================================
ta = Pane()
ta.add(("# technical-analysis-agent", "com", True), ("  (public)", "com"))
for s in [
    "# One specialist agent in a multi-agent investment platform. ~24 indicators in pure",
    "# pandas/numpy, market-structure and volume-profile engines, a weighted confluence",
    "# score, and entry / stop / targets with a readable reasoning chain. Never a bare",
    "# BUY or SELL.  Python, FastAPI, Pydantic, Ollama, Finnhub",
]:
    ta.add((s, "com"))
ta.add(PROMPT, ("cd", "cmd"), (" .\\technical-analysis-agent\\", "fg"), ("; ", "par"),
       ("pytest", "cmd"), (" -q", "par"))
DOTS = 80
for k, pct in enumerate([" 33%", " 66%", "100%"]):
    ta.add(("." * DOTS, "ok"), ("  [" + pct + "]", "fg"))
ta.add(("240 passed", "ok", True), (" in 2.45s", "ok"))
ta.render(
    OUT / "project-technical-analysis-agent.svg",
    "technical-analysis-agent: a specialist technical-analysis agent for a multi-agent investment "
    "platform with about 24 indicators, market-structure and volume-profile engines, confluence "
    "scoring and risk-managed entries. pytest: 240 passed.",
)

# =========================================================================
# 4. PROJECTS — private builds
# =========================================================================
pv = Pane()
pv.add(("# ecom-autopilot", "com", True), ("  (private)", "com"))
for s in [
    "# Decision engine and operating layer for selling on Indian marketplaces. Part 1",
    "# decides whether a product is worth selling: landed cost, three-scenario economics,",
    "# compliance, then a human approval gate. Part 2 runs listings, inventory, orders,",
    "# returns and settlement, and feeds measured profit back into the next decision.",
    "# AI research is never allowed to invent a price or a cost.",
    "# Python, FastAPI, React, Vite, event-sourced audit ledger",
]:
    pv.add((s, "com"))
pv.add(PROMPT, ("cd", "cmd"), (" .\\ecom-autopilot\\", "fg"), ("; ", "par"), ("pytest", "cmd"),
       (" -q ", "par"), ("| ", "par"), ("Select-Object", "cmd"), (" -Last", "par"), (" 2", "fg"))
pv.add(("." * (1029 % DOTS), "ok"), (" " * (DOTS - 1029 % DOTS) + "  [100%]", "fg"))
pv.add(("1029 passed", "ok", True), (" in 39.28s", "ok"))
pv.blank()
pv.add(("# meridian", "com", True), ("  (private, in development)", "com"))
pv.add(("# Decision-first paper-trading terminal for Indian equities (NSE), built on a", "com"))
pv.add(("# multi-agent investment platform.  FastAPI, React, Vite, TypeScript", "com"))
pv.render(
    OUT / "projects-private.svg",
    "Private builds. ecom-autopilot: decision engine and operating layer for Indian marketplace "
    "selling, from landed-cost economics and compliance to listings, orders and settlement; "
    "pytest: 1029 passed. meridian: decision-first paper-trading terminal for Indian equities, in "
    "development.",
)

# =========================================================================
# 5. STACK — hashtable output
# =========================================================================
st = Pane()
st.add(PROMPT, ("$Stack", "var"))
st.blank()
stack = [
    ("Identity", "Active Directory, Entra ID, Group Policy, ADCS/PKI, Kerberos/NTLM, DNS/DHCP"),
    ("Microsoft365", "Exchange Online, SharePoint, Microsoft Graph API"),
    ("Endpoints", "Intune, Jamf Pro"),
    ("Virtualization", "VMware, Hyper-V failover clusters, RDS, FSLogix"),
    ("BackupDR", "Veeam, Spanning, Acronis, Unitrends, ShadowProtect SPX, Datto, AWS Backup"),
    ("MSPTooling", "Kaseya VSA, ConnectWise Automate, ScreenConnect, IT Glue"),
    ("Network", "FortiGate, SonicWall"),
    ("Code", "PowerShell 7, Python, FastAPI, Pydantic, pandas, React, TypeScript, pytest"),
]
nw = max(len(k) for k, _ in stack) + 2
st.add(("Name".ljust(nw), "acc", True), ("Value", "acc", True))
st.add(("----".ljust(nw), "acc", True), ("-----", "acc", True))
for k, v in stack:
    st.add((k.ljust(nw), "fg"), ("{", "par"), (v, "fg"), ("}", "par"))
st.render(
    OUT / "stack.svg",
    "Tech stack. Identity: Active Directory, Entra ID, Group Policy, ADCS/PKI, Kerberos/NTLM, "
    "DNS/DHCP. Microsoft 365: Exchange Online, SharePoint, Graph API. Endpoints: Intune, Jamf Pro. "
    "Virtualization: VMware, Hyper-V clusters, RDS, FSLogix. Backup and DR: Veeam, Spanning, "
    "Acronis, Unitrends, ShadowProtect SPX, Datto, AWS Backup. MSP tooling: Kaseya VSA, "
    "ConnectWise Automate, ScreenConnect, IT Glue. Network: FortiGate, SonicWall. Code: "
    "PowerShell 7, Python, FastAPI, Pydantic, pandas, React, TypeScript, pytest.",
)

# =========================================================================
# 6. CERTS — Cert:\ drive
# =========================================================================
ce = Pane()
ce.add(PROMPT, ("Get-ChildItem", "cmd"), (" Cert:\\CurrentUser\\My", "fg"))
ce.blank()
ce.add(("   PSParentPath: ", "fg"), ("Microsoft.PowerShell.Security\\Certificate::CurrentUser\\My", "fg"))
ce.blank()
certs = [
    "CN=AZ-800 Windows Server Hybrid Core, O=Microsoft",
    "CN=AZ-801 Windows Server Hybrid Advanced, O=Microsoft",
    "CN=MD-102 Endpoint Administrator, O=Microsoft",
    "CN=VMCE Veeam Certified Engineer, O=Veeam",
    "CN=Automate Certified Professional, O=ConnectWise",
    "CN=Jamf Certified Associate, O=Jamf",
]
ce.add(("Thumbprint".ljust(42), "acc", True), ("Subject", "acc", True))
ce.add(("----------".ljust(42), "acc", True), ("-------", "acc", True))
for s in certs:
    ce.add((thumb(s).ljust(42), "par"), (s, "fg"))
ce.render(
    OUT / "certs.svg",
    "Certifications: AZ-800 and AZ-801 Windows Server Hybrid, MD-102 Endpoint Administrator, "
    "VMCE Veeam Certified Engineer, ConnectWise Automate Certified Professional, Jamf Certified "
    "Associate.",
)

for p in sorted(OUT.glob("*.svg")):
    print(f"{p.name:44s} {p.stat().st_size/1024:6.1f} KB")
print(f"timeline: end prompt at {T_end:.2f}s")
