from PIL import Image
def paste_image_on_background(base_image:Image, paste_image:Image, bbox)->Image:
    """
    Pastes one PIL image onto another using the provided bounding box.
    Preserves the aspect ratio of the pasted image.

    Args:
        base_image (Image): The base image as a PIL Image object.
        paste_image (Image): The image to paste as a PIL Image object with transparency.
        bbox (list): Bounding box [x1, y1, x2, y2] where:
            - (x1, y1) is the top-left corner.
            - (x2, y2) is the bottom-right corner.

    Returns:
        Image: The combined image with the pasted image.
    """
    # Validate the bounding box
    if len(bbox) != 4 or any(not isinstance(i, (int, float)) for i in bbox):
        raise ValueError("Bounding box must be a list of four numeric values [x1, y1, x2, y2].")

    # Calculate the position to paste the image (top-left corner of the bounding box)
    x1, y1, x2, y2 = map(int, bbox)  # Convert to integers
    paste_position = (x1, y1)

    # Get the size of the bounding box
    bbox_width = x2 - x1
    bbox_height = y2 - y1

    # Get the original size of the paste image
    paste_width, paste_height = paste_image.size

    # Calculate the aspect ratios
    aspect_ratio = paste_width / paste_height
    bbox_aspect_ratio = bbox_width / bbox_height

    # Determine new size while maintaining aspect ratio
    if bbox_aspect_ratio > aspect_ratio:
        # Bounding box is wider than the pasted image
        new_height = bbox_height
        new_width = int(new_height * aspect_ratio)
    else:
        # Bounding box is taller than the pasted image
        new_width = bbox_width
        new_height = int(new_width / aspect_ratio)

    # Resize the pasted image to fit the bounding box while maintaining aspect ratio
    paste_image = paste_image.resize((new_width, new_height), Image.LANCZOS)

    # Ensure the pasted image is in 'RGBA' mode to preserve transparency
    if paste_image.mode != 'RGBA':
        paste_image = paste_image.convert('RGBA')

    # Check if the pasted image fits within the base image dimensions
    if (x1 < 0 or y1 < 0 or x2 > base_image.width or y2 > base_image.height):
        raise ValueError("Bounding box is out of base image bounds.")

    # Paste the image onto the base image using the alpha channel as a mask
    base_image.paste(paste_image, paste_position, mask=paste_image)

    return base_image




from PIL import Image, ImageDraw, ImageFont

def draw_multiline_text_in_bbox(image: Image.Image, text: str, bbox: tuple, 
                                  font_path: str = "arial.ttf", 
                                  gradient_start: tuple = (100, 0, 0), 
                                  gradient_end: tuple = (0, 0, 100)) -> Image.Image:
    """
    Draws multiline text inside a given bounding box on the provided image with a 3D effect and gradient color.
    Args:
        image (Image.Image): The image to draw on.
        text (str): The text to be drawn, which can contain line breaks.
        bbox (tuple): The bounding box as (left, upper, right, lower).
        font_path (str): The path to the TTF font file to be used.
        gradient_start (tuple): The RGB color to start the gradient (default red).
        gradient_end (tuple): The RGB color to end the gradient (default blue).
    Returns:
        Image.Image: The image with the text drawn inside the bounding box.
    """
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    # Extract bounding box coordinates
    left, upper, right, lower = bbox
    bbox_width = int((right - left) * 0.9)
    bbox_height = int((lower - upper) * 0.9)
    
    # Set initial font size
    font_size = bbox_height // 2  # Start with a reasonable size

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default(font_size)

    # Reduce font size until the text fits in the bounding box
    while True:
        # Split the text into lines that fit within the bounding box width
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_bbox = draw.textbbox((left, upper), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= bbox_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)  # Add the last line

        # Calculate total text height
        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
        if total_text_height <= bbox_height:
            break
        font_size -= 1
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default(font_size)

    # Calculate starting y position to center the text vertically in the bbox
    y = upper + (bbox_height - total_text_height) / 2

    # Draw each line of text with 3D effect and gradient color
    for i, line in enumerate(lines):
        # 3D effect: draw shadow first
        shadow_offset = 0  # Change this for more or less shadow
        shadow_color = (50, 50, 50)  # Dark gray shadow color
        shadow_text_bbox = draw.textbbox((left + shadow_offset, y + shadow_offset), line, font=font)
        shadow_width = shadow_text_bbox[2] - shadow_text_bbox[0]
        # while(shadow_width<bbox_width):
        #     font_size+=1
        #     font = ImageFont.truetype(font_path, font_size)
        #     shadow_text_bbox = draw.textbbox((left + shadow_offset, y + shadow_offset), line, font=font)
        #     shadow_width = shadow_text_bbox[2] - shadow_text_bbox[0]
        shadow_x = left + shadow_offset  # Left align the shadow
        draw.text((shadow_x, y + shadow_offset), line, font=font, fill=shadow_color)

        # Calculate gradient color for the line
        r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * (i / len(lines)))
        g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * (i / len(lines)))
        b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * (i / len(lines)))
        gradient_color = (r, g, b)

        # Draw the main text with gradient color
        text_bbox = draw.textbbox((left, y), line, font=font)
        x = left  # Left align the text
        draw.text((x, y), line, font=font, fill=gradient_color)  # Use gradient color

        y += text_bbox[3] - text_bbox[1] + 5  # Move y position down for the next line

    return image
