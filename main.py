#!/usr/bin/env python3
"""November 19, 2026 -- The Daily Globe.

Renders a one-page newspaper front page summing up the world news of
Thursday, November 19, 2026, and writes it to /output/entry.png.

Pure Python standard library: no network, no third-party packages.
Text is drawn with a hand-built 5x7 bitmap font, rendered at 2x
supersampling and box-downsampled to 1024x1024 for smooth edges.
The PNG encoder is written by hand (zlib + struct), so two runs of
this program produce byte-identical output.

Stories (all reported on 19 November 2026):
  LEAD  Trump, Xi and Putin hold their first three-way summit in
        Shenzhen, on the sidelines of the APEC forum.
  1     Ukraine strikes the Crimean Bridge for the third time in a week.
  2     Iran attacks Gulf states after a US strike on Qeshm Island.
  3     The International Court of Justice rules on the Myanmar
        Rohingya genocide case.
  4     Anthropic prices the biggest IPO in history: $81.3bn at $83 a
        share, debuting on Nasdaq today as ANT.
  5     The IAEA says North Korea has expanded uranium enrichment.
  6     Democrats nominate Hakeem Jeffries, set to be the first
        African-American Speaker of the US House.
  TICKER Voyager 1 nears one light-day from Earth; the EU approves
        its Indonesia trade pact; Australia sanctions Israeli
        settlements; India and Japan hold 2+2 defence talks.
"""

import os
import struct
import zlib

W = 1024
H = 1024
SS = 2  # supersampling factor

# ---------------------------------------------------------------- font --
# Each glyph is 7 rows of 5 bits, "1" = ink.  Uppercase only: the whole
# front page is set in capitals, like a poster.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# --------------------------------------------------------------- colours --
PAPER = (247, 240, 220)   # cream newsprint
GREEN = (14, 59, 44)      # deep green masthead
GREEN_DK = (8, 42, 31)    # darker green
GREEN_MD = (27, 84, 62)   # mid green panel tint
GOLD = (201, 162, 39)     # gold rules and accents
RED = (163, 51, 39)       # breaking / kicker red
INK = (26, 26, 26)        # body ink
PANEL = (255, 252, 242)   # pale panel paper
PANEL_TINT = (233, 236, 214)  # pale green-grey panel
CREAM = (247, 240, 220)
WHITE = (255, 255, 255)

# ------------------------------------------------------------ canvas ops --
# The canvas is a flat RGB bytearray at SSx resolution.
CW, CH = W * SS, H * SS
buf = bytearray([0]) * (CW * CH * 3)


def fill(x, y, w, h, color):
    """Fill a rectangle given in final (1024) coordinates."""
    x0, y0 = max(0, x * SS), max(0, y * SS)
    x1, y1 = min(CW, (x + w) * SS), min(CH, (y + h) * SS)
    r, g, b = color
    for yy in range(y0, y1):
        base = yy * CW * 3
        for xx in range(x0, x1):
            i = base + xx * 3
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b


def hline(x, y, w, color, thick=1):
    fill(x, y, w, thick, color)


def vline(x, y, h, color, thick=1):
    fill(x, y, thick, h, color)


def frame(x, y, w, h, color, thick=2):
    hline(x, y, w, color, thick)
    hline(x, y + h - thick, w, color, thick)
    vline(x, y, h, color, thick)
    vline(x + w - thick, y, h, color, thick)


def circle(cx, cy, r, color):
    """Filled circle, final coordinates."""
    x0, y0 = (cx - r) * SS, (cy - r) * SS
    x1, y1 = (cx + r) * SS, (cy + r) * SS
    rr = r * SS
    ccx, ccy = cx * SS, cy * SS
    cr, cg, cb = color
    for yy in range(max(0, y0), min(CH, y1)):
        dy = yy - ccy
        for xx in range(max(0, x0), min(CW, x1)):
            dx = xx - ccx
            if dx * dx + dy * dy <= rr * rr:
                i = (yy * CW + xx) * 3
                buf[i] = cr
                buf[i + 1] = cg
                buf[i + 2] = cb


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    """Draw uppercase text; x, y are final coords (top-left)."""
    text = text.upper()
    s = scale * SS
    r, g, b = color
    cx = x * SS
    cy = y * SS
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    px = cx + col * s
                    py = cy + row * s
                    for yy in range(py, py + s):
                        base = yy * CW * 3
                        for xx in range(px, px + s):
                            i = base + xx * 3
                            buf[i] = r
                            buf[i + 1] = g
                            buf[i + 2] = b
        cx += 6 * s
    return x + text_width(text, scale)


