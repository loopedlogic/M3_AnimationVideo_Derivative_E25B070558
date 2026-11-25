"""Render a 1080p narrated M3 animation with Pillow and FFmpeg."""
import argparse
import math
import os
from pathlib import Path
import subprocess
import tempfile
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

from scenes import BEATS, SCENES

WIDTH, HEIGHT, FPS = 1920, 1080, 24
BG, PANEL, EDGE = "#101923", "#172432", "#2c4254"
WHITE, MUTED = "#f3f5ec", "#a9bac9"
BLUE, ORANGE, PURPLE, GREEN = "#79d9ff", "#ffb366", "#d1afff", "#9deaaf"
FONT_DIR = Path(os.environ.get("M3_FONT_DIR", "/usr/share/fonts/truetype/dejavu"))
REFERENCE = "OpenStax, Calculus Volume 1, §3.1 · Defining the Derivative"

STEPS = [
    ("Substitute", "[(2 + h)² − 4] / h"),
    ("Expand", "[4 + 4h + h² − 4] / h"),
    ("Factor", "[4h + h²] / h = h(4 + h) / h"),
    ("Cancel  h ≠ 0", "4 + h"),
    ("Take the limit", "f′(2) = lim h→0 (4 + h) = 4"),
]
ALGEBRA = ("substitute", "expand", "factor", "cancel", "evaluate")
TAKEAWAYS = [
    ("Average change", "A secant joins two distinct points.", ORANGE),
    ("Instantaneous change", "The derivative is the limit of secant slopes.", GREEN),
    ("At x = 2", "The tangent slope for f(x) = x² is 4.", BLUE),
]


@lru_cache(maxsize=None)
def font(size, style="regular"):
    files = {
        "regular": "DejaVuSans.ttf",
        "bold": "DejaVuSans-Bold.ttf",
        "serif": "DejaVuSerif.ttf",
        "mono": "DejaVuSansMono.ttf",
    }
    return ImageFont.truetype(str(FONT_DIR / files[style]), size)


def label(draw, xy, content, size=32, color=WHITE, style="regular", **kwargs):
    draw.text(xy, content, font=font(size, style), fill=color, **kwargs)


def panel(draw, box, fill=PANEL, outline=EDGE, radius=26):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def lines(draw, x, y, values, size=30, gap=52, color=WHITE):
    for row, value in enumerate(values):
        label(draw, (x, y + row * gap), value, size, color)


def fade(color, amount, base=PANEL):
    return tuple(round(int(base[i:i+2], 16) * (1-amount) + int(color[i:i+2], 16) * amount)
                 for i in (1, 3, 5))


def number(value, places=2):
    formatted = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return (formatted if formatted != "-0" else "0").replace("-", "−")


