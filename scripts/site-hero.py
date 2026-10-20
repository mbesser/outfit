#!/usr/bin/env python3
"""Draws site/hero.svg: a little agent trying on harnesses from a rolling rack. Standard library only.

Run from the repository root: python3 scripts/site-hero.py

The picture is 1-bit pixel art, drawn here as ASCII sprites ('#' ink, '.' paper, 'x' checker,
'=' stripes, ':' dots, ' ' see-through) and written out as SVG paths. The animation is CSS inside
the SVG, so the page loads one image and its CSP (img-src 'self') still holds.

One slot of the loop: the rack rolls one hanger along, the command types, the outfit drops onto
the agent, the agent hops and says something, and the outfit goes back up. Six outfits, six slots.
A visitor who asks for less motion gets one still frame: the transform and opacity attributes.
"""
import os

INK, PAPER = "#000", "#fff"
HIDDEN = ' opacity="0"'       # hidden until the animation shows it
W = 176
P = 3.2                      # seconds per slot
SLOT = 44                    # pixels between hangers
CENTER = 88                  # where the agent stands
RAIL = 3
HANG = 12                    # first row under a hanger's bar
SCALE = 4                    # the image's own size, in CSS pixels per pixel
STATIC = "yolo"              # the outfit worn in the still frame

# One slot, as fractions of P.
MOVE = (0.00, 0.12)          # rack rolls one hanger along
TYPE = (0.12, 0.30)          # command types
DROP = (0.32, 0.40)          # outfit drops on
HOPS = (0.42, 0.46, 0.50, 0.54, 0.58)
HAPPY = (0.42, 0.80)
SAY = (0.44, 0.82)
RISE = (0.84, 0.92)          # outfit goes back up; the command clears at the end


def pattern(ch, x, y):
    """The colour of one pixel, or None where the sprite is see-through."""
    if ch == "#":
        return INK
    if ch == ".":
        return PAPER
    if ch == "x":
        return INK if (x + y) % 2 == 0 else PAPER
    if ch == "=":
        return INK if y % 2 == 0 else PAPER
    if ch == ":":
        return INK if x % 2 == 0 and y % 2 == 0 else PAPER
    return None


class Sprite:
    """Pixels keyed by (x, y); later strokes paint over earlier ones."""

    def __init__(self):
        self.px = {}

    def rows(self, top, rows, left=0):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                c = pattern(ch, left + dx, top + dy)
                if c:
                    self.px[(left + dx, top + dy)] = c
        return self

    def sym(self, top, halves):
        """Rows given as their left half, centre column last; the right half is the mirror."""
        return self.rows(top, [h + h[:-1][::-1] for h in halves])

    def dot(self, x, y, ch):
        self.px[(x, y)] = pattern(ch, x, y)
        return self

    def top(self):
        return min(y for _, y in self.px)

    def bottom(self):
        return max(y for _, y in self.px)

    def svg(self, cls=None, hidden=False):
        out = []
        for colour in (PAPER, INK):
            d = []
            for y in sorted({y for _, y in self.px}):
                xs = sorted(x for (x, yy), c in self.px.items() if yy == y and c == colour)
                i = 0
                while i < len(xs):
                    j = i
                    while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
                        j += 1
                    w = j - i + 1
                    d.append(f"M{xs[i]} {y}h{w}v1h-{w}z")
                    i = j + 1
            if d:
                out.append(f'<path fill="{colour}" d="{"".join(d)}"/>')
        body = "".join(out)
        return f'<g class="{cls}"{HIDDEN if hidden else ""}>{body}</g>' if cls else body


# Everything the agent wears is drawn on the agent's own 29-column grid: column 14 is its
# middle, row 0 the tip of its antenna.


def agent():
    return Sprite().sym(0, [
        "             ##",
        "            #..",
        "             ##",
        "              #",
        "              #",
        "        #######",
        "       #.......",
        "      #..######",
        "      #.#......",
        "      #.#..##..",
        "      #.#..##..",
        "      #.#......",
        "      #.#...#..",
        "      #.#....##",
        "      #.#......",
        "      #..######",
        "       #.......",
        "        #######",
        "           #...",
        "        #######",
        "       #.......",
        "     ###.......",
        "    #..#.......",
        "     ###.......",
        "       #.......",
        "       #.......",
        "        #######",
        "          ##   ",
        "         ####  ",
    ])


def blink():
    return Sprite().rows(9, ["           ..   ..", "           ##   ##"])


def happy():
    return Sprite().rows(9, [
        "          .##. .##.",
        "          #..# #..#",
        "",
        "            #####",
        "             ###",
    ])


def antenna_light():
    return Sprite().rows(1, ["             ###"])


# An outfit is a list of pieces. On the rack they hang stacked under the hanger; on the agent
# each piece lands where it belongs.

