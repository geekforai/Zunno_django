from PIL import Image, ImageDraw, ImageFont

def create_rounded_rectangle(draw, bbox, radius, outline=None, fill=None):
    # Create a mask for the rounded rectangle
    mask = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 0)
    draw_mask = ImageDraw.Draw(mask)

    # Draw the rounded rectangle on the mask
    draw_mask.rounded_rectangle([0, 0, bbox[2] - bbox[0], bbox[3] - bbox[1]], radius, fill=255)

    # Draw the filled rectangle
    if fill:
        draw.rectangle(bbox, fill=fill)

    # Draw the outline
    if outline:
        draw.rectangle(bbox, outline=outline)

    # Apply the mask
    draw.bitmap((bbox[0], bbox[1]), mask, fill=255)

def create_button(image_size, text, bbox, radius=15, icon_path=None, border_color='black', fill_color='white'):
    # Create a new image with the specified background color
    image = Image.new('RGB', image_size, fill_color)
    draw = ImageDraw.Draw(image)

    # Draw the rounded rectangle
    create_rounded_rectangle(draw, bbox, radius, outline=border_color, fill=fill_color)

    # Set font size based on the bounding box height
    font_size = int((bbox[3] - bbox[1]) * 0.5)  # Use 50% of the bounding box height for font size
    # Load a specific font (if available) or use default
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text bounding box for centering
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate text position for centering
    text_x = bbox[0] + (bbox[2] - bbox[0] - text_width) / 2
    text_y = bbox[1] + (bbox[3] - bbox[1] - text_height) / 2

    # Draw the text
    draw.text((text_x, text_y), text, fill='black', font=font)

    # If an icon path is provided, load and draw the icon
    if icon_path:
        icon = Image.open(icon_path)
        icon = icon.resize((font_size, font_size))  # Resize icon to fit
        icon_x = bbox[2] - icon.width - 10  # 10 pixels padding from the right
        icon_y = bbox[1] + (bbox[3] - bbox[1] - icon.height) / 2  # Center vertically
        # Paste the icon on the image
        image.paste(icon, (int(icon_x), int(icon_y)), icon.convert("RGBA"))  # Use RGBA to maintain transparency

    return image

# Example usage
image = create_button((300, 100), 'Click Me', (50, 30, 200, 70), icon_path='arrow-right-double-line.png')  # Replace with your icon file
image.show()  # This will display the image