def chart(draw, box, h=None, tangent=False, triangle=False, zoom=False, compare=False):
    left, top, right, bottom = box
    if zoom:
        xmin, xmax, ymin, ymax = 1.94, 2.20, 3.72, 4.84
        xticks, yticks = [1.95, 2, 2.05, 2.1, 2.15, 2.2], [3.8, 4, 4.2, 4.4, 4.6, 4.8]
    else:
        xmin, xmax, ymin, ymax = -0.18, 3.65, -0.9, 12.6
        xticks, yticks = [0, 1, 2, 3], [0, 2, 4, 6, 8, 10, 12]

    def xy(x, y):
        return (left + (x-xmin)/(xmax-xmin)*(right-left),
                bottom - (y-ymin)/(ymax-ymin)*(bottom-top))

    for x in xticks:
        px, _ = xy(x, ymin)
        draw.line((px, top, px, bottom), fill=EDGE, width=2)
        label(draw, (px, bottom + 14), number(x), 23, MUTED, anchor="mt")
    for y in yticks:
        _, py = xy(xmin, y)
        draw.line((left, py, right, py), fill=EDGE, width=2)
        label(draw, (left - 15, py), number(y), 23, MUTED, anchor="rm")
    axis_x = xy(0, ymin)[0] if not zoom else left
    axis_y = xy(xmin, 0)[1] if not zoom else bottom
    draw.line((axis_x, top, axis_x, bottom), fill=MUTED, width=2)
    draw.line((left, axis_y, right, axis_y), fill=MUTED, width=2)
    label(draw, (right + 11, axis_y - 22), "x", 26, MUTED)
    label(draw, (axis_x - 9, top - 36), "y", 26, MUTED)

    xs = [xmin + (xmax-xmin)*i/300 for i in range(301)]
    curve = [xy(x, x*x) for x in xs if ymin <= x*x <= ymax]
    draw.line(curve, fill=BLUE, width=7, joint="curve")

    def line_through_p(slope, color):
        start = max(xmin, 2 + (ymin-4)/slope)
        end = min(xmax, 2 + (ymax-4)/slope)
        draw.line((xy(start, 4 + slope*(start-2)), xy(end, 4 + slope*(end-2))),
                  fill=color, width=5)

    def dot(point, color, radius):
        px, py = point
        draw.ellipse((px-radius, py-radius, px+radius, py+radius),
                     fill=color, outline=BG, width=3)

    if tangent:
        line_through_p(4, GREEN)
    p = xy(2, 4)
    if h is not None:
        q = xy(2+h, (2+h)**2)
        line_through_p(4+h, ORANGE)
        if triangle:
            corner = xy(2+h, 4)
            draw.line((p, corner), fill=PURPLE, width=6)
            draw.line((corner, q), fill=ORANGE, width=6)
        dot(q, ORANGE, 10)
        if abs(h) >= .17:
            label(draw, (q[0] + (18 if h > 0 else -20), q[1]-33), "Q",
                  26, ORANGE, "bold", anchor="mt", stroke_width=3, stroke_fill=PANEL)
    dot(p, WHITE, 11)
    label(draw, (p[0]+12, p[1]+23), "P", 27, WHITE, "bold", stroke_width=3, stroke_fill=PANEL)

    if compare:
        curve_point, line_point = xy(2.1, 4.41), xy(2.1, 4.4)
        draw.line((line_point, xy(2.1, ymin)), fill=PURPLE, width=2)
        dot(curve_point, BLUE, 7)
        dot(line_point, GREEN, 6)


def graph_panel(draw, h=None, tangent=False, triangle=False, zoom=False, compare=False):
    panel(draw, (92, 240, 1190, 930))
    label(draw, (130, 271), "●  f(x) = x²", 27, BLUE, "bold")
    if h is not None:
        label(draw, (420, 271), "●  Secant through P and Q", 27, ORANGE)
    if tangent:
        label(draw, (420, 271), "●  Tangent at P", 27, GREEN)
    if zoom:
        label(draw, (1140, 274), "ZOOM NEAR P", 23, MUTED, "mono", anchor="ra")
    chart(draw, (187, 357, 1127, 849), h, tangent, triangle, zoom, compare)


def side(draw, heading, large, descriptions, accent=ORANGE):
    panel(draw, (1226, 240, 1828, 930))
    label(draw, (1268, 291), heading, 27, accent, "bold")
    lines(draw, 1268, 369, large, 38, 61)
    draw.line((1268, 570, 1786, 570), fill=EDGE, width=2)
    lines(draw, 1268, 618, descriptions, 28, 49, MUTED)


