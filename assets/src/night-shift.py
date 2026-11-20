"""«Ночная смена» v2: быстрый цикл день-ночь за окном, пиксельные часы на подоконнике в такт солнцу,
чёрные наушники, горячий чёрный кофе. Всё — внутри одного SVG, без внешних данных."""
import math, pathlib, random, sys

OUT = pathlib.Path(sys.argv[1])
U = 5                      # размер пикселя
W, H = 160, 64             # сцена в клетках (800x320)
T = 10.0                   # цикл печати кода
D = 36.0                   # сутки за окном, с; цикл начинается в 06:00
SLOTS = 48                 # шаг часов — полчаса

PAL = {
    "H": "#3a2a2e", "h": "#5a4246",                        # волосы
    "B": "#1f1b27", "b": "#0f0d15", "X": "#5a5470",        # чёрные наушники
    "s": "#f2c29b", "S": "#cf9670",                        # кожа
    "Y": "#f7c23a", "y": "#cf9520", "o": "#e3a92c", "O": "#b97f17",   # худи
    "R": "#2c2342", "L": "#4a3d6b", "C": "#3a2f55",        # кресло
    "W": "#f1edff", "w": "#c3bde6", "p": "#ffc2d8", "e": "#2b2238", "c": "#ff9ab8",  # зайчик
    "t": "#c98a45", "T": "#ffe7b0",                        # тост
    "m": "#c9c4dd", "M": "#8f89aa", "n": "#5d577a",        # тостер
    "u": "#fffdf8", "U": "#ff7aa8", "q": "#24140c", "Q": "#4a2e20",   # кружка и кофе
    "g": "#6bd49a", "G": "#3f9e6c", "f": "#9a7458", "F": "#7a5a45",   # растение
    "a": "#ffe680", "A": "#ffb83a",                        # солнце
    "l": "#fff1b8", "j": "#e9d38c",                        # луна
    "v": "#f4f7ff", "V": "#d6defa",                        # облака
    "Z": "#9a91bf", "z": "#6f6694", "k": "#120d1e",        # часы
}

def sprite(rows, x0, y0, cls=None, extra=""):
    out = []
    for dy, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch in ". ":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == ch:
                run += 1
            out.append(f'<rect x="{(x0 + x) * U}" y="{(y0 + dy) * U}" width="{run * U}" height="{U}" fill="{PAL[ch]}"/>')
            x += run
    body = "".join(out)
    return f'<g class="{cls}"{extra}>{body}</g>' if cls else body

