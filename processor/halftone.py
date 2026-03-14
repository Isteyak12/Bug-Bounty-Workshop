from PIL import Image, ImageDraw


def apply_halftone(input_path, output_path, dot_spacing=10, style="classic"):
    """
    Convert an image to a halftone (dot pattern) version.

    Supported styles: classic (dots), diamond, line.

    1. Convert to appropriate color mode
    2. Divide into a grid of cells (dot_spacing x dot_spacing)
    3. For each cell, compute average brightness
    4. Draw a shape whose size is proportional to pixel intensity
    """
    width, height = Image.open(input_path).size
    output = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(output)
    max_radius = dot_spacing / 2

    if style == "classic":
        img = Image.open(input_path).convert("L")
        pixels = img.load()

        for y in range(0, height, dot_spacing):
            for x in range(0, width, dot_spacing):
                total = 0
                count = 0
                for cy in range(y, min(y + dot_spacing, height)):
                    for cx in range(x, min(x + dot_spacing, width)):
                        total += pixels[cx, cy]
                        count += 1
                avg = total / count

                # Halftones need larger marks for darker regions.
                darkness = 1 - (avg / 255)
                radius = max_radius * darkness

                if radius > 0.5:
                    center_x = x + dot_spacing // 2
                    center_y = y + dot_spacing // 2
                    draw.ellipse(
                        [
                            center_x - radius,
                            center_y - radius,
                            center_x + radius,
                            center_y + radius,
                        ],
                        fill=(0, 0, 0),
                    )

    elif style == "diamond":
        img_rgb = Image.open(input_path).convert("RGB")
        pixels = img_rgb.load()

        for y in range(0, height, dot_spacing):
            for x in range(0, width, dot_spacing):
                r_total = g_total = b_total = 0
                count = 0
                for cy in range(y, min(y + dot_spacing, height)):
                    for cx in range(x, min(x + dot_spacing, width)):
                        r, g, b = pixels[cx, cy]
                        r_total += r
                        g_total += g
                        b_total += b
                        count += 1

                avg_brightness = (r_total + g_total + b_total) / (count * 3)

                darkness = 1 - (avg_brightness / 255)
                radius = max_radius * darkness
                if radius > 0.5:
                    cx_pos = x + dot_spacing // 2
                    cy_pos = y + dot_spacing // 2
                    draw.polygon(
                        [
                            (cx_pos, cy_pos - radius),
                            (cx_pos + radius, cy_pos),
                            (cx_pos, cy_pos + radius),
                            (cx_pos - radius, cy_pos),
                        ],
                        fill=(0, 0, 0),
                    )

    elif style == "line":
        img = Image.open(input_path).convert("L")
        pixels = img.load()

        for y in range(0, height, dot_spacing):
            for x in range(0, width, dot_spacing):
                total = 0
                count = 0
                for cy in range(y, min(y + dot_spacing, height)):
                    for cx in range(x, min(x + dot_spacing, width)):
                        total += pixels[cx, cy]
                        count += 1
                avg = total / count

                darkness = 1 - (avg / 255)
                line_width = int(max_radius * 2 * darkness)
                if line_width > 0:
                    cx_pos = x + dot_spacing // 2
                    cy_pos = y + dot_spacing // 2
                    draw.line(
                        [(x, cy_pos), (x + dot_spacing, cy_pos)],
                        fill=(0, 0, 0),
                        width=line_width,
                    )

    output.save(output_path)
    return output_path