def draw_text_c(cx, y, text, scale, color):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    """Word-wrap text to lines fitting max_w pixels at the given scale."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, scale, color, max_w, leading):
    """Draw a wrapped paragraph; returns the y below the last line."""
    for line in wrap(text, scale, max_w):
        draw_text(x, y, line, scale, color)
        y += leading
    return y


# -------------------------------------------------------------- the page --
def build():
    fill(0, 0, W, H, PAPER)
    # Outer frame: deep green border with a gold hairline inside.
    frame(6, 6, W - 12, H - 12, GREEN, 6)
    frame(16, 16, W - 32, H - 32, GOLD, 1)

    # ---- Masthead: deep green band -------------------------------------
    fill(22, 22, W - 44, 112, GREEN)
    draw_text_c(W // 2, 36, "THE DAILY GLOBE", 7, CREAM)
    hline(52, 108, W - 104, GOLD, 2)
    draw_text_c(W // 2, 114, "THURSDAY, NOVEMBER 19, 2026", 2, GOLD)

    # ---- Lead panel: the Shenzhen summit --------------------------------
    lx, ly, lw, lh = 30, 146, W - 60, 252
    fill(lx, ly, lw, lh, PANEL)
    frame(lx, ly, lw, lh, GREEN, 3)
    draw_text(lx + 18, ly + 12, "LEAD STORY  \u2022  SHENZHEN, CHINA", 2, RED)
    hline(lx + 18, ly + 34, lw - 36, GOLD, 2)
    draw_text(lx + 18, ly + 44, "TRUMP, XI AND PUTIN", 5, GREEN_DK)
    draw_text(lx + 18, ly + 80, "MEET IN SHENZHEN", 5, GREEN_DK)
    draw_text(lx + 18, ly + 116, "FIRST THREE-WAY SUMMIT", 5, GREEN_DK)
    draw_para(
        lx + 18, ly + 158,
        "The presidents of the United States, China and Russia met on the "
        "sidelines of the APEC forum \u2014 the first time the three leaders "
        "have held talks together. Nuclear arms and the wars in Ukraine "
        "and the Middle East were on the table.",
        2, INK, lw - 36, 17)
    # Three flag chips: USA / CHINA / RUSSIA.
    chip_y = ly + lh - 34
    chips = [("USA", (178, 34, 52)), ("CHINA", (222, 41, 16)),
             ("RUSSIA", (0, 57, 166))]
    cx = lx + 18
    for label, col in chips:
        fill(cx, chip_y, 14, 14, col)
        frame(cx, chip_y, 14, 14, GREEN_DK, 1)
        draw_text(cx + 20, chip_y + 1, label, 2, GREEN_DK)
        cx += 20 + text_width(label, 2) + 26

    # ---- Story panels: two rows of three --------------------------------
    cols = [30, 352, 674]
    col_w = 320
    rows = [(410, 252), (674, 252)]
    stories = [
        ("WAR IN UKRAINE", "CRIMEAN BRIDGE HIT A THIRD TIME THIS WEEK",
         "Ukraine struck the bridge to Crimea again \u2014 the third attack "
         "in a week \u2014 as the summit talks opened. Traffic was halted "
         "while damage was assessed.", PANEL),
        ("GULF CRISIS", "IRAN HITS GULF STATES AFTER U.S. STRIKE",
         "Iran attacked Gulf states after U.S. jets struck Qeshm Island. "
         "A tanker was hit near Hormuz; its crew were reported safe.",
         PANEL_TINT),
        ("JUSTICE", "WORLD COURT TO RULE ON MYANMAR GENOCIDE CASE",
         "The International Court of Justice delivers its judgment today "
         "on claims Myanmar committed genocide against the Rohingya.",
         PANEL),
        ("BUSINESS", "ANTHROPIC'S $81BN IPO IS THE BIGGEST EVER",
         "The Claude maker priced shares at $83, raising a record $81.3 "
         "billion and valuing the AI lab at about $1.5 trillion. Trading "
         "starts today on Nasdaq as ANT.", PANEL_TINT),
        ("SECURITY", "NORTH KOREA EXPANDS URANIUM ENRICHMENT",
         "The IAEA says North Korea has expanded its uranium-enrichment "
         "work at Yongbyon, raising fresh fears over its nuclear "
         "programme.", PANEL),
        ("WASHINGTON", "JEFFRIES SET TO BE FIRST BLACK HOUSE SPEAKER",
         "Democrats nominated Hakeem Jeffries to lead the House \u2014 he "
         "is set to become the first African-American Speaker.",
         PANEL_TINT),
    ]
    for idx, (kicker, headline, body, bg) in enumerate(stories):
        row, col = divmod(idx, 3)
        px, py = cols[col], rows[row][0]
        ph = rows[row][1]
        fill(px, py, col_w, ph, bg)
        frame(px, py, col_w, ph, GREEN, 2)
        draw_text(px + 14, py + 12, kicker, 2, RED)
        hline(px + 14, py + 32, col_w - 28, GOLD, 2)
        y = py + 42
        for line in wrap(headline, 3, col_w - 28):
            draw_text(px + 14, y, line, 3, GREEN_DK)
            y += 26
        y += 4
        draw_para(px + 14, y, body, 2, INK, col_w - 28, 16)

    # ---- Ticker ----------------------------------------------------------
    ty = 938
    fill(22, ty, W - 44, 64, GREEN)
    draw_text(34, ty + 10, "ALSO TODAY:", 2, GOLD)
    draw_para(
        34, ty + 32,
        "VOYAGER 1 NEARS ONE LIGHT-DAY FROM EARTH \u2022 EU APPROVES "
        "INDONESIA TRADE PACT \u2022 AUSTRALIA SANCTIONS ISRAELI "
        "SETTLEMENTS \u2022 INDIA, JAPAN HOLD 2+2 DEFENCE TALKS",
        2, CREAM, W - 68, 16)


# ------------------------------------------------------------ png encode --
def encode_png(rgb_rows):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + row for row in rgb_rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def downsample():
    rows = []
    for y in range(H):
        row = bytearray()
        sy = y * SS
        for x in range(W):
            sx = x * SS
            r = g = b = 0
            for dy in range(SS):
                base = (sy + dy) * CW * 3 + sx * 3
                for dx in range(SS):
                    i = base + dx * 3
                    r += buf[i]
                    g += buf[i + 1]
                    b += buf[i + 2]
            n = SS * SS
            row += bytes((r // n, g // n, b // n))
        rows.append(bytes(row))
    return rows


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(downsample())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (os.path.join(out_dir, "entry.png"),
                                   len(data)))


if __name__ == "__main__":
    main()
