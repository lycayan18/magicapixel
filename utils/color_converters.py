def hsv2rgb(h: float, s: float, v: float):
    hi = int(h / 60) % 6
    vmin = (1.0 - s) * v
    a = (v - vmin) * (h % 60) / 60
    vinc = vmin + a
    vdec = v - a

    return [
        (v, vinc, vmin),  # for hi = 0
        (vdec, v, vmin),  # for hi = 1
        (vmin, v, vinc),  # for hi = 2
        (vmin, vdec, v),  # for hi = 3
        (vinc, vmin, v),  # for hi = 4
        (v, vmin, vdec)   # for hi = 5
    ][hi]


def convert(channels: tuple, mode: str) -> tuple[int, int, int, int]:
    if mode == "RGBA":
        return channels
    elif mode == "RGB":
        return (channels[0], channels[1], channels[2], 255)
    else:
        return (0, 0, 0, 0)