def strict():
    hat = Sprite().sym(1, [
        "           ####",
        "         ######",
        "        ##.####",
        "        #######",
        "      #########",
    ]).dot(11, 2, ".").dot(17, 3, "#")
    straps = Sprite().sym(19, [
        "          ##   ",
        "          ##   ",
        "          #####",
        "        #####.#",
        "          #####",
        "          ##   ",
        "      #########",
        "          ##   ",
    ])
    return [hat, straps]


def yolo():
    shades = Sprite().sym(8, [
        "         ######",
        "          #### ",
        "           ### ",
    ]).dot(11, 9, ".").dot(16, 9, ".")
    pack = Sprite().sym(11, [
        "  ##           ",
        " #..#          ",
        " #xx#          ",
        " #xx#          ",
        " #xx#          ",
        " #xx#          ",
        " #xx#          ",
        " #xx#          ",
        " #..######     ",
        " ####    #  ###",
        "  ##     #####.",
        "         #  ###",
        "         #     ",
        "         #     ",
        "         #     ",
        "         #     ",
    ])
    return [shades, pack]


def flame(frame):
    rows = [["#..#", "#..#", " ## "], ["#..#", " ## ", ""]][frame]
    return Sprite().sym(22, [(" " + r).ljust(15) for r in rows])


def review():
    monocle = Sprite().rows(8, [
        "                ##",
        "               #  #",
        "               #  #",
        "                ##",
        "                   #",
        "",
        "                   #",
    ])
    tie = Sprite().sym(18, [
        "          #    ",
        "          ##   ",
        "          ###.#",
        "          ##   ",
        "          #    ",
    ]).sym(19, ["        ==     "] * 8)
    return [monocle, tie]


def tests():
    return [Sprite().sym(19, [
        "       ###     ",
        "       #xx#    ",
        "       #xxx#   ",
        "       #xxxx#  ",
        "       #xxxxx# ",
        "       #xxxxxx#",
        "       #xxxxxxx",
        "       ########",
    ]).rows(18, [
        "  ##  ",
        "######",
        "#....#",
        "#.##.#",
        "#....#",
        "#.##.#",
        "#....#",
        "######",
    ])]


def mine():
    hat = Sprite().sym(-3, [
        "             ##",
        "             ##",
        "             #:",
        "            #::",
        "           #:::",
        "          #::::",
        "          #::::",
        "         #:::::",
        "        #######",
    ])
    heart = Sprite().sym(19, [
        "         #     ",
        "         #  ## ",
        "         # ####",
        "         ######",
        "         #  ###",
        "         #   ##",
        "         #    #",
        "         #     ",
    ]).dot(12, 21, ".")
    return [hat, heart]


def base():
    return [Sprite().sym(19, [
        "         #.#   ",
        "         #.#   ",
        "       ########",
        "       #....#.#",
        "       ########",
        "         #.#   ",
        "         #.#   ",
        "         #.#   ",
    ])]


OUTFITS = [
    ("strict", strict(), "tests first. always."),
    ("yolo", yolo(), "ship it!"),
    ("review", review(), "nit: naming."),
    ("tests", tests(), "red, green, refactor."),
    ("mine", mine(), "just how I like it."),
    ("base", base(), "exactly what's committed."),
]
N = len(OUTFITS)
CYCLE = round(P * N, 6)      # 19.2, not 19.200000000000003, in the CSS


def hung(pieces):
    """Each piece's offset on the rack: stacked under the hanger, one pixel apart."""
    out, top = [], HANG
    for s in pieces:
        out.append(top - s.top())
        top += s.bottom() - s.top() + 2
    return out


# The agent stands just below the longest outfit on the rack, so nothing passes through its head.
AGENT_Y = max(off + s.bottom() for _, pieces, _ in OUTFITS for off, s in zip(hung(pieces), pieces)) + 3
GROUND = AGENT_Y + 29
H = GROUND + 5


def hanger():
    return Sprite().rows(RAIL - 1, [
        "    ###  ",
        "   #   # ",
        "   #     ",
        "    #    ",
        "    #    ",
        "   # #   ",
        "  #   #  ",
        " #     # ",
        "#########",
    ], left=10)


def sparkle():
    return Sprite().rows(0, ["  #  ", "  #  ", "## ##", "  #  ", "  #  "])


# --- timing ---------------------------------------------------------------------------------

def keyframes(name, stops):
    """stops: (time 0..1, declarations, timing function of the segment that starts there)."""
    body = []
    for t, decl, fn in stops:
        f = f"animation-timing-function:{fn};" if fn else ""
        body.append(f"{t * 100:.4g}%{{{decl}{f}}}")
    return f"@keyframes {name}{{{''.join(body)}}}"


def tr(x, y):
    return f"transform:translate({x}px,{y}px);"


