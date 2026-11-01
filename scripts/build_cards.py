#!/usr/bin/env python3
"""Builds the animated SVG cards used by the README.

Same design language as my GitHub profile README, in an emerald + amber
palette. All text lives in the data section below; edit it and re-run:

    python3 scripts/build_cards.py

Output goes to assets/cards/. Standard library only.
"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"

# ---------------------------------------------------------------- palette
C = {
    "bg0": "#07100C",
    "bg1": "#0C1712",
    "bg2": "#12241B",
    "panel": "#0F1E17",
    "line": "#1C3529",
    "line2": "#2A4D3B",
    "accent": "#2FBF71",   # emerald (main colour)
    "soft": "#7FE0A8",     # light green (kickers, highlights)
    "pale": "#C6F4D9",
    "silver": "#E8F1EC",
    "mist": "#C3D6CB",
    "muted": "#8EA99A",
    "dim": "#5C7A69",
    "amber": "#F5B461",    # second accent (desert sun)
    "sky": "#8FD3F5",
}

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- content
TYPING = [
    "node play.js --record",
    "obstacle ahead: CACTUS · distance 74 → jump",
    "obstacle ahead: BIRD (mid) · distance 90 → duck",
    "speed 13.0 · score 7,899 · crashes 0",
]

STATS = [
    ("7,899", "points in 7 min, 0 crashes"),
    ("13.0", "top game speed reached"),
    ("200/s", "decisions per second"),
    ("44", "lines of JavaScript"),
]

LOOP = [
    ("READ", "the game state", ["next obstacle · type", "distance · height · speed"]),
    ("DECIDE", "what to do", ["react at speed × 13", "jump · duck · keep running"]),
    ("ACT", "press the key", ["startJump() · setDuck()", "drop fast after clearing"]),
]

RULES = [
    ("Cactus", "any size", "JUMP", "amber", "cactus"),
    ("Low bird", "flies at ground level", "JUMP", "amber", "bird_low"),
    ("Mid bird", "flies at head height", "DUCK", "sky", "bird_mid"),
    ("High bird", "flies over the dino", "RUN", "soft", "bird_high"),
]

LESSONS = [
    ("The game speeds up", "a fixed jump distance fails later, so the bot reacts earlier as speed grows", "SOLVED"),
    ("Birds at three heights", "jumping into a mid-height bird ends the game, so heights are checked", "SOLVED"),
    ("Long jumps at top speed", "the dino landed on the next cactus; it now drops fast once clear", "SOLVED"),
    ("Different Chrome versions", "Runner.getInstance() in new Chrome, Runner.instance_ in old", "SOLVED"),
    ("Screen-only version", "play using screenshots alone, without reading the game's code", "NEXT"),
    ("Neural network (NEAT)", "let a model learn the game and race it against this bot", "NEXT"),
]

TITLES = [
    ("01", "DEMO", "Watch it", "play.", "REAL CHROME DINO", "demo"),
    ("02", "HOW IT WORKS", "Read, decide,", "act.", "200 TIMES A SECOND", "how"),
    ("03", "THE RULES", "Jump, duck", "or run.", "ONE RULE PER OBSTACLE", "rules"),
    ("04", "TRY IT", "Run it", "yourself.", "NO INSTALL NEEDED", "try"),
    ("05", "LESSONS", "Problems I", "ran into.", "AND WHAT'S NEXT", "lessons"),
]


# ---------------------------------------------------------------- helpers
def e(s):
    return escape(str(s), {'"': "&quot;"})


STYLE = f"""
<style>
.serif{{font-family:{SERIF}}}
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.twinkle{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.pulse{{animation:pl 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes pl{{0%,100%{{opacity:.55;transform:scale(1)}}50%{{opacity:1;transform:scale(1.35)}}}}
.float{{animation:fl 6s ease-in-out infinite}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.fadein{{animation:fi 1.2s ease-out both}}
@keyframes fi{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
</style>"""


def base_defs(uid):
    return f"""
<defs>
  <radialGradient id="{uid}-bg" cx="70%" cy="30%" r="90%">
    <stop offset="0" stop-color="{C['bg2']}"/>
    <stop offset=".55" stop-color="{C['bg1']}"/>
    <stop offset="1" stop-color="{C['bg0']}"/>
  </radialGradient>
  <radialGradient id="{uid}-glowA" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="{C['accent']}" stop-opacity=".38"/>
    <stop offset="1" stop-color="{C['accent']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}-glowB" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="{C['amber']}" stop-opacity=".10"/>
    <stop offset="1" stop-color="{C['amber']}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="{uid}-silver" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#FFFFFF"/>
    <stop offset=".5" stop-color="{C['mist']}"/>
    <stop offset="1" stop-color="{C['soft']}"/>
  </linearGradient>
  <linearGradient id="{uid}-rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['soft']}" stop-opacity="0"/>
    <stop offset=".25" stop-color="{C['soft']}" stop-opacity=".8"/>
    <stop offset="1" stop-color="{C['soft']}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="{uid}-grid" width="28" height="28" patternUnits="userSpaceOnUse">
    <path d="M28 0H0V28" fill="none" stroke="{C['soft']}" stroke-opacity=".05"/>
  </pattern>
</defs>"""


def frame(w, h, uid, glow=(0.75, 0.3)):
    gx, gy = glow
    return f"""
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#{uid}-bg)" stroke="{C['line']}"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#{uid}-grid)"/>
<ellipse cx="{w*gx:.0f}" cy="{h*gy:.0f}" rx="{w*0.35:.0f}" ry="{h*0.7:.0f}" fill="url(#{uid}-glowA)"/>
<ellipse cx="{w*(1-gx):.0f}" cy="{h*(1-gy):.0f}" rx="{w*0.25:.0f}" ry="{h*0.5:.0f}" fill="url(#{uid}-glowB)"/>"""


def stars(w, h, n, seed, pad=20):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(pad, w - pad), rnd.uniform(pad, h - pad)
        r = rnd.choice([0.8, 1, 1.2, 1.6])
        d = rnd.uniform(0, 4)
        out.append(f'<circle class="twinkle" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{C["silver"]}" style="animation-delay:{d:.1f}s"/>')
    return "\n".join(out)


def svg(w, h, uid, title, desc, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="{uid}-t {uid}-d">
<title id="{uid}-t">{e(title)}</title>
<desc id="{uid}-d">{e(desc)}</desc>
{STYLE}
{base_defs(uid)}
{body}
</svg>
"""


def text(x, y, s, size, fill, cls="sans", anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{e(s)}</text>'


def mono_w(s, size):
    return sum(size * 0.61 for _ in s)


def chip(x, y, label, size=11, color=None):
    w = mono_w(label, size) + 22
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
        + text(x + 11, y + 16, label, size, color or C["mist"], "mono")
    ), w


def chips(x, y, labels, gap=8, **kw):
    out, cx = [], x
    for lb in labels:
        s, w = chip(cx, y, lb, **kw)
        out.append(s)
        cx += w + gap
    return "\n".join(out)


def write(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:22s} {len(content.encode()) / 1024:6.1f} KB")


# ---------------------------------------------------------------- pixel art
# Original pixel sprites drawn on a grid ("#" = filled pixel).
DINO = [
    "..........######",
    ".........##.####",
    ".........#######",
    ".........#######",
    ".........####...",
    ".........######.",
    "#.......#####...",
    "#.....#######...",
    "##...#########..",
    "###.#######.#...",
    "##########......",
    ".#########......",
    "..#######.......",
    "...##..##.......",
    "...#....#.......",
    "...##...##......",
]
CACTUS = [
    "....##....",
    "...####...",
    "...####...",
    "#..####..#",
    "##.####.##",
    "##.####.##",
    "##.####.##",
    "########..",
    ".#######..",
    "...####...",
    "...####...",
    "...####...",
    "...####...",
]
BIRD = [
    "....#.......",
    "....##......",
    "..####......",
    "#########...",
    "...#######..",
    "....######..",
    "......####..",
]


def sprite(rows, x, y, px, fill, extra=""):
    rects = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            if row[i] == "#":
                k = i
                while k < len(row) and row[k] == "#":
                    k += 1
                rects.append(f'<rect x="{x + i * px}" y="{y + j * px}" width="{(k - i) * px}" height="{px}"/>')
                i = k
            else:
                i += 1
    return f'<g fill="{fill}" {extra}>{"".join(rects)}</g>'


# ---------------------------------------------------------------- hero
def build_hero():
    W, H, u = 1200, 500, "hero"

    per = 4.5
    total = per * len(TYPING)
    typed = []
    for i, ln in enumerate(TYPING):
        t0 = i * per / total
        t1 = (i * per + 1.8) / total
        t3 = (i + 1) * per / total
        full = round(mono_w(ln, 13) + 4)
        if i == 0:
            kt_w, v_w = f"0;{t1:.4f};1", f"0;{full};{full}"
            kt_o, v_o = f"0;{t3:.4f}", "1;0"
        else:
            kt_w, v_w = f"0;{t0:.4f};{t1:.4f};1", f"0;0;{full};{full}"
            kt_o, v_o = (f"0;{t0:.4f};{t3:.4f}", "0;1;0") if i < len(TYPING) - 1 else (f"0;{t0:.4f}", "0;1")
        typed.append(f"""
<clipPath id="hero-type{i}"><rect x="200" y="58" height="24" width="0">
  <animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt_w}" values="{v_w}"/>
</rect></clipPath>
<g clip-path="url(#hero-type{i})" opacity="{1 if i == 0 else 0}">
  <animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt_o}" values="{v_o}"/>
  {text(202, 75, ln, 13, C['silver'], 'mono')}
</g>""")

    # desert scene on the right: dino jumps each time a cactus scrolls past
    sx, sy, sw, sh = 700, 70, 440, 330
    ground = sy + 262
    px = 5
    dino_h = len(DINO) * px
    loop = 2.6  # seconds per cactus
    cactus_w = len(CACTUS[0]) * px
    cactus = sprite(CACTUS, 0, ground - len(CACTUS) * px, px, C['soft'])
    dunes = " ".join(f"M{sx + 20 + k * 90} {ground + 22} h{24 + (k % 3) * 10}" for k in range(5))
    scene = f"""
<clipPath id="hero-scene"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="18"/></clipPath>
<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="18" fill="{C['bg0']}" fill-opacity=".75" stroke="{C['line2']}"/>
<g clip-path="url(#hero-scene)">
  <circle cx="{sx + 340}" cy="{sy + 86}" r="34" fill="{C['amber']}" fill-opacity=".85"/>
  <circle cx="{sx + 340}" cy="{sy + 86}" r="56" fill="{C['amber']}" fill-opacity=".12" class="pulse"/>
  {stars(sw, 160, 0, 1)}
  <line x1="{sx}" y1="{ground}" x2="{sx + sw}" y2="{ground}" stroke="{C['mist']}" stroke-opacity=".6"/>
  <path d="{dunes}" stroke="{C['dim']}" stroke-width="2">
    <animateTransform attributeName="transform" type="translate" values="0 0;-90 0" dur="{loop / 2}s" repeatCount="indefinite"/>
  </path>
  <g>
    <animateTransform attributeName="transform" type="translate" values="{sx + sw + 10} 0;{sx - cactus_w - 10} 0" dur="{loop}s" repeatCount="indefinite"/>
    {cactus}
  </g>
  <g>
    <animateTransform attributeName="transform" type="translate" dur="{loop}s" repeatCount="indefinite"
      values="0 0;0 0;0 -96;0 -96;0 0;0 0" keyTimes="0;.62;.74;.80;.92;1" calcMode="spline"
      keySplines="0 0 1 1;.2 .7 .4 1;0 0 1 1;.6 0 .8 .3;0 0 1 1"/>
    {sprite(DINO, sx + 60, ground - dino_h, px, C['silver'])}
  </g>
</g>
{text(sx + 22, sy + 34, "BOT · AUTOPLAY", 11, C['soft'], 'mono', 'start', 'letter-spacing="3"')}
<circle cx="{sx + sw - 30}" cy="{sy + 30}" r="5" fill="{C['accent']}" class="pulse"/>
{text(sx + 22, sy + sh - 18, "jump · duck · run", 11, C['muted'], 'mono')}
{text(sx + sw - 22, sy + sh - 18, "crashes: 0", 11, C['amber'], 'mono', 'end')}
"""

    body = f"""
{frame(W, H, u, (0.78, 0.35))}
<defs>
  <linearGradient id="hero-sheen" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="-60" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".85"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;900 0;900 0" keyTimes="0;.45;1" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
{stars(W, H, 40, 11)}

<rect x="60" y="52" width="600" height="36" rx="18" fill="{C['bg0']}" fill-opacity=".7" stroke="{C['line2']}"/>
<circle cx="80" cy="70" r="4" fill="{C['soft']}" class="pulse"/>
{text(94, 75, "~/dino-bot", 13, C['muted'], 'mono')}
{text(180, 75, "$", 13, C['soft'], 'mono')}
{''.join(typed)}

<line x1="60" y1="128" x2="92" y2="128" stroke="{C['soft']}"/>
{text(104, 132, "JAVASCRIPT · PLAYWRIGHT · AUTOMATION", 12, C['soft'], 'mono', 'start', 'letter-spacing="3"')}
<g class="fadein">
  {text(56, 224, "DINO BOT", 92, f"url(#{u}-silver)", 'serif', 'start', 'letter-spacing="6"')}
  {text(56, 224, "DINO BOT", 92, "url(#hero-sheen)", 'serif', 'start', 'letter-spacing="6" opacity=".55"')}
</g>
<rect x="60" y="246" width="520" height="1.5" fill="url(#{u}-rule)"/>
<circle cx="60" cy="247" r="3" fill="#fff">
  <animate attributeName="cx" values="60;580;60" dur="9s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="9s" repeatCount="indefinite"/>
</circle>
{text(60, 288, "THE CHROME DINO, ON AUTOPILOT", 17, C['silver'], 'sans', 'start', 'letter-spacing="5" font-weight="600"')}
{text(60, 320, "A 44-line bot that jumps cactuses and ducks under birds", 15, C['mist'], 'sans')}
<text x="60" y="358" class="serif" font-size="20" fill="{C['pale']}" font-style="italic">It reads the game, decides, and never misses a jump.</text>
{chips(60, 384, ["● 7,899 points", "0 crashes", "Top speed 13.0"], size=11)}

<line x1="60" y1="440" x2="1140" y2="440" stroke="{C['line']}"/>
{text(60, 466, "PASTE INTO DEVTOOLS · OR RUN WITH NODE", 11, C['muted'], 'mono', 'start', 'letter-spacing="2.5"')}
{text(1140, 466, "BUILT BY HEMASHREE", 11, C['silver'], 'mono', 'end', 'letter-spacing="2.5"')}
{scene}
"""
    write("hero.svg", svg(W, H, u, "Dino Bot",
                          "A 44-line JavaScript bot that plays the Chrome Dino game by itself: 7,899 points, 0 crashes, top speed 13.0.", body))


# ---------------------------------------------------------------- section titles
def build_title(num, kicker, plain, italic, right, slug):
    W, H, u = 1200, 104, f"t{num}"
    body = f"""
{text(30, 32, num, 12, C['silver'], 'mono', 'start', 'letter-spacing="3"')}
{text(58, 32, kicker, 12, C['soft'], 'mono', 'start', 'letter-spacing="3"')}
{text(1170, 32, right, 11, C['muted'], 'mono', 'end', 'letter-spacing="3"')}
<text x="30" y="80" class="serif" font-size="40" fill="{C['silver']}">{e(plain)} <tspan fill="{C['soft']}" font-style="italic">{e(italic)}</tspan></text>
<rect x="30" y="96" width="1140" height="1.2" fill="url(#{u}-rule)"/>
<circle cy="96.6" r="2.6" fill="#fff">
  <animate attributeName="cx" values="30;1170" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="6s" repeatCount="indefinite"/>
</circle>
"""
    write(f"title-{slug}.svg", svg(W, H, u, f"{num} {kicker.title()}: {plain} {italic}", right, body))


# ---------------------------------------------------------------- stats
def build_stats():
    W, H, u = 1200, 150, "stats"
    parts = [frame(W, H, u, (0.5, 0.5))]
    cw = 1136 / len(STATS)
    for k, (big, small) in enumerate(STATS):
        x = 32 + k * cw
        parts.append(f'<rect x="{x + 4:.0f}" y="24" width="{cw - 8:.0f}" height="102" rx="16" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(text(round(x + cw / 2), 78, big, 38, f"url(#{u}-silver)", 'serif', 'middle'))
        parts.append(text(round(x + cw / 2), 104, small, 13, C['muted'], 'sans', 'middle'))
    desc = "; ".join(f"{a} {b}" for a, b in STATS)
    write("stats.svg", svg(W, H, u, "Results", desc, "".join(parts)))


# ---------------------------------------------------------------- loop
def build_loop():
    W, H, u = 1200, 330, "loop"
    xs = [70, 450, 830]
    parts = [frame(W, H, u, (0.5, 0.5))]
    for k, (name, sub, lines) in enumerate(LOOP):
        x = xs[k]
        parts.append(f"""
<rect x="{x}" y="60" width="300" height="180" rx="18" fill="{C['panel']}" stroke="{C['line2']}"/>
<circle cx="{x + 40}" cy="100" r="16" fill="none" stroke="{C['soft']}"/>
<circle cx="{x + 40}" cy="100" r="5" fill="{C['pale']}" class="pulse" style="animation-delay:{k * 0.8}s"/>
{text(x + 68, 98, f"0{k + 1}", 11, C['muted'], 'mono', 'start', 'letter-spacing="2"')}
{text(x + 68, 115, sub.upper(), 10, C['soft'], 'mono', 'start', 'letter-spacing="2"')}
{text(x + 24, 168, name, 34, C['silver'], 'serif', 'start', 'letter-spacing="4"')}
{text(x + 24, 198, lines[0], 13, C['mist'], 'mono')}
{text(x + 24, 220, lines[1], 13, C['muted'], 'mono')}""")
        if k < 2:
            a, b = x + 300, xs[k + 1]
            parts.append(f"""<path d="M{a + 6} 150H{b - 6}" stroke="{C['soft']}" stroke-dasharray="3 5"/>
<path d="M{b - 14} 144l8 6-8 6" fill="none" stroke="{C['soft']}"/>
<circle r="3.5" fill="#fff"><animateMotion dur="1.8s" repeatCount="indefinite" path="M{a + 6} 150H{b - 10}" begin="{k * 0.9}s"/></circle>""")
    loop = f"M{xs[2] + 150} 240 V282 H{xs[0] + 150} V244"
    parts.append(f"""<path d="{loop}" fill="none" stroke="{C['soft']}" stroke-opacity=".5" stroke-dasharray="3 6"/>
<path d="M{xs[0] + 144} 252l6-8 6 8" fill="none" stroke="{C['soft']}" stroke-opacity=".7"/>
<circle r="3" fill="{C['pale']}"><animateMotion dur="5s" repeatCount="indefinite" path="{loop}"/></circle>
{text(600, 300, "EVERY 5 MILLISECONDS", 11, C['soft'], 'mono', 'middle', 'letter-spacing="4"')}
{text(600, 38, "No screenshots, no guessing: the bot asks the game where the next obstacle is.", 14, C['muted'], 'serif', 'middle', 'font-style="italic"')}""")
    desc = " → ".join(f"{n}: {', '.join(l)}" for n, _, l in LOOP)
    write("loop.svg", svg(W, H, u, "Read, decide, act", desc, "".join(parts)))


# ---------------------------------------------------------------- rules
def build_rules():
    W, H, u = 1200, 290, "rules"
    parts = [frame(W, H, u, (0.3, 0.4))]
    cw = 1136 / len(RULES)
    for k, (name, sub, action, col, kind) in enumerate(RULES):
        x = 32 + k * cw
        color = C[col]
        cx = x + cw / 2
        parts.append(f'<rect x="{x + 6:.0f}" y="26" width="{cw - 12:.0f}" height="238" rx="18" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        # mini scene: ground line + obstacle at the right height
        gy = 132
        parts.append(f'<line x1="{x + 30:.0f}" y1="{gy}" x2="{x + cw - 30:.0f}" y2="{gy}" stroke="{C["dim"]}"/>')
        if kind == "cactus":
            parts.append(sprite(CACTUS, round(cx - 20), gy - 52, 4, C['soft']))
        else:
            by = {"bird_low": gy - 30, "bird_mid": gy - 62, "bird_high": gy - 92}[kind]
            parts.append(f'<g class="float">{sprite(BIRD, round(cx - 24), by, 4, C["soft"])}</g>')
        parts.append(text(round(x + 30), 172, name, 24, C['silver'], 'serif'))
        parts.append(text(round(x + 30), 196, sub, 13, C['muted'], 'sans'))
        parts.append(f'<rect x="{x + 30:.0f}" y="216" width="{mono_w(action, 13) + 44:.0f}" height="30" rx="15" fill="{color}" fill-opacity=".14" stroke="{color}"/>')
        parts.append(f'<circle cx="{x + 46:.0f}" cy="231" r="4" fill="{color}" class="pulse" style="animation-delay:{k * 0.6}s"/>')
        parts.append(text(round(x + 58), 236, action, 13, color, 'mono', 'start', 'letter-spacing="2" font-weight="700"'))
    desc = "; ".join(f"{n} ({s}): {a.lower()}" for n, s, a, _, _ in RULES)
    write("rules.svg", svg(W, H, u, "Jump, duck or run", desc, "".join(parts)))


# ---------------------------------------------------------------- lessons
def build_lessons():
    W, H = 1200, 70 + 66 * len(LESSONS)
    u = "les"
    parts = [frame(W, H, u, (0.2, 0.4))]
    for k, (name, what, status) in enumerate(LESSONS):
        y = 32 + k * 66
        col = C['accent'] if status == "SOLVED" else C['amber']
        parts.append(f'<rect x="32" y="{y}" width="1136" height="54" rx="14" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(text(56, y + 34, f"0{k + 1}", 12, C['dim'], 'mono'))
        parts.append(text(96, y + 35, name, 20, C['silver'], 'serif'))
        parts.append(text(380, y + 33, what, 13.5, C['muted'], 'sans'))
        if status == "SOLVED":
            parts.append(f'<path d="M1046 {y + 27}l5 5 9-10" fill="none" stroke="{col}" stroke-width="2"/>')
        else:
            parts.append(f'<circle class="pulse" cx="{1053}" cy="{y + 27}" r="4" fill="{col}"/>')
        parts.append(text(1150, y + 32, status, 10.5, col, 'mono', 'end', 'letter-spacing="2"'))
    desc = "; ".join(f"{n} ({s.lower()}): {w}" for n, w, s in LESSONS)
    write("lessons.svg", svg(W, H, u, "Problems I ran into, and what's next", desc, "".join(parts)))


# ---------------------------------------------------------------- footer
def build_footer():
    W, H, u = 1200, 300, "foot"
    body = f"""
{frame(W, H, u, (0.5, 0.75))}
{stars(W, H, 30, 5)}
{text(600, 64, "A WEEKEND PROJECT · BUILT FOR FUN AND LEARNING", 12, C['soft'], 'mono', 'middle', 'letter-spacing="4"')}
<text x="600" y="164" class="serif" font-size="88" font-style="italic" text-anchor="middle" fill="url(#{u}-silver)" letter-spacing="2">Dino Bot</text>
<text x="600" y="164" class="serif" font-size="88" font-style="italic" text-anchor="middle" fill="none" stroke="#fff" stroke-width="1.4" stroke-dasharray="120 900" letter-spacing="2" opacity=".8">Dino Bot<animate attributeName="stroke-dashoffset" values="1020;0" dur="6s" repeatCount="indefinite"/></text>
<rect x="380" y="192" width="440" height="1.2" fill="url(#{u}-rule)"/>
{text(600, 232, "Made by Hemashree · B.Tech CSE, VIT Chennai", 15, C['mist'], 'sans', 'middle')}
{text(600, 266, "If it made you smile, leave a star ★", 18, C['amber'], 'serif', 'middle', 'font-style="italic"')}
"""
    write("footer.svg", svg(W, H, u, "Dino Bot", "Made by Hemashree. If it made you smile, leave a star.", body))


def main():
    print("building cards →", OUT.relative_to(ROOT))
    build_hero()
    for t in TITLES:
        build_title(*t)
    build_stats()
    build_loop()
    build_rules()
    build_lessons()
    build_footer()


if __name__ == "__main__":
    main()
