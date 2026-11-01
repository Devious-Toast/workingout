import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

T, UA, FA, TH, SH, FT = 3.0, 1.5, 1.4, 2.1, 2.0, 0.7
C1, C2, CT, CB = "#1f4e79", "#8fb3d9", "#c0392b", "#d9d2c3"


def vec(a, l):
    r = math.radians(a)
    return (l * math.cos(r), l * math.sin(r))


def add(p, v):
    return (p[0] + v[0], p[1] + v[1])


def arm(sh, a):
    e = add(sh, vec(a[0], UA))
    return [sh, e, add(e, vec(a[1], FA))]


def leg(hip, l):
    k = add(hip, vec(l[0], TH))
    an = add(k, vec(l[1], SH))
    ft = l[2] if len(l) > 2 else 0
    return [hip, k, an, add(an, vec(ft, FT))]


def contact_key(p):
    return "l2" if "l2" in p else "l"


def build(p, theta=None):
    p = dict(p)
    if theta is not None:
        p["t"] = theta
        k = contact_key(p)
        v = list(p[k])
        v[0] = 180 + theta
        if p.get("contact") != "knee":
            v[1] = 180 + theta
        p[k] = tuple(v)
    hip = (0, 0)
    sh = add(hip, vec(p["t"], T))
    pts = {"hip": hip, "sh": sh, "a": arm(sh, p["a"]), "l": leg(hip, p["l"])}
    if "a2" in p:
        pts["a2"] = arm(sh, p["a2"])
    if "l2" in p:
        pts["l2"] = leg(hip, p["l2"])
    pts["head"] = add(sh, vec(p["t"] + p.get("hd", 0), 0.95))
    return pts


def ground_of(p, pts):
    lg = pts[contact_key(p)]
    return lg[1][1] if p.get("contact") == "knee" else lg[3][1]


def solved(p):
    h = p["solve"]
    f = lambda th: build(p, th)["a"][2][1] - ground_of(p, build(p, th)) - h
    lo, hi = 0.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return build(p, (lo + hi) / 2)


def flat(pts):
    for k, v in pts.items():
        if k == "head":
            continue
        for q in (v if isinstance(v, list) else [v]):
            yield q


def draw(ax, p, top=9.4):
    box = None
    if "solve" in p:
        pts = solved(p)
        ground = ground_of(p, pts)
        if p["solve"] > 0:
            box = (pts["a"][2], p["solve"])
    else:
        pts = build(p)
        ground = min(y for _, y in flat(pts))
    xs = [x for x, _ in flat(pts)]
    ox, oy = -(max(xs) + min(xs)) / 2, -ground
    P = lambda q: (q[0] + ox, q[1] + oy)
    ax.plot([-8.3, 8.3], [0, 0], color="#888", lw=1.2, zorder=1)
    if box:
        hx = P(box[0])[0]
        ax.add_patch(Rectangle((hx - 1.0, 0), 2.0, box[1], color=CB, zorder=1))
    if p.get("chair"):
        hp = P(pts["hip"])
        ax.add_patch(Rectangle((hp[0] - 1.6, 0), 1.9, hp[1] - 0.45, color=CB, zorder=1))
        ax.add_patch(Rectangle((hp[0] - 1.6, 0), 0.2, hp[1] + 2.2, color=CB, zorder=1))

    def line(seq, c, lw, z):
        s = [P(q) for q in seq]
        ax.plot([q[0] for q in s], [q[1] for q in s], color=c, lw=lw, zorder=z,
                solid_capstyle="round", solid_joinstyle="round")

    for k in ("a2", "l2"):
        if k in pts:
            line(pts[k], C2, 5, 2)
    line([pts["hip"], pts["sh"]], CT, 9, 3)
    line(pts["l"], C1, 5, 4)
    line(pts["a"], C1, 5, 4)
    ax.add_patch(Circle(P(pts["head"]), 0.55, color=CT, zorder=5))
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(-0.6, top)
    ax.set_aspect("equal")
    ax.axis("off")


S = dict(t=90, a=(270, 270), l=(270, 270, 0))
HP = dict(t=0, a=(270, 270), l=(180, 180, 300), solve=0.0)

