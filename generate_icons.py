import os, math
from PIL import Image, ImageDraw, ImageFont

def generate_usted_gcc_icons():
    os.makedirs("static/icons", exist_ok=True)

    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="maroonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8A002A"/><stop offset="100%" stop-color="#63001C"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFD043"/><stop offset="100%" stop-color="#E59E00"/>
    </linearGradient>
    <linearGradient id="flameGrad" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#D32F2F"/><stop offset="50%" stop-color="#F57C00"/>
      <stop offset="100%" stop-color="#FFEB3B"/>
    </linearGradient>
  </defs>
  <path fill="url(#maroonGrad)" d="M256,40 L272,40 L276,66 A190,190 0 0,1 325,86 L345,69 L368,82 L361,107 A190,190 0 0,1 405,133 L429,122 L447,143 L433,165 A190,190 0 0,1 462,199 L488,198 L496,227 L474,242 A190,190 0 0,1 474,270 L496,285 L488,314 L462,313 A190,190 0 0,1 433,347 L447,369 L429,390 L405,379 A190,190 0 0,1 361,405 L368,430 L345,443 L325,426 A190,190 0 0,1 276,446 L272,472 L240,472 L236,446 A190,190 0 0,1 187,426 L167,443 L144,430 L151,405 A190,190 0 0,1 107,379 L83,390 L65,369 L79,347 A190,190 0 0,1 50,313 L24,314 L16,285 L38,270 A190,190 0 0,1 38,242 L16,227 L24,198 L50,199 A190,190 0 0,1 79,165 L65,143 L83,122 L107,133 A190,190 0 0,1 151,107 L144,82 L167,69 L187,86 A190,190 0 0,1 236,66 L240,40 Z"/>
  <circle cx="256" cy="256" r="172" fill="none" stroke="#FFFFFF" stroke-width="8"/>
  <circle cx="256" cy="256" r="160" fill="none" stroke="#006A4E" stroke-width="6"/>
  <circle cx="256" cy="256" r="150" fill="url(#goldGrad)" stroke="#FFFFFF" stroke-width="4"/>
  <circle cx="256" cy="256" r="144" fill="none" stroke="#006A4E" stroke-width="3.5"/>
  <line x1="115" y1="256" x2="397" y2="256" stroke="#006A4E" stroke-width="5"/>
  <g stroke="#006A4E" stroke-width="3.5" fill="none">
    <path d="M148,256 A110,110 0 0,0 364,256"/>
    <path d="M180,256 A78,78 0 0,0 332,256"/>
    <path d="M212,256 A46,46 0 0,0 300,256"/>
    <line x1="256" y1="256" x2="256" y2="398"/>
    <line x1="256" y1="256" x2="180" y2="365"/>
    <line x1="256" y1="256" x2="332" y2="365"/>
  </g>
  <path d="M254,250 C220,242 165,244 140,252 L155,224 C180,216 225,214 254,222 Z" fill="#FFFFFF" stroke="#006A4E" stroke-width="3"/>
  <path d="M258,250 C292,242 347,244 372,252 L357,224 C332,216 287,214 258,222 Z" fill="#FFFFFF" stroke="#006A4E" stroke-width="3"/>
  <line x1="256" y1="220" x2="256" y2="252" stroke="#006A4E" stroke-width="4"/>
  <path d="M238,206 L274,206 L268,220 L244,220 Z" fill="#006A4E"/>
  <path d="M256,150 C242,172 238,188 244,198 C248,204 256,206 256,206 C256,206 264,204 268,198 C274,188 270,172 256,150 Z" fill="url(#flameGrad)"/>
  <path d="M256,172 C248,184 248,194 252,199 C256,202 260,199 264,194 C264,184 256,172 256,172 Z" fill="#FFF9C4"/>
  <path d="M90,425 C150,455 362,455 422,425 C430,448 415,472 97,472 C82,448 90,425 90,425 Z" fill="url(#maroonGrad)" stroke="#FFFFFF" stroke-width="3"/>
  <text x="256" y="460" font-family="Arial" font-size="28" font-weight="bold" fill="#FFFFFF" text-anchor="middle">USTED GCC</text>
  <text x="256" y="482" font-family="Arial" font-size="11" fill="#FFD043" text-anchor="middle">GUIDANCE &amp; COUNSELLING</text>
