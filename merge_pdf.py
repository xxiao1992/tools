import os
from pypdf import PdfReader, PdfWriter

# Letter size in points (1 inch = 72 points)
LETTER_WIDTH = 612.0   # 8.5 inches
LETTER_HEIGHT = 792.0  # 11 inches
TOLERANCE = 1.0        # points tolerance for size comparison

def scale_page_to_letter(page):
    """Scale a page to Letter size, preserving orientation."""
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    # Determine if page is landscape
    is_landscape = width > height

    if is_landscape:
        target_w, target_h = LETTER_HEIGHT, LETTER_WIDTH  # 792 x 612
    else:
        target_w, target_h = LETTER_WIDTH, LETTER_HEIGHT  # 612 x 792

    # Check if already correct Letter size (within tolerance)
    if (abs(width - target_w) <= TOLERANCE and
            abs(height - target_h) <= TOLERANCE):
        return page

    # Scale to fit, maintaining aspect ratio, centered
    scale = min(target_w / width, target_h / height)
    offset_x = (target_w - width * scale) / 2
    offset_y = (target_h - height * scale) / 2

    page.add_transformation([scale, 0, 0, scale, offset_x, offset_y])

    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (target_w, target_h)

    return page


filenames = [x for x in os.listdir() if ".pdf" in x.lower() and "To_print" not in x]
filenames = list(sorted(filenames))

files = []
outPdf = PdfWriter()
for filename in filenames:
    f = open(filename, "rb")
    files.append(f)
    file = PdfReader(f, strict=False)

    for page in file.pages:
        scaled_page = scale_page_to_letter(page)
        outPdf.add_page(scaled_page)

    n_page = len(file.pages)
    if n_page % 2 == 1:
        # Match blank page orientation to last page
        last_page = file.pages[-1]
        lw = float(last_page.mediabox.width)
        lh = float(last_page.mediabox.height)
        if lw > lh:
            outPdf.add_blank_page(width=LETTER_HEIGHT, height=LETTER_WIDTH)
        else:
            outPdf.add_blank_page(width=LETTER_WIDTH, height=LETTER_HEIGHT)

with open("To_print.pdf", "wb") as outStream:
    outPdf.write(outStream)

for x in files:
    x.close()