POSES = {
    "chair_squat": [("Start: stand tall", S),
                    ("Sit back, touch the chair, stand", dict(t=75, a=(0, 0), l=(2, 262, 0), chair=True))],
    "incline_pushup": [("Top: arms straight", dict(t=0, a=(270, 270), l=(180, 180, 300), solve=3.0)),
                       ("Bottom: chest to counter", dict(t=0, a=(235, 305), l=(180, 180, 300), solve=3.0))],
    "pushup": [("Top: strong plank", HP),
               ("Bottom: chest near floor", dict(HP, a=(235, 305)))],
    "bridge": [("Start: back flat", dict(t=180, a=(0, 0), l=(60, 282, 0))),
               ("Top: squeeze glutes", dict(t=200, a=(0, 0), l=(20, 282, 0)))],
    "birddog": [("Start: hands under shoulders", dict(t=10, a=(270, 270), l=(270, 180, 180))),
                ("Reach opposite arm and leg", dict(t=10, a=(8, 8), a2=(270, 270), l=(190, 190, 200), l2=(270, 180, 180)))],
    "deadbug": [("Start: arms up, knees over hips", dict(t=180, a=(90, 90), l=(90, 180))),
                ("Lower opposite arm and leg", dict(t=180, a=(90, 90), a2=(180, 180), l=(90, 180), l2=(5, 5, 80)))],
    "plank": [("Knee plank (easier)", dict(t=0, a=(270, 0), l=(180, 155, 170), solve=0.0, contact="knee")),
              ("Full forearm plank", dict(t=0, a=(270, 0), l=(180, 180, 300), solve=0.0))],
    "lunge": [("Start: stand tall", dict(S, a=(255, 30))),
              ("Step back, drop down, push up", dict(t=90, a=(255, 30), l=(350, 270, 0), l2=(250, 200, 340)))],
    "split": [("Start: staggered stance", dict(t=90, a=(255, 30), l=(285, 268, 0), l2=(250, 250, 320))),
              ("Lower straight down", dict(t=90, a=(255, 30), l=(350, 270, 0), l2=(250, 200, 340)))],
    "superman": [("Start: lie face down", dict(t=0, a=(0, 0), l=(180, 180, 180))),
                 ("Lift arms, chest and legs", dict(t=8, a=(25, 25), l=(172, 172, 172), hd=10))],
    "squat": [("Start: feet shoulder width", S),
              ("Hips back and down", dict(t=62, a=(0, 0), l=(3, 255, 0)))],
    "hinge": [("Start: soft knees", dict(t=90, a=(270, 270), l=(278, 258, 0))),
              ("Push hips back, flat back", dict(t=35, a=(270, 270), l=(278, 258, 0)))],
    "climber": [("Start: high plank", HP),
                ("Drive one knee to chest", dict(t=0, a=(270, 270), l=(325, 200, 250), l2=(180, 180, 300), solve=0.0))],
    "tap": [("Start: wide high plank", HP),
            ("Tap opposite shoulder, hips still", dict(HP, a2=(335, 100)))],
    "march": [("Start: stand tall", S),
              ("Drive knee up, opposite arm swings", dict(t=90, a=(320, 70), a2=(215, 255), l=(15, 285, 0), l2=(270, 270, 0)))],
}


LOW = {'pushup', 'bridge', 'birddog', 'deadbug', 'plank', 'superman', 'climber', 'tap'}


def render(key, path):
    poses = POSES[key]
    low = key in LOW
    fig, axes = plt.subplots(1, len(poses), figsize=(3.6 * len(poses), 1.5 if low else 2.15), dpi=170)
    for ax, (lab, p) in zip(axes, poses):
        draw(ax, p, 5.4 if low else 9.4)
        ax.set_title(lab, fontsize=9, color="#333")
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.86, wspace=0.05)
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs("./img", exist_ok=True)
    for k in POSES:
        render(k, f"./img/{k}.png")
    # contact sheet for review
    import PIL.Image as I
    ims = [I.open(f"./img/{k}.png") for k in POSES]
    w, h = ims[0].size
    sheet = I.new('RGB', (w * 3, h * 5), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 3) * w, (i // 3) * h))
    sheet.thumbnail((2200, 2200))
    sheet.save("./sheet.png")