</svg>"""

    with open("static/icons/icon.svg", "w") as f:
        f.write(svg_content)
    print("  icon.svg")

    S = 4
    SIZE = 512 * S
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2 - 20*S
    MAROON=(122,0,38,255); MAROON_DARK=(80,0,20,255); GOLD=(253,184,19,255)
    GREEN=(0,106,78,255); WHITE=(255,255,255,255)
    FLAME_RED=(217,56,30,255); FLAME_YELLOW=(255,235,59,255)

    num_teeth=12; r_inner,r_outer=180*S,225*S; pts=[]
    for i in range(num_teeth):
        ab=i*(2*math.pi/num_teeth)
        pts+=[(cx+r_inner*math.cos(ab-0.12),cy+r_inner*math.sin(ab-0.12)),
              (cx+r_outer*math.cos(ab-0.08),cy+r_outer*math.sin(ab-0.08)),
              (cx+r_outer*math.cos(ab+0.08),cy+r_outer*math.sin(ab+0.08)),
              (cx+r_inner*math.cos(ab+0.12),cy+r_inner*math.sin(ab+0.12))]
    draw.polygon(pts, fill=MAROON)
    draw.ellipse([cx-175*S,cy-175*S,cx+175*S,cy+175*S], outline=WHITE, width=9*S)
    draw.ellipse([cx-162*S,cy-162*S,cx+162*S,cy+162*S], outline=GREEN, width=7*S)
    draw.ellipse([cx-152*S,cy-152*S,cx+152*S,cy+152*S], fill=GOLD, outline=WHITE, width=4*S)
    draw.ellipse([cx-145*S,cy-145*S,cx+145*S,cy+145*S], outline=GREEN, width=4*S)
    draw.line([(cx-140*S,cy),(cx+140*S,cy)], fill=GREEN, width=6*S)
    for r_web in [105*S, 75*S, 45*S]:
        draw.arc([cx-r_web,cy-r_web,cx+r_web,cy+r_web], start=0, end=180, fill=GREEN, width=4*S)
    draw.line([(cx,cy),(cx,cy+144*S)], fill=GREEN, width=4*S)
    draw.line([(cx,cy),(cx-76*S,cy+115*S)], fill=GREEN, width=4*S)
    draw.line([(cx,cy),(cx+76*S,cy+115*S)], fill=GREEN, width=4*S)
    bx, by = cx, cy-25*S
    draw.polygon([(bx-2*S,by),(bx-100*S,by+12*S),(bx-85*S,by-25*S),(bx-2*S,by-32*S)], fill=WHITE, outline=GREEN)
    draw.polygon([(bx+2*S,by),(bx+100*S,by+12*S),(bx+85*S,by-25*S),(bx+2*S,by-32*S)], fill=WHITE, outline=GREEN)
    draw.line([(bx,by-35*S),(bx,by+2*S)], fill=GREEN, width=5*S)
    tx, ty = cx, cy-68*S
    draw.polygon([(tx-18*S,ty),(tx+18*S,ty),(tx+10*S,ty+18*S),(tx-10*S,ty+18*S)], fill=GREEN)
    draw.polygon([(tx,ty-50*S),(tx+15*S,ty-25*S),(tx+14*S,ty-8*S),(tx,ty-2*S),(tx-14*S,ty-8*S),(tx-15*S,ty-25*S)], fill=FLAME_RED)
    draw.polygon([(tx,ty-32*S),(tx+8*S,ty-18*S),(tx+6*S,ty-6*S),(tx,ty-2*S),(tx-6*S,ty-6*S),(tx-8*S,ty-18*S)], fill=FLAME_YELLOW)
    rib_y = SIZE - 120*S
    draw.rounded_rectangle([75*S,rib_y-10*S,SIZE-75*S,rib_y+65*S], radius=20*S, fill=MAROON, outline=WHITE, width=4*S)
    draw.rounded_rectangle([85*S,rib_y-2*S, SIZE-85*S,rib_y+57*S], radius=15*S, outline=GOLD, width=2*S)

    fl = fs = None
    for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/Arial Bold.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(fp):
            try:
                fl = ImageFont.truetype(fp, 38*S)
                fs = ImageFont.truetype(fp, 16*S)
                break
            except Exception:
                pass
    if fl is None:
        fl = fs = ImageFont.load_default()

    draw.text((SIZE//2, rib_y+15*S), "USTED GCC",             fill=WHITE, font=fl, anchor="mm")
    draw.text((SIZE//2, rib_y+45*S), "GUIDANCE & COUNSELLING", fill=GOLD,  font=fs, anchor="mm")

    img.resize((512,512), Image.Resampling.LANCZOS).save("static/icons/icon-512.png", "PNG")
    img.resize((192,192), Image.Resampling.LANCZOS).save("static/icons/icon-192.png", "PNG")
    img.resize((64,64),   Image.Resampling.LANCZOS).save("static/favicon.ico", "ICO")
    print("  icon-512.png")
    print("  icon-192.png")
    print("  static/favicon.ico")
    print("Done!")

if __name__ == "__main__":
    generate_usted_gcc_icons()
