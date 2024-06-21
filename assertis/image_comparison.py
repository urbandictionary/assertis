from PIL import Image, ImageChops


def compare_images(img1_path, img2_path, sensitivity):
    "Compare two images and highlight differences."
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    reasons = []

    if img1.format != img2.format:
        reasons.append(f"Format changed from {img1.format} to {img2.format}")
    if img1.mode != img2.mode:
        reasons.append(f"Mode changed from {img1.mode} to {img2.mode}")
    if img1.size != img2.size:
        reasons.append(f"Size changed from {img1.size} to {img2.size}")

    if reasons:
        return False, None, reasons

    # Calculate the difference between the images
    diff = ImageChops.difference(img1, img2)

    # Convert the difference image to grayscale
    diff_mask = diff.convert("L")

    # Create an RGBA image to highlight the differences
    diff_highlight = Image.new("RGBA", img1.size, (0, 0, 0, 0))
    threshold = 0  # You can adjust the threshold to control sensitivity

    # Highlight the changed pixels in red
    for x in range(diff.width):
        for y in range(diff.height):
            if diff_mask.getpixel((x, y)) > threshold:
                diff_highlight.putpixel((x, y), (255, 0, 0, 255))  # Highlight in red

    # Calculate the extent of the change as a percentage of total pixels
    total_pixels = img1.size[0] * img1.size[1]
    changed_pixels = sum(1 for pixel in diff_mask.getdata() if pixel > threshold)
    change_extent = (changed_pixels / total_pixels) * 100
    reasons.append(f"Pixels changed with extent {change_extent:.2f}%")

    return change_extent <= sensitivity, diff_highlight, reasons
