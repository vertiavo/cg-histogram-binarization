def calculate_stretch_lut(v_min, v_max, i_max=255):
    lut = []
    for i in range(i_max + 1):
        equation = int((i_max / (v_max - v_min)) * (i - v_min))

        if equation > 255:
            lut.append(255)
        elif equation < 0:
            lut.append(0)
        else:
            lut.append(equation)

    return lut


def check_min(r, g, b, r_min, g_min, b_min):
    if r < r_min: r_min = r
    if g < g_min: g_min = g
    if b < b_min: b_min = b

    return r_min, g_min, b_min


def check_max(r, g, b, r_max, g_max, b_max):
    if r > r_max: r_max = r
    if g > g_max: g_max = g
    if b > b_max: b_max = b

    return r_max, g_max, b_max


def calculate_distribution(pixels, width, height):
    r_dist, g_dist, b_dist = [0] * 256, [0] * 256, [0] * 256
    for i in range(width):
        for j in range(height):
            (r, g, b) = pixels[i, j]
            r = int(r)
            g = int(g)
            b = int(b)
            r_dist[r] += 1
            g_dist[g] += 1
            b_dist[b] += 1

    return r_dist, g_dist, b_dist


def calculate_equalization_lut(d):
    lut = []

    # find first not zero distribution value
    i = 0
    while d[i] == 0:
        i += 1
    d0_min = d[i]

    for i in range(256):
        lut.append(int(((d[i] - d0_min) / (1 - d0_min)) * (256 - 1)))

    return lut
