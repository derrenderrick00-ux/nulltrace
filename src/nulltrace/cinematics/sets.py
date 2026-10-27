"""Procedural five-location 2D backgrounds. No external graphics files required."""
from __future__ import annotations
from nulltrace.cinematics.timeline import ENVIRONMENTS, SHOTS

PALETTES = {
 'apartment':((12,22,39),(34,54,80),(80,157,175)),
 'operations':((10,24,35),(25,55,68),(66,203,193)),
 'archive':((20,24,40),(52,50,76),(155,148,210)),
 'datacenter':((10,17,31),(25,50,71),(88,173,224)),
 'mirror':((18,18,38),(46,41,77),(229,163,107)),
}

def draw_set(pg,canvas,area,environment,shot='establish',milliseconds=0,reduced_motion=False):
    """Render cinematic props in bounded rect. All motion optional and deterministic."""
    if environment not in ENVIRONMENTS:raise ValueError('Unknown scene location')
    if shot not in SHOTS:raise ValueError('Unknown camera shot')
    bounds=pg.Rect(area)
    dark,mid,accent=PALETTES[environment]
    pg.draw.rect(canvas,dark,bounds,border_radius=10)
    x,y,w,h=bounds
    # Background window and frames: scaled to area rather than window size.
    window=pg.Rect(x+int(w*.12),y+24,int(w*.76),int(h*.43))
    pg.draw.rect(canvas,mid,window,border_radius=5)
    for col in range(1,7):
        xx=window.left+int(window.width*col/7)
        pg.draw.line(canvas,dark,(xx,window.top),(xx,window.bottom),3)
    for row in range(1,4):
        yy=window.top+int(window.height*row/4)
        pg.draw.line(canvas,dark,(window.left,yy),(window.right,yy),2)
    for i in range(17):
        bx=x+int(w*(.04+i*.055)); height=int(h*(.05+(i*7%9)*.013))
        pg.draw.rect(canvas,(22,37,54),(bx,y+int(h*.6)-height,13,height))
    ground=pg.Rect(x+14,y+int(h*.62),w-28,int(h*.33))
    pg.draw.rect(canvas,(27,44,53),ground,border_radius=8)
    # Desks/screens emphasize environment and focal prop.
    count=3 if environment!='apartment' else 2
    for i in range(count):
        mx=x+int(w*(.19+i*.31))
        screen=pg.Rect(mx,y+int(h*.50),int(w*.17),int(h*.13))
        pg.draw.rect(canvas,(8,18,30),screen,border_radius=3)
        pg.draw.rect(canvas,accent,screen,2,border_radius=3)
        for bar in range(3):
            pg.draw.line(canvas,mid,(screen.x+8,screen.y+11+bar*8),(screen.right-8,screen.y+11+bar*8),2)
        pg.draw.rect(canvas,(56,62,70),(screen.x-10,screen.bottom+7,screen.width+20,7))
    if environment in ('datacenter','archive','mirror'):
        pg.draw.rect(canvas,(31,49,64),(x+w-101,y+49,70,int(h*.48)),border_radius=5)
        for j in range(7):
            yy=y+72+j*23
            pg.draw.rect(canvas,(12,22,33),(x+w-90,yy,49,14),border_radius=2)
            pg.draw.circle(canvas,accent,(x+w-83,yy+7),2)
    # Text-safe shot highlights; no procedural time-dependent flashing for reduced motion.
    if shot in ('console','reveal'):
        focus=pg.Rect(x+int(w*.42),y+int(h*.41),int(w*.19),int(h*.24))
        pg.draw.rect(canvas,accent,focus,2,border_radius=6)
    elif shot=='close':
        pg.draw.circle(canvas,accent,(x+int(w*.79),y+int(h*.43)),17,2)
    if shot=='reveal' and not reduced_motion:
        shift=(milliseconds//350)%5
        pg.draw.line(canvas,accent,(x+20,y+h-28-shift),(x+w-20,y+h-28-shift),2)
    pg.draw.rect(canvas,accent,bounds,1,border_radius=10)