def blinks(name, spans):
    """Visible only inside the given (start, end) spans."""
    stops = [(0, "opacity:0;", "step-end")]
    for a, b in spans:
        stops += [(a, "opacity:1;", "step-end"), (b, "opacity:0;", "step-end")]
    return keyframes(name, stops + [(1, "opacity:0;", None)])


def turn(f):
    """Fraction f of the slot an outfit spends over the agent (its third slot), as a fraction of its cycle."""
    return (2 + f) / N


def slot_x(k, f):
    """The left edge of an outfit's grid in slot k at fraction f of that slot."""
    a, b = MOVE
    moved = 0 if f <= a else SLOT if f >= b else round(SLOT * (f - a) / (b - a))
    return CENTER + SLOT * (3 - k) - 14 - moved


def rack_frames():
    stops = []
    for k in range(N):
        stops.append(((k + MOVE[0]) / N, tr(slot_x(k, 0), 0), f"steps({SLOT})"))
        stops.append(((k + MOVE[1]) / N, tr(slot_x(k, 1), 0), None))
    return keyframes("rack", stops + [(1, tr(slot_x(N - 1, 1), 0), None)])


def drop_frames(name, up):
    down = AGENT_Y
    dist = down - up
    stops = [(0, tr(0, up), None), (turn(DROP[0]), tr(0, up), f"steps({dist})"), (turn(DROP[1]), tr(0, down), None)]
    for n, f in enumerate(HOPS):
        stops.append((turn(f), tr(0, down - 2 * (n % 2)), "steps(2)"))
    stops += [(turn(RISE[0]), tr(0, down), f"steps({dist})"), (turn(RISE[1]), tr(0, up), None), (1, tr(0, up), None)]
    return keyframes(name, stops)


def hop_frames():
    stops = [(0, tr(CENTER - 14, AGENT_Y), None)]
    for n, f in enumerate(HOPS):
        stops.append((f, tr(CENTER - 14, AGENT_Y - 2 * (n % 2)), "steps(2)"))
    return keyframes("hop", stops + [(1, tr(CENTER - 14, AGENT_Y), None)])


def delay(i):
    """Outfit i is over the agent in slot i of the loop."""
    return f"{-((2 - i) % N) * P:g}s"


# --- the scene ------------------------------------------------------------------------------

FONT = "Monaco,Menlo,'Lucida Console','DejaVu Sans Mono','Courier New',monospace"
CH = 2.4                     # one character's advance at font-size 4
STILL = [name for name, _, _ in OUTFITS].index(STATIC)