def rect(x, y, w, h, fill, cls=None, extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<rect{c}{extra} x="{x * U}" y="{y * U}" width="{w * U}" height="{h * U}" fill="{fill}"/>'

def pct(t, total=T):
    return f"{t / total * 100:.3f}%"

def hp(h):
    """час суток (6…30) → процент дневного цикла"""
    return f"{(h - 6) / 24 * 100:.3f}%"

def day_anim(cls, prop, pts):
    kf = "".join(f"{hp(h)}{{{prop}:{v}}}" for h, v in pts)
    return f".{cls}{{animation:{cls} {D}s linear infinite}}@keyframes {cls}{{{kf}}}"

css, g = [], []
random.seed(7)

# ---------- общие кривые дня ----------
NIGHT = [(6, .3), (7, 0), (18.5, 0), (20, 1), (29, 1), (30, .3)]
css += [
    day_anim("ov", "opacity", [(6, .45), (7.5, .1), (8.5, 0), (17.5, 0), (19, .3), (20.5, .62), (28.5, .62), (30, .45)]),
    day_anim("nt", "opacity", NIGHT),
    day_anim("gl", "opacity", [(6, .6), (8, .12), (18, .12), (20, 1), (29, 1), (30, .6)]),
    day_anim("beam", "opacity", [(6, 0), (8, .5), (12, 1), (16, .7), (18.5, 0), (30, 0)]),
    day_anim("bld", "fill", [(6, "#3a3270"), (8, "#5e679c"), (17, "#5e679c"), (19.5, "#2a2050"), (21, "#151028"), (29, "#151028"), (30, "#3a3270")]),
    day_anim("sk0", "stop-color", [(6, "#3b3f8f"), (7.5, "#6fb0f0"), (9, "#4aa3f5"), (16, "#4aa3f5"), (18, "#5a78cf"), (19.5, "#3b2f73"), (21, "#141b4d"), (28.5, "#0f1640"), (29.5, "#2c2f74"), (30, "#3b3f8f")]),
    day_anim("sk1", "stop-color", [(6, "#ff9e7a"), (7.5, "#ffd9b0"), (9, "#bfe6ff"), (16, "#bfe6ff"), (18, "#ffb36b"), (19.5, "#ff6f61"), (21, "#3a2766"), (28.5, "#2a2160"), (29.5, "#b56a8a"), (30, "#ff9e7a")]),
    day_anim("cl", "opacity", [(6, 0), (8, 1), (17, 1), (19, 0), (30, 0)]),
]

# ---------- стена ----------
g.append(rect(0, 0, W, H, "#5d5088"))
g.append(rect(0, 44, W, 3, "#4f4377"))

# ---------- окно ----------
WX, WY, WWD, WHT = 6, 6, 34, 30
g.append(rect(WX - 1, WY - 1, WWD + 2, WHT + 2, "#3f3366"))
glass = [f'<rect x="{WX * U}" y="{WY * U}" width="{WWD * U}" height="{WHT * U}" fill="url(#sky)"/>']

# звёзды
stars = "".join(rect(WX + sx, WY + sy, 1, 1, "#fff6d6", "tw", f' style="animation-delay:{-i * 0.37:.2f}s"')
                for i, (sx, sy) in enumerate([(3, 3), (9, 6), (15, 2), (19, 9), (6, 11), (29, 12), (12, 14), (22, 4), (26, 7), (1, 8)]))
glass.append(f'<g class="nt">{stars}</g>')
css.append(".tw{animation:tw 2.2s steps(2) infinite}@keyframes tw{0%{opacity:1}100%{opacity:.15}}")

# солнце: дуга 06:00 → 20:00, по клетке
SUN = [".aaa.", "aaaaa", "aaaaA", "aaaAA", ".AAA."]
kf, N = [], 56
for i in range(N + 1):
    u = i / N
    x, y = round(WX + 1 + u * 27), round(WY + 27 - 25 * math.sin(math.pi * u))
    kf.append(f"{(u * 14 / 24) * 100:.3f}%{{transform:translate({x * U}px,{y * U}px);opacity:1}}")
kf.append(f"{14 / 24 * 100 + .01:.3f}%,100%{{transform:translate({(WX + 28) * U}px,{(WY + 27) * U}px);opacity:0}}")
css.append(f".sun{{animation:sun {D}s steps(1) infinite}}@keyframes sun{{{''.join(kf)}}}")
glass.append(sprite(SUN, 0, 0, "sun"))

# луна: дуга 20:00 → 06:00
MOON = [".lll.", "llllj", "llljj", "llljj", ".ljj."]
kf, N = [f"0%,{14 / 24 * 100 - .01:.3f}%{{transform:translate({(WX + 1) * U}px,{(WY + 27) * U}px);opacity:0}}"], 40
for i in range(N + 1):
    u = i / N
    x, y = round(WX + 1 + u * 27), round(WY + 27 - 22 * math.sin(math.pi * u))
    kf.append(f"{(14 + u * 10) / 24 * 100:.3f}%{{transform:translate({x * U}px,{y * U}px);opacity:1}}")
css.append(f".moon{{animation:moon {D}s steps(1) infinite}}@keyframes moon{{{''.join(kf)}}}")
glass.append(sprite(MOON, 0, 0, "moon"))

# облака днём
CLOUD = ["...vvv...", ".vvvvvvv.", "vvvvvvvvv", ".VVVVVVV."]
for i, (cy, shift, dur) in enumerate([(WY + 5, 0, 14), (WY + 11, -6, 18)]):
    dist = WWD + 12
    css.append(f".cx{i}{{animation:cx{i} {dur}s steps({dist}) infinite;animation-delay:{shift}s}}"
               f"@keyframes cx{i}{{0%{{transform:translateX(0)}}100%{{transform:translateX({dist * U}px)}}}}")
    glass.append(f'<g class="cl"><g class="cx{i}">{sprite(CLOUD, WX - 10, cy)}</g></g>')

# город: силуэты меняют цвет, окна горят ночью
city, lights, bx = [], [], WX
for bw, bh in [(5, 9), (4, 13), (6, 7), (3, 11), (5, 15), (4, 8), (7, 10)]:
    bw = min(bw, WX + WWD - bx)
    city.append(rect(bx, WY + WHT - bh, bw, bh, "#151028", "bld"))
    for wy in range(WY + WHT - bh + 2, WY + WHT - 1, 2):
        for wx in range(bx + 1, bx + bw - 1, 2):
            if random.random() < 0.45:
                lights.append(rect(wx, wy, 1, 1, "#ffd23f", "cw", f' style="animation-delay:{-random.random() * 6:.2f}s"'))
    bx += bw
    if bx >= WX + WWD:
        break
glass += city
glass.append(f'<g class="nt">{"".join(lights)}</g>')
css.append(".cw{animation:cw 6s steps(1) infinite}@keyframes cw{0%,70%{opacity:.95}71%,100%{opacity:.25}}")
g.append(f'<g clip-path="url(#glass)">{"".join(glass)}</g>')

# переплёт и подоконник
g.append(rect(WX + WWD // 2, WY, 1, WHT, "#3f3366"))
g.append(rect(WX, WY + WHT // 2, WWD, 1, "#3f3366"))
g.append(rect(WX - 2, WY + WHT + 1, WWD + 4, 2, "#6c5c9c"))

# луч солнца на стену и стол
g.append('<polygon class="beam" points="40,190 200,190 300,236 140,236" fill="#fff2c0" fill-opacity=".16"/>')

# постер с лапкой
g.append(rect(138, 8, 16, 15, "#3f3366"))
g.append(rect(139, 9, 14, 13, "#ffe9ef"))
g.append(sprite(["..U.U..", ".UU.UU.", "U.....U", "U.UUU.U", "..UUU..", ".UUUUU.", ".UUUUU."], 142, 11))

# ---------- стол ----------
g.append(rect(0, 47, W, 2, "#a07a5c"))
g.append(rect(0, 49, W, 15, "#7d5b45"))
g.append(rect(0, 49, W, 1, "#6a4b38"))

# ---------- монитор и код ----------
MX, MY, MW, MH = 72, 14, 60, 29
g.append(rect(MX, MY, MW, MH, "#2b2238"))
g.append(rect(MX + 2, MY + 2, MW - 4, MH - 4, "#0e1626"))
g.append(rect(MX + 2, MY + 2, MW - 4, 2, "#1b2740"))
for i, col in enumerate(["#ff4f86", "#ffd23f", "#2ebf8f"]):
    g.append(rect(MX + 3 + i * 2, MY + 2, 1, 1, col))
g.append(rect(MX + 27, MY + MH, 6, 4, "#3c3350"))
g.append(rect(MX + 22, MY + MH + 4, 16, 1, "#4a4068"))

TOK = ["#ff79c6", "#8be9fd", "#f1fa8c", "#c9c3e6", "#c9c3e6", "#50fa7b", "#bd93f9"]
lines = [
    [(0, 3, 0), (4, 5, 3), (10, 2, 3), (13, 6, 1)],
    [(2, 4, 0), (7, 7, 1), (15, 3, 3)],
    [(2, 2, 3), (5, 9, 2), (15, 2, 3)],
    [(4, 5, 1), (10, 4, 3), (15, 6, 6)],
    [(4, 3, 0), (8, 8, 3)],
    [(2, 1, 3)],
    [(0, 3, 0), (4, 6, 1), (11, 3, 3), (15, 8, 2)],
    [(2, 6, 3), (9, 5, 1), (15, 3, 3)],
    [(2, 1, 3)],
]
CX0, CY0 = MX + 4, MY + 6
code, covers = [], []
for i, ln in enumerate(lines):
    t0, t1 = 0.3 + i * 1.0, 1.15 + i * 1.0
    y = CY0 + i * 2
    for (x, w, c) in ln:
        code.append(rect(CX0 + x, y, w, 1, TOK[c]))
    n = max(x + w for x, w, _ in ln)
    covers.append(f'<g class="cv{i}">{rect(CX0, y, MW - 8, 1, "#0e1626")}{rect(CX0, y, 1, 1, "#e8e4ff", "cur")}</g>')
    steps = "".join(f"{pct(t0 + (t1 - t0) * k / n)}{{transform:translateX({k * U}px)}}" for k in range(1, n + 1))
    css.append(f".cv{i}{{animation:cv{i} {T}s steps(1) infinite}}@keyframes cv{i}{{0%,{pct(t0)}{{transform:translateX(0)}}{steps}100%{{transform:translateX({n * U}px)}}}}")
okY = CY0 + len(lines) * 2 + 1
code.append(f'<g class="ok">{rect(CX0, okY, 2, 1, "#50fa7b")}{rect(CX0 + 3, okY, 14, 1, "#50fa7b")}</g>')
css.append(f".ok{{animation:ok {T}s steps(1) infinite}}@keyframes ok{{0%,{pct(9.4)}{{opacity:0}}{pct(9.45)},100%{{opacity:1}}}}")
css.append(".cur{animation:cur .5s steps(1) infinite}@keyframes cur{0%{opacity:1}50%{opacity:0}}")
g.append(f'<g clip-path="url(#scr)">{"".join(code)}{"".join(covers)}</g>')

# зайчик на мониторе
BUN = [
    ".....wWWWw.....", "...wWWWWWWWw...", "..WWWWWWWWWWW..", ".wWWWWWWWWWWWw.",
    "wpWWWWWWWWWWWpw", "wpWWeWWWWWeWWpw", "wpWWeWWWWWeWWpw", "wpWcWWWeWWWcWpw",
    "wpWWWWWWWWWWWpw", ".wpwWWWWWWWwpw.", "..w.WWWWWWW.w..", "....ww...ww....",
]
BLINK = list(BUN)
BLINK[5] = "wpWWWWWWWWWWWpw"
BLINK[6] = "wpWeeWWWWWeeWpw"
g.append(sprite(BUN, MX + MW - 18, MY - 12))
g.append(sprite(BLINK, MX + MW - 18, MY - 12, "bb"))
css.append(".bb{animation:bb 3.4s steps(1) infinite}@keyframes bb{0%,90%{opacity:0}91%,96%{opacity:1}97%,100%{opacity:0}}")

# растение
g.append(sprite(["..g.g..", ".gGgGg.", "gGgGgGg", ".gGgGg.", "..fff..", ".fFfFf.", ".fFfFf.", "..fff.."], 150, 39))

# тостер и тост
g.append(sprite([".tttttt.", "tTTTTTTt", "tTTTTTTt", ".tTTTTt.", ".tTTTTt.", ".tTTTTt.", ".tTTTTt."], 137, 36, "toast"))
css.append(
    f".toast{{animation:pop {T}s steps(1) infinite}}@keyframes pop{{0%,{pct(9.5)}{{transform:translateY(0)}}"
    f"{pct(9.55)}{{transform:translateY(-{3 * U}px)}}{pct(9.62)}{{transform:translateY(-{6 * U}px)}}{pct(9.7)}{{transform:translateY(-{7 * U}px)}}"
    f"{pct(9.8)}{{transform:translateY(-{6 * U}px)}}{pct(9.88)}{{transform:translateY(-{4 * U}px)}}{pct(9.94)},100%{{transform:translateY(0)}}}}"
)
g.append(sprite(["..nnnnnnnnnnnn..", ".mmmmmmmmmmmmmm.", "mmmmmmmmmmmmmmmm", "mmMMMMMMMMMMMmmm",
                 "mmmmmmmmmmmmmmMm", "mmmmmmmmmmmmmmMm", ".MMMMMMMMMMMMMM."], 133, 40))

# кружка горячего чёрного кофе и пар
MUGX, MUGY = 40, 40
g.append(sprite([
    "uuuuuu..",
    "uqQqqu..",
    "uuuuuuuu",
    "UUUUUu.u",
    "uuuuuu.u",
    "uuuuuuuu",
    ".uuuu...",
], MUGX, MUGY))
for i, (dx, dl) in enumerate([(1, 0), (3, -.6), (4, -1.2)]):
    g.append(f'<g class="st" style="animation-delay:{dl}s">{rect(MUGX + dx, MUGY - 2, 1, 1, "#d9d2ea")}{rect(MUGX + dx + 1, MUGY - 3, 1, 1, "#d9d2ea")}{rect(MUGX + dx, MUGY - 4, 1, 1, "#d9d2ea")}</g>')
css.append(".st{animation:st 1.8s steps(4) infinite}@keyframes st{0%{transform:translateY(0);opacity:.95}100%{transform:translateY(-20px);opacity:0}}")

# клавиатура
g.append(rect(80, 46, 26, 2, "#3a3150"))
for kx in range(81, 105, 2):
    g.append(rect(kx, 46, 1, 1, "#6a5e8c"))
    g.append(rect(kx, 46, 1, 1, "#ffd23f", "key", f' style="animation-delay:{-random.random() * 1.2:.2f}s"'))
css.append(".key{opacity:0;animation:key 1.2s steps(1) infinite}@keyframes key{0%,85%{opacity:0}86%,100%{opacity:1}}")

# ---------- человек со спины ----------
HEAD = [
    "......XXXXXX......",
    "....BBHHHHHHBB....",
    "...BHHHhhHHHHHB...",
    "..BHHhhHHHHHHHHB..",
    "..BHhhHHHHHHHHHB..",
    ".XBHHHHHHHHHHHHBX.",
    "XBBbHHHHHHHHHHbBBX",
    "BBBbHHHHHHHHHHbBBB",
    "bBBbHHHHHHHHHHbBBb",
    ".bBbHHHHHHHHHHbBb.",
    "...sHHHHHHHHHHs...",
    "....HHHHHHHHHH....",
    ".....HHHHHHHH.....",
    "......SssssS......",
    "......ssssss......",
]
BODY = [
    "...........oooooooo...........",
    "........oooOOOOOOOOooo........",
    "......YYoOOOOOOOOOOOOoYY......",
    "....YYYYYoOOOOOOOOOOoYYYYY....",
    "...YYYYYYYooooooooooYYYYYYY...",
    "..YYYYYYYYYYYYYYYYYYYYYYYYYY..",
    ".yYYYYYYYYYYYYYYYYYYYYYYYYYYy.",
    ".yYYYYYYYYYYYYYYYYYYYYYYYYYYy.",
    "yyYYYYYYYYYYYYYYYYYYYYYYYYYYyy",
    "yyYYYYYYYYYYYYYYYYYYYYYYYYYYyy",
    "yyYYYYYYYYYYYYYYYYYYYYYYYYYYyy",
    "yyyYYYYYYYYYYYYYYYYYYYYYYYYyyy",
]
PX = 49
g.append(sprite(BODY, PX, 38))
g.append(sprite(["YY....", "YYYY..", ".yYYYs", "...yss"], PX + 28, 42, "armA"))
g.append(sprite(["YY....", "YYYY..", ".yYYY.", "...yYs", ".....s"], PX + 28, 42, "armB"))
g.append(sprite(["yy", "yYY", "yYY"], PX - 2, 44, "elb"))
css.append(".armA{animation:fa .36s steps(1) infinite}.armB{animation:fb .36s steps(1) infinite}"
           "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
           ".elb{animation:elb .36s steps(1) infinite;animation-delay:-.18s}@keyframes elb{0%{transform:translateY(0)}50%{transform:translateY(-5px)}}")
HX, HY = PX + 6, 24
rim = "".join(rect(HX + cx, HY + cy, 1, 1, "#58c7e0") for cx, cy in [(13, 2), (14, 3), (13, 10), (13, 11), (12, 12)])
g.append(f'<g class="head">{sprite(HEAD, HX, HY)}<g class="nt">{rim}</g></g>')
css.append(".head{animation:head 1.2s steps(1) infinite}@keyframes head{0%{transform:translateY(0)}50%{transform:translateY(5px)}}")
g.append(sprite([
    "..RRRRRRRRRRRRRRRRRRRRRR..", ".RLLLLLLLLLLLLLLLLLLLLLLR.",
    *["RLCCCCCCCCCCCCCCCCCCCCCCLR"] * 6,
    ".RLCCCCCCCCCCCCCCCCCCCCLR.", "..RRRRRRRRRRRRRRRRRRRRRR..",
    *["..........RRRRRR.........."] * 4,
], PX + 2, 50))

# ---------- ночь: затемнение комнаты (стёкла окна и экран не трогаем) ----------
def hole(x, y, w, h):
    return f"M{x * U},{y * U}h{w * U}v{h * U}h{-w * U}z"
half = WWD // 2
panes = [hole(WX, WY, half, WHT // 2), hole(WX + half + 1, WY, WWD - half - 1, WHT // 2),
         hole(WX, WY + WHT // 2 + 1, half, WHT - WHT // 2 - 1), hole(WX + half + 1, WY + WHT // 2 + 1, WWD - half - 1, WHT - WHT // 2 - 1)]
g.append(f'<path class="ov" fill-rule="evenodd" fill="#0a0720" d="M0,0H800V320H0z{"".join(panes)}{hole(MX + 2, MY + 2, MW - 4, MH - 4)}"/>')
g.append(f'<rect class="gl" x="{(MX - 14) * U}" y="{(MY - 6) * U}" width="{(MW + 28) * U}" height="{(MH + 20) * U}" fill="url(#glow)"/>')

# ---------- часы на подоконнике, идут в такт солнцу ----------
CLX, CLY = 10, 28
g.append(sprite(["....z.........z....."], CLX, CLY - 1))
g.append(sprite([".ZZZZZZZZZZZZZZZZZZZ."] + ["Zkkkkkkkkkkkkkkkkkkkz"] * 7 + [".zzzzzzzzzzzzzzzzzzz."], CLX, CLY))
FONT = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "001", "001", "001"],
    "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
}
LED = "#ff4f6d"
def digit(ch, x0, y0):
    return "".join(rect(x0 + c, y0 + r, 1, 1, LED) for r, row in enumerate(FONT[ch]) for c, b in enumerate(row) if b == "1")
times = []
for k in range(SLOTS):
    h, m = (6 + k // 2) % 24, 30 if k % 2 else 0
    times.append(f"{h:02d}{m:02d}")
DY = CLY + 2
POS = [CLX + 2, CLX + 6, CLX + 12, CLX + 16]
for pos in range(4):
    vals = sorted({t[pos] for t in times})
    for v in vals:
        name = f"d{pos}{v}"
        if len(vals) == 1:
            g.append(f'<g>{digit(v, POS[pos], DY)}</g>')
            continue
        kf, prev = [], None
        for k, t in enumerate(times):
            on = 1 if t[pos] == v else 0
            if on != prev:
                kf.append(f"{k / SLOTS * 100:.3f}%{{opacity:{on}}}")
                prev = on
        kf.append(f"100%{{opacity:{prev}}}")
        css.append(f".{name}{{animation:{name} {D}s steps(1) infinite}}@keyframes {name}{{{''.join(kf)}}}")
        g.append(f'<g class="{name}">{digit(v, POS[pos], DY)}</g>')
g.append(f'<g class="colon">{rect(CLX + 10, DY + 1, 1, 1, LED)}{rect(CLX + 10, DY + 3, 1, 1, LED)}</g>')
css.append(f".colon{{animation:colon {D / SLOTS}s steps(1) infinite}}@keyframes colon{{0%{{opacity:1}}50%{{opacity:.2}}}}")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="800" height="320" shape-rendering="crispEdges" role="img" aria-label="Пиксельная комната: Владимир со спины печатает код, за окном быстро сменяются день и ночь, часы на подоконнике идут в такт солнцу, рядом горячий кофе">
<title>Ночная смена — пиксельная анимация</title>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop class="sk0" offset="0" stop-color="#3b3f8f"/><stop class="sk1" offset="1" stop-color="#ff9e7a"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#5ef2ff" stop-opacity=".2"/><stop offset="1" stop-color="#5ef2ff" stop-opacity="0"/></radialGradient>
<clipPath id="glass"><rect x="{WX * U}" y="{WY * U}" width="{WWD * U}" height="{WHT * U}"/></clipPath>
<clipPath id="scr"><rect x="{(MX + 2) * U}" y="{(MY + 2) * U}" width="{(MW - 4) * U}" height="{(MH - 4) * U}"/></clipPath>
<clipPath id="card"><rect width="800" height="320" rx="24"/></clipPath>
<style>{"".join(css)}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
</defs>
<g clip-path="url(#card)">{"".join(g)}</g>
</svg>'''
OUT.write_text(svg, encoding="utf-8")
print(OUT, len(svg) // 1024, "KB")
