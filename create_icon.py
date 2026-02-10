from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with transparent background
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    shield_color = (31, 106, 165) # #1f6aa5 (Blue)
    pulse_color = (46, 204, 113)  # #2ecc71 (Green)
    dark_bg = (30, 30, 30)

    # Draw Shield Shape (Simple)
    # Points: TopLeft, TopRight, BottomCenter
    points = [
        (40, 40),   # TL
        (216, 40),  # TR
        (216, 160), # Right side down
        (128, 240), # Bottom point
        (40, 160)   # Left side down
    ]
    draw.polygon(points, fill=shield_color)

    # Draw Pulse Line (Heartbeat style)
    # Center line coordinates
    line_y = 120
    draw.line((60, line_y, 100, line_y), fill=pulse_color, width=12)
    draw.line((100, line_y, 115, line_y-40), fill=pulse_color, width=12) # Up
    draw.line((115, line_y-40, 140, line_y+40), fill=pulse_color, width=12) # Down
    draw.line((140, line_y+40, 155, line_y), fill=pulse_color, width=12) # Back to center
    draw.line((155, line_y, 196, line_y), fill=pulse_color, width=12)

    # Save as ICO
    img.save("icon.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Icon created: icon.ico")

if __name__ == "__main__":
    create_icon()
