# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

ROSE = (217, 106, 148, 255)   # #d96a94
ROSE2 = (239, 170, 194, 255)  # #efaac2
CREAM = (246, 241, 232, 255)  # #f6f1e8

F = 260  # font px
font = ImageFont.truetype("C:/Windows/Fonts/constanb.ttf", F)

def text_w(s):
    b = font.getbbox(s)
    return b[2] - b[0]

pad = int(F * 0.30)
kern = int(F * 0.07)
r = int(F * 0.25)
stroke = max(6, int(F * 0.058))
gap = int(F * 0.30)          # spacing between ring centers (overlap for interlock)
ring_span = r * 2 + gap      # visual width of twin rings

du_w = text_w("Du")
n_w = text_w("n")

total_w = pad + du_w + kern + ring_span + kern + n_w + pad
total_h = int(F * 1.5)

img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

baseline = int(F * 1.05)
x = pad
d.text((x, baseline), "Du", font=font, fill=ROSE, anchor="ls")
x += du_w + kern

cy = baseline - int(F * 0.36)
c1 = x + r
c2 = c1 + gap
d.ellipse([c1 - r, cy - r, c1 + r, cy + r], outline=ROSE, width=stroke)
d.ellipse([c2 - r, cy - r, c2 + r, cy + r], outline=ROSE2, width=stroke)
x += ring_span + kern

d.text((x, baseline), "n", font=font, fill=ROSE, anchor="ls")

img.save("static/logo.png")
print("logo.png", img.size)

# ---- square icon (SNS profile), cream rounded bg + twin rings ----
SZ = 512
icon = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
di = ImageDraw.Draw(icon)
di.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=112, fill=CREAM)
ir = 118
istroke = 34
icy = SZ // 2
ic1 = SZ // 2 - 52
ic2 = SZ // 2 + 52
di.ellipse([ic1 - ir, icy - ir, ic1 + ir, icy + ir], outline=ROSE, width=istroke)
di.ellipse([ic2 - ir, icy - ir, ic2 + ir, icy + ir], outline=ROSE2, width=istroke)
icon.save("static/logo-mark.png")
print("logo-mark.png", icon.size)

# ---- SNS square (full-bleed cream, rings + "Duon" wordmark) ----
SQ = 800
sns = Image.new("RGBA", (SQ, SQ), CREAM)
ds = ImageDraw.Draw(sns)
# twin rings, upper-center
sr = 150
sstroke = 26
scy = int(SQ * 0.40)
sc1 = SQ // 2 - 60
sc2 = SQ // 2 + 60
ds.ellipse([sc1 - sr, scy - sr, sc1 + sr, scy + sr], outline=ROSE, width=sstroke)
ds.ellipse([sc2 - sr, scy - sr, sc2 + sr, scy + sr], outline=ROSE2, width=sstroke)
# wordmark below
wf = ImageFont.truetype("C:/Windows/Fonts/constanb.ttf", 150)
wb = ds.textbbox((0, 0), "Duon", font=wf, anchor="ls")
ds.text((SQ // 2, int(SQ * 0.82)), "Duon", font=wf, fill=ROSE, anchor="ms")
sns.save("static/logo-sns.png")
sns.resize((400, 400), Image.LANCZOS).save("static/logo-sns-400.png")
print("logo-sns.png", sns.size)