def rect(x, y, w, h, fill=INK, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<rect{c} x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def terminal():
    """A tiny window where each `outfit use` types itself."""
    x, y, w, h = 3, AGENT_Y + 7, 54, 17
    out = [rect(x + 1, y + 1, w, h), rect(x, y, w, h), rect(x + 1, y + 1, w - 2, h - 2, PAPER), rect(x, y + 6, w, 1)]
    out += [rect(x + 8, r, w - 11, 1) for r in (y + 2, y + 4)]
    out += [rect(x + 3, y + 2, 4, 3), rect(x + 4, y + 3, 2, 1, PAPER)]
    tx, ty = x + 3, y + 13
    # A paper cover slides off each command one character at a time; its left edge is the cursor.
    # The screen clips it, so a cover parked past the text never paints over the window's frame.
    out.append(f'<clipPath id="screen">{rect(x + 1, y + 7, w - 2, h - 8)}</clipPath><g clip-path="url(#screen)">')
    frames = []
    for i, (name, _, _) in enumerate(OUTFITS):
        cmd = f"$ outfit use {name}"
        reach = round(CH * len(cmd), 2)
        out.append(f'<g class="cmd c{i}"{"" if i == STILL else HIDDEN}><text x="{tx}" y="{ty}">{cmd}</text>'
                   f'<g class="cover t{i}" transform="translate({reach} 0)">{rect(tx, ty - 4, w - 6, 5, PAPER)}'
                   f'{rect(tx, ty - 4, CH, 5, cls="cursor")}</g></g>')
        frames.append(f".t{i}{{animation:type{i} {P}s infinite}}")
        frames.append(keyframes(f"type{i}", [
            (0, tr(0, 0), "step-end"), (TYPE[0], tr(0, 0), f"steps({len(cmd)})"),
            (TYPE[1], tr(reach, 0), "step-end"), (RISE[1], tr(0, 0), None), (1, tr(0, 0), None)]))
    out.append("</g>")
    return "".join(out), "".join(frames)


def bubble(i, text):
    x, y, w = 105, AGENT_Y + 2, round(len(text) * CH) + 6
    s = Sprite().rows(y, ["#" * (w - 2)], left=x + 1).rows(y + 10, ["#" * (w - 2)], left=x + 1)
    for r in range(y + 1, y + 10):
        s.rows(r, ["#" + "." * (w - 2) + "#"], left=x)
    s.rows(y + 4, ["   .", "  #.", " #..", "####"], left=x - 3)
    return (f'<g class="say b{i}"{"" if i == STILL else HIDDEN}>{s.svg()}'
            f'<text x="{x + 3}" y="{y + 7}">{text.replace("&", "&amp;")}</text></g>')


def ground():
    s = Sprite().rows(GROUND, ["#" * W])
    for r in range(GROUND + 1, H):
        s.rows(r, [":" * W])
    return s.rows(GROUND + 1, ["x" * 20], left=CENTER - 10).rows(GROUND + 2, ["x" * 14], left=CENTER - 7)


def rail():
    s = Sprite().rows(RAIL, ["#" * W])
    for x in (12, W - 13):
        s.rows(0, ["#.#", "#.#", "###"], left=x - 1)
    return s


def build():
    term, typing = terminal()
    css = [
        f"text{{font:4px {FONT};fill:{INK}}}",
        f".rk{{animation:rack {CYCLE}s infinite}}",
        f".agent{{animation:hop {P}s infinite}}",
        f".happy{{animation:happy {P}s infinite}}",
        f".spark{{animation:spark {P}s infinite}}",
        ".spark+.spark{animation-name:spark2}",
        ".blink{animation:blink 4.3s infinite}",
        ".light{animation:light 1.6s infinite}",
        f".cmd{{animation:cmd {CYCLE}s infinite}}",
        f".say{{animation:say {CYCLE}s infinite}}",
        f".fire{{animation:fire {CYCLE}s infinite}}",
        ".flame{animation:flame .3s infinite}",
        ".flame+.flame{animation-name:flame2}",
        ".cursor{animation:cursor .8s infinite}",
        rack_frames(), hop_frames(), typing,
        blinks("happy", [HAPPY]),
        blinks("cmd", [(turn(TYPE[0]), turn(RISE[1]))]),
        blinks("say", [(turn(SAY[0]), turn(SAY[1]))]),
        blinks("fire", [(turn(DROP[1]), turn(RISE[0]))]),
        blinks("spark", [(HAPPY[0], 0.50), (0.58, 0.66)]),
        blinks("spark2", [(0.46, 0.54), (0.62, 0.70)]),
        blinks("blink", [(0.94, 0.97)]),
        blinks("light", [(0.5, 1)]),
        blinks("flame", [(0, 0.5)]),
        blinks("flame2", [(0.5, 1)]),
        blinks("cursor", [(0, 0.5)]),
    ]

    scene = [rect(0, 0, W, H, PAPER), ground().svg(), rail().svg(), term]
    a = agent().svg() + blink().svg("blink", hidden=True) + antenna_light().svg("light") + happy().svg("happy")
    scene.append(f'<g class="agent" transform="translate({CENTER - 14} {AGENT_Y})">{a}</g>')
    hang = hanger().svg()
    for i, (name, pieces, _) in enumerate(OUTFITS):
        css.append(f".h{i},.c{i},.b{i},.f{i}{{animation-delay:{delay(i)}}}")
        k = (STILL + 2 - i) % N
        groups = []
        for p, (up, s) in enumerate(zip(hung(pieces), pieces)):
            css.append(f".d{i}{p}{{animation:d{i}{p} {CYCLE}s infinite {delay(i)}}}")
            css.append(drop_frames(f"d{i}{p}", up))
            extra = ""
            if name == "yolo" and p == 1:
                extra = (f'<g class="fire f{i}"{"" if i == STILL else HIDDEN}>'
                         f'{flame(0).svg("flame")}{flame(1).svg("flame", hidden=True)}</g>')
            groups.append(f'<g class="d{i}{p}" transform="translate(0 {AGENT_Y if i == STILL else up})">'
                          f'{s.svg()}{extra}</g>')
        scene.append(f'<g class="rk h{i}" transform="translate({slot_x(k, 1)} 0)">{hang}{"".join(groups)}</g>')
    scene += [bubble(i, said) for i, (_, _, said) in enumerate(OUTFITS)]
    scene.append(f'<g class="spark" transform="translate({CENTER - 22} {AGENT_Y + 6})">{sparkle().svg()}</g>')
    scene.append(f'<g class="spark" transform="translate({CENTER + 11} {AGENT_Y - 5})">{sparkle().svg()}</g>')
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * SCALE}" '
            f'height="{H * SCALE}" shape-rendering="crispEdges">'
            "<title>An illustration: an agent tries on harnesses from a rolling rack, one outfit at a time.</title>"
            f"<style>{''.join(css)}</style>{''.join(scene)}</svg>\n")


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "site", "hero.svg"), "w", encoding="utf-8") as f:
        f.write(build())
    print(f"wrote site/hero.svg ({W}x{H})")
