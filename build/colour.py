"""Colour helpers shared by the theme builders: hex parsing, HSL, WCAG contrast."""
import colorsys


def rgb(hex_):
    h = hex_.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(r, g, b):
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(c))) for c in (r, g, b))


def hls(hex_):
    r, g, b = (c / 255 for c in rgb(hex_))
    return colorsys.rgb_to_hls(r, g, b)


def from_hls(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1, max(0, min(1, l)), max(0, min(1, s)))
    return to_hex(r * 255, g * 255, b * 255)


def luminance(hex_):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def blend(fg, bg, alpha):
    """Composite fg over bg at the given alpha (0-1)."""
    f, b = rgb(fg), rgb(bg)
    return to_hex(*(fc * alpha + bc * (1 - alpha) for fc, bc in zip(f, b)))


def lighten_until(fg, backgrounds, ratio):
    """Raise fg's lightness (keeping hue) until it meets ratio against every background."""
    h, l, s = hls(fg)
    out = fg
    while l < 1 and min(contrast(out, bg) for bg in backgrounds) < ratio:
        l = min(1, l + 0.01)
        out = from_hls(h, l, s)
    return out
