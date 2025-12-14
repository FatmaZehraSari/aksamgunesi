from PIL import Image, ImageDraw, ImageFilter
import math
import random

# --- YARDIMCI FONKSİYON: Gradyan Oluşturma ---
def create_gradient(width, height, color1, color2, vertical=True):
    base = Image.new('RGBA', (width, height), color1)
    top = Image.new('RGBA', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            if vertical:
                ratio = y / height
            else:
                ratio = x / width
            mask_data.append(int(255 * ratio))
    mask.putdata(mask_data)
    return Image.composite(top, base, mask)

# --- YARDIMCI FONKSİYON: Işık Işını Çizme ---
def draw_sun_rays(draw, cx, cy, radius, length, width, color, start_angle, end_angle):
    # Açıları normalize et (0-360 arası)
    start_angle = start_angle % 360
    end_angle = end_angle % 360
    if end_angle < start_angle: end_angle += 360
    
    step = 30 
    
    for i in range(start_angle, end_angle + 1, step):
        # Dikey ayırıcı çizgilere denk gelen açıları atla
        if i % 180 == 90:
            continue
            
        rad = math.radians(i)
        # Başlangıç (Güneş kenarından biraz dışarıda)
        x1 = cx + (radius + 5) * math.cos(rad)
        y1 = cy + (radius + 5) * math.sin(rad)
        # Bitiş
        x2 = cx + (radius + 5 + length) * math.cos(rad)
        y2 = cy + (radius + 5 + length) * math.sin(rad)
        
        # Yuvarlak uçlu çizgi
        draw.line([(x1,y1), (x2,y2)], fill=color, width=width)
        r = width / 2
        draw.ellipse((x1-r, y1-r, x1+r, y1+r), fill=color)
        draw.ellipse((x2-r, y2-r, x2+r, y2+r), fill=color)

def create_final_icon():
    print("🌗 Final İkon (Her iki tarafta belirgin ışınlar) hazırlanıyor...")

    S = 1024 # Boyut
    CX, CY = S // 2, S // 2
    R = S // 2 - 20 # Ana yarıçap

    # --- GÜNEŞ GEOMETRİSİ ---
    sun_r = 120
    sun_cx, sun_cy = CX, CY - R // 2

    # --- 1. KATMAN: GÜNDÜZ (Day) - Sol Üst ---
    day_layer = create_gradient(S, S, (135, 206, 235), (220, 240, 255))
    day_draw = ImageDraw.Draw(day_layer)
    
    # GÜNEŞ IŞINLARI (Mavi Taraf)
    draw_sun_rays(day_draw, sun_cx, sun_cy, sun_r, 40, 15, (255, 255, 200), 90, 270)
    
    # GÜNEŞ GÖVDESİ (Mavi Taraf)
    day_draw.pieslice((sun_cx-sun_r, sun_cy-sun_r, sun_cx+sun_r, sun_cy+sun_r), 
                      90, 270, fill=(255, 255, 220))

    # --- 2. KATMAN: GÜN BATIMI (Sunset) - Sağ Üst ---
    sunset_layer = create_gradient(S, S, (255, 70, 50), (255, 200, 50))
    sunset_draw = ImageDraw.Draw(sunset_layer)
    
    # --- DÜZELTME BURADA ---
    # GÜNEŞ IŞINLARI (Turuncu Taraf)
    # Rengi daha parlak yaptık (255, 180, 30) ve boyunu uzattık (55)
    draw_sun_rays(sunset_draw, sun_cx, sun_cy, sun_r, 55, 15, (255, 180, 30), 270, 450)

    # GÜNEŞ GÖVDESİ (Turuncu Taraf - Çerçeveli)
    sunset_draw.pieslice((sun_cx-sun_r, sun_cy-sun_r, sun_cx+sun_r, sun_cy+sun_r), 
                         270, 90, fill=(255, 120, 0), 
                         outline=(200, 60, 0), width=6)

    # --- 3. KATMAN: GECE (Night) - Alt ---
    night_layer = create_gradient(S, S, (20, 20, 100), (0, 0, 40))
    night_draw = ImageDraw.Draw(night_layer)
    # HİLAL AY
    moon_r = 100
    moon_x, moon_y = CX, CY + 180
    night_draw.ellipse((moon_x-moon_r, moon_y-moon_r, moon_x+moon_r, moon_y+moon_r), fill=(230, 230, 255))
    shadow_r = 90
    night_draw.ellipse((moon_x-shadow_r-20, moon_y-shadow_r-20, moon_x+shadow_r-20, moon_y+shadow_r-20), fill=(20, 20, 100))
    # Yıldızlar
    for _ in range(50):
        sx, sy = random.randint(0, S), random.randint(CY, S)
        sr = random.randint(2, 6)
        night_draw.ellipse((sx-sr, sy-sr, sx+sr, sy+sr), fill=(255, 255, 255, 220))


    # ==========================================
    # MASKELEME VE BİRLEŞTİRME
    # ==========================================
    final_comp = Image.new("RGBA", (S, S), (0,0,0,0))

    # 1. Gündüz Dilimi
    mask_day = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask_day).pieslice((CX-R, CY-R, CX+R, CY+R), 180, 270, fill=255)
    final_comp.paste(day_layer, (0,0), mask=mask_day)

    # 2. Gün Batımı Dilimi
    mask_sunset = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask_sunset).pieslice((CX-R, CY-R, CX+R, CY+R), 270, 360, fill=255)
    final_comp.paste(sunset_layer, (0,0), mask=mask_sunset)

    # 3. Gece Dilimi
    mask_night = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask_night).pieslice((CX-R, CY-R, CX+R, CY+R), 0, 180, fill=255)
    final_comp.paste(night_layer, (0,0), mask=mask_night)

    # ==========================================
    # ÇERÇEVE VE AYIRAÇLAR
    # ==========================================
    separator_draw = ImageDraw.Draw(final_comp)
    sep_width = 16
    white = (255, 255, 255)

    separator_draw.line([(CX-R, CY), (CX+R, CY)], fill=white, width=sep_width)
    separator_draw.line([(CX, CY), (CX, CY-R)], fill=white, width=sep_width)
    
    frame_draw = ImageDraw.Draw(final_comp)
    frame_draw.ellipse((CX-R, CY-R, CX+R, CY+R), outline=white, width=sep_width*2)
    
    final_mask = Image.new("L", (S, S), 0)
    inner_R = R - sep_width
    ImageDraw.Draw(final_mask).ellipse((CX-inner_R, CY-inner_R, CX+inner_R, CY+inner_R), fill=255)
    ImageDraw.Draw(final_mask).ellipse((CX-R, CY-R, CX+R, CY+R), outline=255, width=sep_width*2)
    final_mask = final_mask.filter(ImageFilter.GaussianBlur(2))
    
    final_icon_clean = Image.new("RGBA", (S, S), (0,0,0,0))
    final_icon_clean.paste(final_comp, (0,0), mask=final_mask)

    # KAYDET
    icon_size = (256, 256)
    final_icon_resized = final_icon_clean.resize(icon_size, Image.Resampling.LANCZOS)
    final_icon_resized.save("final_icon.ico", format="ICO", sizes=[icon_size])
    print("✅ 'final_icon.ico' başarıyla oluşturuldu.")

if __name__ == "__main__":
    create_final_icon()