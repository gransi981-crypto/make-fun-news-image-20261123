"""Draw the front page for Monday 23 November 2026.

A single-page newspaper built from rectangles: a masthead, one lead
story with a market chart, two mid stories, three short briefs and a
two-line ticker. Everything is drawn with Pillow; no network, no
randomness, no clock — the same input always produces the same PNG
bytes.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (163, 18, 18)
BLUE = (26, 58, 107)
GREY = (90, 86, 76)
BAND = (20, 20, 20)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


class Flow:
    """Word-wrap helper bound to one draw context."""

    def __init__(self, draw):
        self.d = draw

    def wrap(self, text, fnt, width):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.d.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def para(self, text, fnt, box, leading, fill=INK, align="left"):
        """Draw wrapped text inside (x, y, w); return y after last line."""
        x, y, w = box
        for line in self.wrap(text, fnt, w):
            if align == "center":
                lx = x + (w - self.d.textlength(line, font=fnt)) / 2
            else:
                lx = x
            self.d.text((lx, y), line, font=fnt, fill=fill)
            y += leading
        return y

    def fit_headline(self, text, fnt, box, leading, max_lines=2):
        """Headline wrapped to at most max_lines; shrink font until it fits."""
        x, y, w = box
        size = fnt.size
        lines = self.wrap(text, fnt, w)
        while len(lines) > max_lines and size > 14:
            size -= 2
            fnt = ImageFont.truetype(fnt.path, size)
            lines = self.wrap(text, fnt, w)
        for line in lines[:max_lines]:
            self.d.text((x, y), line, font=fnt, fill=INK)
            y += leading
        return y


def hline(d, x0, x1, y, width=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(d, x, y0, y1, width=1, fill=GREY):
    d.line([(x, y0), (x, y1)], fill=fill, width=width)


def draw_masthead(d, fl):
    d.text((512, 26), "THE WORLD", font=font(SERIF_B, 96),
           fill=INK, anchor="ma")
    fl.para("MONDAY, 23 NOVEMBER 2026  ·  ONE DAY, ONE PAGE",
            font(SANS, 19), (36, 138, 952), 24, fill=GREY, align="center")
    hline(d, 36, 988, 168, width=3)


def draw_market_chart(d, x, y, w, h):
    """Falling-line chart for the Nikkei slide, with a red axis."""
    d.rectangle([x, y, x + w, y + h], outline=GREY, width=1)
    for i in range(1, 4):
        gy = y + h * i / 4
        d.line([(x, gy), (x + w, gy)], fill=(210, 205, 190), width=1)
    pts = []
    n = 24
    for i in range(n):
        px = x + 12 + (w - 24) * i / (n - 1)
        frac = i / (n - 1)
        drop = frac * 0.72 - (0.10 if 0.60 < frac < 0.72 else 0)
        py = y + 14 + (h - 28) * drop
        pts.append((px, py))
    d.line(pts, fill=RED, width=4)
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=RED)
    d.text((x + 8, y + 6), "NIKKEI 225", font=font(SANS_B, 17), fill=INK)
    d.text((x + w - 8, y + h - 10), "-5.06%", font=font(SANS_B, 34),
           fill=RED, anchor="rb")


def draw_seat_bar(d, x, y, w, h):
    """House seats: Democrats 258 of 435."""
    total, dem = 435, 258
    split = w * dem / total
    d.rectangle([x, y, x + split, y + h], fill=BLUE)
    d.rectangle([x + split, y, x + w, y + h], fill=(200, 196, 186))
    d.text((x + 6, y + h + 6), "DEM 258", font=font(SANS_B, 17), fill=BLUE)
    d.text((x + w - 6, y + h + 6), "GOP 177", font=font(SANS_B, 17),
           fill=GREY, anchor="ra")


def draw_lead(d, fl):
    fl.para("MARKETS", font(SANS_B, 20), (36, 184, 600), 24, fill=RED)
    fl.fit_headline("AI sell-off hits Asia as the tech rout spreads",
                    font(SERIF_B, 52), (36, 212, 600), 58, max_lines=2)
    fl.para("Japan's Nikkei falls 5.06% on Monday and Hong Kong "
            "stocks touch a 19-month low, as the slide in US "
            "artificial-intelligence shares reaches Asia. Taiwan "
            "shares swing 1,578 points in a day.",
            font(SERIF, 22), (36, 338, 600), 29)
    draw_market_chart(d, 668, 188, 320, 240)
    fl.para("TOKYO  ·  HONG KONG  ·  TAIPEI",
            font(SANS, 16), (668, 440, 320), 20, fill=GREY, align="center")
    hline(d, 36, 988, 470, width=2)


def draw_duo(d, fl):
    # left column: US House
    fl.para("UNITED STATES", font(SANS_B, 18), (36, 486, 460), 22, fill=RED)
    fl.fit_headline("Democrats win biggest House majority since 1992",
                    font(SERIF_B, 30), (36, 510, 460), 35, max_lines=2)
    draw_seat_bar(d, 36, 590, 460, 22)
    fl.para("Democrats clinch at least 258 House seats after "
            "Chuck Hubbard beats Republican Virginia Foxx in a "
            "North Carolina recount.",
            font(SERIF, 20), (36, 642, 460), 25)
    # right column: Korea exports
    vline(d, 512, 486, 726)
    fl.para("TRADE", font(SANS_B, 18), (536, 486, 452), 22, fill=RED)
    fl.fit_headline("Seoul exports pass $1 trillion for the first time",
                    font(SERIF_B, 30), (536, 510, 452), 35, max_lines=2)
    d.text((536, 586), "$1T", font=font(SERIF_B, 44), fill=BLUE)
    fl.para("Annual exports top $1 trillion on AI chip demand — "
            "only the fourth economy ever to reach the mark.",
            font(SERIF, 20), (536, 646, 452), 25)
    hline(d, 36, 988, 732, width=2)


def draw_trio(d, fl):
    cols = [
        (36, "SCIENCE", "Riemann proof checks pass 62%",
         "Independent verification of the Claude-assisted "
         "claim reaches 109,717 of 175,187 Lean modules."),
        (352, "DISASTER", "M 6.5 quake hits Vanuatu",
         "A magnitude 6.5 earthquake strikes the Vanuatu "
         "region at 02:40 UTC, 598 km deep. No tsunami "
         "warning is issued."),
        (668, "EDUCATION", "Minister quits over AI exam cheating",
         "South Korea's education minister resigns after "
         "chaos over measures against AI-assisted cheating "
         "on the college entrance exam."),
    ]
    for x, kick, head, body in cols:
        fl.para(kick, font(SANS_B, 17), (x, 748, 300), 21, fill=RED)
        fl.fit_headline(head, font(SERIF_B, 26), (x, 770, 300), 28,
                        max_lines=2)
        fl.para(body, font(SERIF, 18), (x, 836, 300), 22)
    vline(d, 336, 748, 928)
    vline(d, 652, 748, 928)
    hline(d, 36, 988, 940, width=2)


def draw_ticker(d):
    d.rectangle([36, 950, 988, 1014], fill=BAND)
    lines = [
        "LIBYA REPORTS SECOND DRONE ATTACK ON SHIPS  •  "
        "ISRAEL COALITION TALKS FAIL  •  "
        "BOY, 7, PULLED ALIVE FROM DYMER RUBBLE",
        "GAZA WAR LEAVES WIDESPREAD CONTAMINATION, EXPERTS SAY  •  "
        "US ARMY TO DETONATE UNSTABLE EXPLOSIVES IN IOWA  •  "
        "MAN RESCUED AFTER 11 DAYS IN THE AMAZON",
    ]
    size = 13
    fnt = font(SANS_B, size)
    while max(d.textlength(t, font=fnt) for t in lines) > 940 and size > 8:
        size -= 1
        fnt = ImageFont.truetype(SANS_B, size)
    d.text((512, 968), lines[0], font=fnt, fill=(247, 243, 232), anchor="ma")
    d.text((512, 992), lines[1], font=fnt, fill=(247, 243, 232), anchor="ma")


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    fl = Flow(d)
    draw_masthead(d, fl)
    draw_lead(d, fl)
    draw_duo(d, fl)
    draw_trio(d, fl)
    draw_ticker(d)
    img.save(path, format="PNG", optimize=True)


if __name__ == "__main__":
    import sys
    render(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