def draw_multiline_text_in_bbox_center(image: Image.Image, text: str, bbox: tuple, 
                                  font_path: str = "arial.ttf", 
                                  gradient_start: tuple = (100, 0, 0), 
                                  gradient_end: tuple = (0, 0, 100)) -> Image.Image:
    """
    Draws multiline text inside a given bounding box on the provided image with a 3D effect and gradient color.
    Args:
        image (Image.Image): The image to draw on.
        text (str): The text to be drawn, which can contain line breaks.
        bbox (tuple): The bounding box as (left, upper, right, lower).
        font_path (str): The path to the TTF font file to be used.
        gradient_start (tuple): The RGB color to start the gradient (default red).
        gradient_end (tuple): The RGB color to end the gradient (default blue).
    Returns:
        Image.Image: The image with the text drawn inside the bounding box.
    """
    draw = ImageDraw.Draw(image)
    left, upper, right, lower = bbox
    bbox_width = int((right - left) * 0.9)
    bbox_height = int((lower - upper) * 0.9)
    
    font_size = bbox_height // 2

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default(font_size)

    while True:
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_bbox = draw.textbbox((left, upper), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= bbox_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
        if total_text_height <= bbox_height:
            break
        font_size -= 1
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default(font_size)

    y = upper + (bbox_height - total_text_height) / 2

    for i, line in enumerate(lines):
        shadow_offset = 1  # Change this for more or less shadow
        shadow_color = (50, 50, 50)
        shadow_text_bbox = draw.textbbox((left + shadow_offset, y + shadow_offset), line, font=font)
        
        shadow_x = left + shadow_offset
#        draw.text((shadow_x, y + shadow_offset), line, font=font, fill=shadow_color)

        r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * (i / len(lines)))
        g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * (i / len(lines)))
        b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * (i / len(lines)))
        gradient_color = (r, g, b)

        text_bbox = draw.textbbox((left, y), line, font=font)
        line_width = text_bbox[2] - text_bbox[0]
        x = left + (bbox_width - line_width) / 2  # Center the line
        draw.text((x, y), line, font=font, fill=gradient_color)

        y += text_bbox[3] - text_bbox[1] + 5  # Move y position down for the next line

    return image
import cv2
import numpy as np
import easyocr
from PIL import Image

def remove_text_with_easyocr(pil_image):
    """
    Detects and removes text from a PIL image using EasyOCR and OpenCV.
    :param pil_image: Input PIL image.
    :return: Processed PIL image with text removed.
    """
    # Initialize EasyOCR Reader
    reader = easyocr.Reader(['en'])

    # Convert PIL image to NumPy array and then to BGR format
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Perform OCR to detect text
    results = reader.readtext(img)

    # Create a mask for the detected text
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    for (bbox, text, prob) in results:
        # Get the bounding box coordinates
        pts = np.array(bbox, dtype=np.int32)
        cv2.fillConvexPoly(mask, pts, 255)  # Fill the detected text area

    # Inpaint the image using the mask
    result = cv2.inpaint(img, mask, inpaintRadius=1, flags=cv2.INPAINT_NS)

    # Convert BGR to RGB for PIL
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Convert NumPy array back to PIL Image
    result_pil = Image.fromarray(result_rgb)

    return result_pil

# Example usage
# processed_image = remove_text_with_easyocr(pil_image)

from PIL import Image, ImageDraw, ImageFont

def create_rounded_rectangle(draw, bbox, radius, outline=None, fill=None):
    print(fill)
    # Create a mask for the rounded rectangle
    mask = Image.new('L', (int(bbox[2]) - int(bbox[0]), int(bbox[3] - bbox[1])), 0)
    draw_mask = ImageDraw.Draw(mask)

    # Draw the rounded rectangle on the mask
    draw_mask.rounded_rectangle([0, 0,int( bbox[2] - bbox[0]), int(bbox[3] - bbox[1])], radius, fill=fill)

    # Draw the filled rectangle
    if fill:
        draw.rectangle(bbox, fill=fill)

    # Draw the outline
    if outline:
        draw.rectangle(bbox, outline=outline)

    # Apply the mask
    draw.bitmap((bbox[0], bbox[1]), mask, fill=fill)

def create_button(image:Image, text, bbox, radius=15, icon_path='arrow-right-double-line.png', font_color='black', fill_color='white'):
    # Create a new image with the specified background color

    draw = ImageDraw.Draw(image)

    # Draw the rounded rectangle
    create_rounded_rectangle(draw, bbox, radius, fill=fill_color)

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
    text_x = int(bbox[0] + (bbox[2] - bbox[0] - text_width) / 2)
    text_y = int(bbox[1] + (bbox[3] - bbox[1] - text_height) / 2)

    # Draw the text
    draw.text((text_x, text_y), text, fill=font_color, font=font)

    # If an icon path is provided, load and draw the icon
    if icon_path:
        icon = Image.open(icon_path)
        icon = icon.resize((font_size, font_size))  # Resize icon to fit
        icon_x = int(bbox[2] - icon.width - 10)  # 10 pixels padding from the right
        icon_y = int(bbox[1] + (bbox[3] - bbox[1] - icon.height) / 2)  # Center vertically
        # Paste the icon on the image
        image.paste(icon, (icon_x,icon_y), icon.convert("RGBA"))  # Use RGBA to maintain transparency

    return image

# Example usage
