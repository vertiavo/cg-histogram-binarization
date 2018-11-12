def change_to_simple_greyscale(image):
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (r, g, b) = pixels[i, j]
            mean = int((r + g + b) / 3)
            pixels[i, j] = (mean, mean, mean)

    return image


def perform_manual_binarization(image, threshold):
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (r, g, b) = pixels[i, j]
            if r < threshold:
                pixels[i, j] = (0, 0, 0)
            else:
                pixels[i, j] = (255, 255, 255)

    return image