def draw_frame(beat, progress, student):
    scene, tag, title, _ = beat
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    label(draw, (93, 58), "M3  /  LINEAR ALGEBRA & CALCULUS", 24, BLUE, "mono")
    label(draw, (1827, 58), SCENES[scene-1].upper(), 24, MUTED, "mono", anchor="ra")
    draw.line((92, 111, 1828, 111), fill=EDGE, width=2)
    for i in range(6):
        left = 92+i*291
        draw.rounded_rectangle((left, 1005, left+279, 1011), radius=3,
                               fill=BLUE if i == scene-1 else EDGE)
    eased = progress*progress*(3-2*progress)

    if tag == "title":
        label(draw, (96, 210), "DERIVATIVE AND RATE OF CHANGE", 26, ORANGE, "mono")
        label(draw, (88, 278), title, 100, WHITE, "serif", spacing=10)
        label(draw, (96, 570), "Finding the slope of a curve", 35, MUTED)
        label(draw, (96, 735), "STUDENT", 22, BLUE, "mono")
        label(draw, (96, 776), student[0], 29)
        label(draw, (96, 831), f"ID  {student[1]}", 26, MUTED, "mono")
        panel(draw, (973, 200, 1828, 929))
        label(draw, (1008, 232), "f(x) = x²", 29, BLUE, "bold")
        chart(draw, (1050, 328, 1765, 845), 1.12 - .68*eased, triangle=True)
        return image

    label(draw, (90, 146), title, 59, WHITE, "serif")
    if tag in ALGEBRA:
        active = ALGEBRA.index(tag)
        panel(draw, (92, 240, 1828, 930))
        label(draw, (135, 273), "SECANT SLOPE AT P       [ f(2 + h) − f(2) ] / h", 28, BLUE, "mono")
        for i, (operation, equation) in enumerate(STEPS[:active+1]):
            y = 347 + i*109
            current = i == active
            ink = GREEN if i == 4 else ORANGE
            if current:
                panel(draw, (130, y-11, 1790, y+75), fill="#223242", radius=14)
            label(draw, (156, y+11), operation, 25,
                  fade(ink, .55+.45*eased, "#223242") if current else MUTED, "bold")
            label(draw, (480, y), equation, 47,
                  fade(WHITE, .55+.45*eased, "#223242") if current else MUTED)
        return image

    if tag in {"summary", "credits"}:
        full = tag == "summary"
        panel(draw, (92, 240, 1165 if not full else 1828, 930))
        for i, (key, value, color) in enumerate(TAKEAWAYS):
            y = 318+i*195
            alpha = min(1, max(0, eased*3-i))
            label(draw, (140, y), key, 29, color if not full else fade(color, alpha), "bold")
            label(draw, (140, y+51), value, 38 if not full else 47,
                  WHITE if not full else fade(WHITE, alpha), "serif")
            if i < 2:
                draw.line((140, y+140, 1110 if not full else 1777, y+140), fill=EDGE, width=2)
        if not full:
            panel(draw, (1195, 240, 1828, 930))
            label(draw, (1242, 310), "REFERENCE", 24, BLUE, "mono")
            lines(draw, 1242, 359, ["OpenStax · Calculus Volume 1", "§3.1 Defining the Derivative"], 29, 45)
            label(draw, (1242, 507), "PRODUCTION", 24, BLUE, "mono")
            lines(draw, 1242, 554, ["ChatGPT · script, storyboard,", "diagram design and animation code",
                                    "Flite (SLT) · synthetic English voice", "Music · none"], 27, 55)
        return image

    if tag in {"tangent", "approx", "compare"}:
        zoom = tag == "compare"
        graph_panel(draw, tangent=True, zoom=zoom, compare=zoom)
        if tag == "tangent":
            side(draw, "TANGENT AT P", ["y − 4 = 4(x − 2)", "y = 4x − 4"],
                 ["Passes through P = (2, 4)", "Slope = 4"], GREEN)
        elif tag == "approx":
            side(draw, "A SMALL STEP TO x = 2.1", ["h = 0.1", "Predicted rise = 0.4", "Actual rise = 0.41"],
                 ["Tangent prediction", "4 × 0.1 = 0.4"], GREEN)
        else:
            side(draw, "AT x = 2.1", ["Curve     4.41", "Tangent  4.40", "Gap       0.01"],
                 ["Curve − tangent = h²", "A step half as large gives", "one quarter of the gap."], GREEN)
        return image

    if tag == "limit":
        h = -.1 + .09*eased
        graph_panel(draw, h, triangle=True)
        panel(draw, (1226, 240, 1828, 930))
        label(draw, (1268, 291), "SECANT SLOPES", 27, ORANGE, "bold")
        label(draw, (1280, 375), "h", 29, MUTED, "mono")
        label(draw, (1560, 375), "Slope", 29, MUTED, "mono")
        for i, (step, slope) in enumerate([("−0.10", "3.90"), ("−0.01", "3.99"),
                                          ("+0.01", "4.01"), ("+0.10", "4.10")]):
            y = 448+79*i
            draw.line((1268, y-15, 1786, y-15), fill=EDGE, width=2)
            label(draw, (1280, y), step, 34, WHITE, "mono")
            label(draw, (1560, y), slope, 34, GREEN, "mono")
        label(draw, (1280, 821), "h → 0         slope → 4", 33, GREEN, "mono")
        return image

    transitions = {
        "puzzle": (.25, 1), "points": (.6, 1), "ratio": (1, 1), "right1": (1, 1),
        "right2": (1, .1), "left": (-.5, -.1),
    }
    start, end = transitions[tag]
    h = start + (end-start)*eased
    graph_panel(draw, h, triangle=tag != "points")
    if tag == "puzzle":
        side(draw, "THE QUESTION", ["P = (2, 4)", "Q moves on the curve"],
             ["The orange line rotates", "as Q slides.", "Which slope belongs to P?"])
    elif tag == "points":
        side(draw, "THE HORIZONTAL STEP h", ["P = (2, 4)", "Q = (2 + h, f(2 + h))"],
             ["h > 0 puts Q to the right.", "h < 0 puts Q to the left.", "h ≠ 0 keeps the points distinct."], PURPLE)
    elif tag == "ratio":
        side(draw, "SECANT SLOPE", ["Rise ÷ run", "[ f(2 + h) − f(2) ] / h"],
             ["Rise = f(2 + h) − f(2)", "Run = h", "Defined for h ≠ 0."])
    else:
        side(draw, "RISE ÷ RUN", [f"Run  {number(h)}", f"Rise  {number((2+h)**2-4)}",
                                  f"Slope  {number(4+h)}"],
             ["Run is the purple segment.", "Rise is the orange segment."])
    return image


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def duration(file):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(file),
    ], text=True))


