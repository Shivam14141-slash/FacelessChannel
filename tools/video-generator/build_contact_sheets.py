import os
from PIL import Image, ImageDraw, ImageFont

IMG_DIR = "Testing/output/images"
OUT_DIR = "Testing/output"

files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
print(f"{len(files)} images")

THUMB_W, THUMB_H = 320, 180
COLS = 6
PER_SHEET = 30  # 5 rows x 6 cols

for sheet_idx in range(0, len(files), PER_SHEET):
    chunk = files[sheet_idx:sheet_idx + PER_SHEET]
    rows = (len(chunk) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * THUMB_W, rows * (THUMB_H + 20)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, fname in enumerate(chunk):
        img = Image.open(os.path.join(IMG_DIR, fname)).resize((THUMB_W, THUMB_H))
        r, c = divmod(i, COLS)
        x, y = c * THUMB_W, r * (THUMB_H + 20)
        sheet.paste(img, (x, y))
        draw.text((x + 4, y + THUMB_H + 2), fname, fill="black")
    out_path = os.path.join(OUT_DIR, f"contact_sheet_{sheet_idx // PER_SHEET + 1:02d}.png")
    sheet.save(out_path)
    print("saved", out_path)
