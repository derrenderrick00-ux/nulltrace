"""Procedural 2D operator animation: no external sprite files or network assets.

Illustrative art for v0.6.1; replaceable by licensed frame/sprite assets later.
The animation math is deterministic and independent of Pygame for unit tests.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sin, pi

APPEARANCES = ('hoodie', 'analyst', 'technician')

@dataclass(frozen=True)
class AnimationFrame:
    bob: float
    arm_swing: float
    leg_swing: float
    blink: bool


def frame_at(milliseconds: int, moving: bool = False, reduced_motion: bool = False) -> AnimationFrame:
    """Subtle breathing/blinking when idle; alternating walk stride when moving."""
    if reduced_motion:
        return AnimationFrame(0.0, 0.0, 0.0, False)
    t = max(0, int(milliseconds)) / 1000.0
    if moving:
        phase = sin(t * 2 * pi * 2.4)
        return AnimationFrame(abs(phase) * 2.3, phase * 13.0, -phase * 12.0, False)
    return AnimationFrame(sin(t * 2 * pi * 0.30) * 1.4, sin(t * 2 * pi * 0.22) * 1.5, 0.0, int(t * 1000) % 4400 < 115)


def advance_position(x: float, y: float, dx: float, dy: float, dt: float,
                     bounds=(344.0, 1044.0, 400.0, 559.0), speed: float = 170.0):
    """Frame-independent movement clamped inside the permitted room rectangle."""
    from math import hypot
    length = hypot(dx, dy)
    if not length or dt <= 0:
        return x, y
    amount = max(0.0, min(float(dt), 0.10)) * speed / length
    xmin, xmax, ymin, ymax = bounds
    return max(xmin, min(xmax, x + dx * amount)), max(ymin, min(ymax, y + dy * amount))


def draw_operator(pg, canvas, x: float, foot_y: float, appearance: str,
                  milliseconds: int, moving: bool = False, facing: int = 1,
                  scale: float = 1.0, reduced_motion: bool = False):
    """Draw an animated operator with clothing differentiated by appearance.

    Coordinates are world/screen units at 1x: the feet are on (x, foot_y).
    Only primitive Pygame polygons/circles are used; no private user imagery.
    """
    from math import cos
    if appearance not in APPEARANCES:
        appearance = 'hoodie'
    frame = frame_at(milliseconds, moving, reduced_motion)
    coat = {'hoodie': (44, 73, 91), 'analyst': (68, 87, 113), 'technician': (104, 93, 63)}[appearance]
    accent = {'hoodie': (65, 213, 206), 'analyst': (139, 184, 247), 'technician': (238, 188, 95)}[appearance]
    outline = (10, 21, 32)
    skin = (205, 171, 141)
    def p(dx, dy):
        return (int(x + dx * scale), int(foot_y + (dy - frame.bob) * scale))
    def poly(color, points, width=0):
        pg.draw.polygon(canvas, color, [p(*v) for v in points], width)
    def line(color, a, b, width=2):
        pg.draw.line(canvas, color, p(*a), p(*b), max(1, int(width*scale)))
    def circ(color, at, r, width=0):
        pg.draw.circle(canvas, color, p(*at), max(1,int(r * scale)), width)
    def ell(color, dx, dy, w, h):
        pg.draw.ellipse(canvas, color, pg.Rect(int(x+dx*scale), int(foot_y+dy*scale),
                                             max(1,int(w*scale)),max(1,int(h*scale))))
    ell((8, 18, 29), -32, -5, 64, 12)
    stride = frame.leg_swing if moving else 0
    for direction in (-1, 1):
        sx = direction * 13
        leg = sx + (stride if direction == 1 else -stride)*0.42
        poly(outline, [(sx-9,-57),(sx+8,-57),(leg+8,-7),(leg-9,-7)])
        poly((37, 49, 71), [(sx-6,-55),(sx+5,-55),(leg+5,-11),(leg-6,-11)])
        ell((17,25,34), leg-11, -10, 23, 12)
        line(accent, (leg-9,-9),(leg+7,-9),1)
    # Arms move independently, opposite to the walking legs.
    swing = frame.arm_swing
    for direction in (-1,1):
        arm = direction * 34
        wrist = arm + (swing if direction < 0 else -swing)*0.45
        poly(outline,[(direction*25,-113),(direction*39,-111),(wrist+direction*3,-59),(wrist-direction*10,-56)])
        poly(coat,[(direction*26,-110),(direction*36,-106),(wrist+direction*2,-62),(wrist-direction*7,-61)])
        circ(skin,(wrist-direction*3,-58),5)
    poly(outline,[(-27,-119),(27,-119),(35,-58),(-35,-58)])
    poly(coat,[(-24,-116),(24,-116),(29,-60),(-29,-60)])
    if appearance == 'hoodie':
        poly((25,48,62),[(-23,-116),(23,-116),(13,-103),(-13,-103)])
        line(accent,(-6,-100),(-6,-85),2); line(accent,(7,-100),(7,-87),2)
        line((100,136,147),(-23,-77),(23,-77),1)
    elif appearance == 'analyst':
        poly((218,221,220),[(-8,-113),(8,-113),(2,-81),(-2,-81)])
        poly((24,42,61),[(-4,-110),(4,-110),(7,-90),(0,-83),(-7,-90)])
        line(accent,(-14,-70),(14,-70),2)
    else:
        poly((155,129,69),[(-20,-104),(20,-104),(23,-85),(-23,-85)])
        line(accent,(-14,-91),(14,-91),3)
        poly((41,60,70),[(9,-111),(21,-111),(21,-97),(9,-97)])
    # Neck and head. Blink lasts about 115 ms every 4.4 seconds.
    poly(outline,[(-8,-123),(8,-123),(9,-109),(-9,-109)])
    poly(skin,[(-6,-124),(6,-124),(6,-110),(-6,-110)])
    if appearance == 'hoodie':
        circ(outline,(0,-144),30)
        circ((26,48,63),(0,-145),26)
        circ(skin,(0,-144),20)
        poly(coat,[(-29,-142),(-15,-167),(-2,-169),(-18,-151)])
        poly(coat,[(29,-142),(15,-167),(2,-169),(18,-151)])
    else:
        circ(outline,(0,-145),24)
        circ(skin,(0,-145),20)
        poly((27,37,47),[(-21,-151),(-14,-166),(9,-166),(19,-157),(-5,-159)])
    eyex = -9 if facing >= 0 else -11
    if frame.blink:
        line(outline,(eyex,-143),(eyex+6,-143),2)
        line(outline,(eyex+15,-143),(eyex+21,-143),2)
    else:
        circ(outline,(eyex+3,-143),2)
        circ(outline,(eyex+18,-143),2)
    line((131,85,73),(-3,-133),(5,-133),1)
    if moving:
        # Direction indicator doubles as a subtle leg animation accent.
        line(accent, (-15,-2),(15,-2),1)
    return pg.Rect(int(x-41*scale),int(foot_y-177*scale),int(82*scale),int(182*scale))