def render_segment(folder, index, student):
    beat = BEATS[index]
    tag = beat[1]
    narration = folder / f"voice_{index:02}.txt"
    narration.write_text(beat[3], encoding="utf-8")
    voice = folder / f"voice_{index:02}.wav"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         f"flite=voice=slt:textfile={narration.name}", "-af", "atempo=0.94,volume=1.5",
         "-ar", "48000", str(voice)], cwd=folder)
    seconds = max(16, math.ceil(duration(voice)+2.1))
    animated = {"title", "puzzle", "points", "right2", "left", "limit", "summary"}
    count = 78 if tag in animated else 17 if tag in ALGEBRA else 1
    segment = folder / f"part_{index:02}.mp4"
    command = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-video_size", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-i", str(voice),
        "-vf", f"tpad=stop_mode=clone:stop={seconds*FPS-count}",
        "-af", "adelay=650,apad", "-t", str(seconds), "-c:v", "libx264",
        "-preset", "veryfast", "-threads", "3", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", str(segment),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for n in range(count):
            progress = 1 if count == 1 else n/(count-1)
            if count == 78:
                progress = min(1, max(0, (n-8)/(count-9)))
            encoder.stdin.write(draw_frame(beat, progress, student).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError(f"FFmpeg failed on beat {index + 1}")
    print(f"{index+1:02}  {tag:12} {seconds:2}s", flush=True)
    return segment, seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="[Student name]")
    parser.add_argument("--student-id", default="[Student ID]")
    parser.add_argument("--output", type=Path, default=Path("_Video.mp4"))
    parser.add_argument("--preview-dir", type=Path, help="Write a PNG per beat instead of a video")
    args = parser.parse_args()
    student = (args.name, args.student_id)
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        for index, beat in enumerate(BEATS):
            draw_frame(beat, 1, student).save(args.preview_dir / f"{index:02}_{beat[1]}.png")
        return

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m3-animation-") as temporary:
        folder = Path(temporary)
        rendered = [render_segment(folder, i, student) for i in range(len(BEATS))]
        manifest = folder / "segments.txt"
        manifest.write_text("".join(f"file '{file.name}'\n" for file, _ in rendered))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
             "-c", "copy", "-movflags", "+faststart", str(output)], cwd=folder)
        print(f"Total: {sum(seconds for _, seconds in rendered)} seconds")


if __name__ == "__main__":
    main()
