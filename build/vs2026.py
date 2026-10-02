"""Visual Studio 2026 shell colours.

VS 2026's redesigned (Fluent) UI reads its colours from new categories (Shell, ShellInternal,
EditorOverride) that a VS 2022-era .vstheme doesn't contain, so on their own those surfaces fall back
to the default light theme. This module takes VS 2026's dark defaults (templates/vs2026-shell-dark.json)
and recolours them to the palette: greys move onto the ink ramp, Microsoft's blue/cyan accents become
brand purples, and text becomes solid so contrast can be measured. VS 2022 ignores these categories.
"""
import json
import os

from colour import blend, contrast, rgb, to_hex

HERE = os.path.dirname(os.path.abspath(__file__))
DARK_FALLBACK = '{1ded0138-47ce-435e-84ef-9ec1f439b749}'  # VS's built-in Dark theme

# Grey level in the VS dark defaults → colour on the ink ramp. Greys in between are interpolated.
RAMP = [
    (0x0A, '#07031A'), (0x1C, '#0D0629'), (0x20, '#120A33'), (0x28, '#1B1048'), (0x2C, '#201354'),
    (0x33, '#271862'), (0x37, '#2B1C6B'), (0x3A, '#2E2070'), (0x42, '#36277E'), (0x45, '#3A2A85'),
    (0x75, '#6A5BB0'), (0x8A, '#8C84B8'), (0xA1, '#B3ABD6'), (0xFA, '#F7F5FD'),
]


def ramp(grey):
    if grey <= RAMP[0][0]:
        return RAMP[0][1]
    for (g0, c0), (g1, c1) in zip(RAMP, RAMP[1:]):
        if grey <= g1:
            return blend(c1, c0, (grey - g0) / (g1 - g0))
    return RAMP[-1][1]


def overrides(p):
    s, t, st, b = p['surface'], p['text'], p['status'], p['brand']
    solid = lambda c: c + 'FF'  # noqa: E731
    a = lambda c, alpha: c + alpha  # noqa: E731
    o = {
        # Accent: brand light purple, with dark text on it (brand purple is too dark to see on ink).
        'AccentFillDefault': solid(t['accent']), 'AccentFillSecondary': a(t['accent'], 'E5'),
        'AccentFillTertiary': a(t['accent'], 'CC'), 'AccentFillSenary': a(t['accent'], '1F'),
        'AccentFillAlt': solid(t['link']),
        'AccentTextFillPrimary': solid(t['link']), 'AccentTextFillSecondary': solid(t['link']),
        'AccentTextFillTertiary': solid(t['accent']),
        'TextOnAccentFillPrimary': solid(b['dark']), 'TextOnAccentFillSecondary': a(b['dark'], 'B0'),
        'AccentFillSelectedTextBackground': solid(s['primary']), 'TextOnAccentFillSelectedText': solid(t['bright']),
        'AccentFillSelectedTextBackgroundSubtle': a(t['accent'], '66'),
        # Text, made solid so it can be checked
        'TextFillPrimary': solid(t['fg']), 'TextFillSecondary': solid(t['muted']),
        'TextFillTertiary': solid(t['subtle']), 'TextFillDisabled': solid(t['disabled']),
        'HyperlinkFillPrimary': solid(t['link']), 'HyperlinkFillSecondary': solid(t['accent']),
        'HyperlinkFillTertiary': a(t['accent'], 'E6'), 'HyperlinkFillDisabled': solid(t['disabled']),
        # Status colours
        'SystemFillAttention': solid(st['info']), 'SystemFillCaution': solid(st['warning']),
        'SystemFillCritical': solid(st['error']), 'SystemFillSuccess': solid(st['success']),
        'SystemFillCautionBackground': solid(blend(st['warning'], s['ink1'], 0.18)),
        'SystemFillCriticalBackground': solid(blend(st['error'], s['ink1'], 0.18)),
        'SystemFillSuccessBackground': solid(blend(st['success'], s['ink1'], 0.18)),
        'SystemFillSolidNeutral': solid(t['disabled']),
        'FocusStrokeOuter': solid(t['bright']),
        # Window frame, tabs, status bar (ShellInternal)
        'EnvironmentBackground': solid(s['ink0']), 'EnvironmentBody': solid(s['ink0']),
        'EnvironmentBodyText': solid(t['fg']),
        'EnvironmentHeader': solid(s['ink0']), 'EnvironmentHeaderInactive': solid(s['ink0']),
        'EnvironmentTab': solid(s['ink1']), 'EnvironmentTabInactive': solid(s['ink0']),
        'EnvironmentBorder': solid(s['primary']), 'EnvironmentBorderInactive': solid(s['border']),
        'EnvironmentLogo': solid(t['accent']), 'EnvironmentIndicator': a(t['accent'], '66'),
        'StatusBarBackgroundFillRest': solid(b['purple']),
        'StatusBarBackgroundFillBuilding': solid(s['primaryHover']),
        'StatusBarBackgroundFillDebugging': '8A2A63FF',
        'StatusBarBackgroundFillSolutionLoading': solid(s['selection']),
        'StatusBarTextFillRest': solid(t['bright']), 'StatusBarTextFillBuilding': solid(t['bright']),
        'StatusBarTextFillDebugging': solid(t['bright']), 'StatusBarTextFillSolutionLoading': solid(t['bright']),
        'StatusBarTextFillDisabled': 'FFFFFFA0',
        # Pop-ups (EditorOverride)
        'PopupBackground': solid(s['ink2']), 'PopupBorder': solid(s['border']),
        'PopupHyperlink': solid(t['link']), 'PopupSelectedBackground': solid(s['selection']),
        'PopupSelectedText': solid(t['bright']), 'PopupText': solid(t['fg']), 'PopupSubtleText': solid(t['muted']),
    }
    return {k: v.lstrip('#').upper() for k, v in o.items()}


def recolour(value, name, o):
    """value is RRGGBBAA. Returns RRGGBBAA."""
    if name in o:
        return o[name]
    rgb_hex, alpha = value[:6], value[6:]
    r, g, b_ = rgb('#' + rgb_hex)
    if rgb_hex in ('FFFFFF', '000000'):
        return value  # translucent white/black overlays work on purple as they do on grey
    if r == g == b_:
        return ramp(r).lstrip('#') + alpha
    return value


def categories(p):
    with open(os.path.join(HERE, 'templates', 'vs2026-shell-dark.json'), encoding='utf-8') as f:
        data = json.load(f)
    o = overrides(p)
    out = {}
    for cat, c in data['categories'].items():
        out[cat] = (c['guid'], {n: recolour(v, n, o) for n, v in c['colors'].items()})
    return out


def xml(cats, indent='\t\t'):
    lines = []
    for cat, (guid, colors) in cats.items():
        lines.append(f'{indent}<Category Name="{cat}" GUID="{guid}">')
        for n, v in colors.items():
            lines.append(f'{indent}\t<Color Name="{n}">')
            lines.append(f'{indent}\t\t<Background Type="CT_RAW" Source="{v[6:]}{v[:6]}" />')  # vstheme is AARRGGBB
            lines.append(f'{indent}\t</Color>')
        lines.append(f'{indent}</Category>')
    return '\n'.join(lines) + '\n'


def checks(cats, label):
    flat = {}
    for _, colors in cats.values():
        flat.update(colors)
    solid = lambda n: '#' + flat[n][:6]  # noqa: E731
    surfaces = ['SolidBackgroundFillBase', 'SolidBackgroundFillSecondary', 'SolidBackgroundFillTertiary',
                'SolidBackgroundFillQuaternary', 'SurfaceBackgroundFillDefault', 'EnvironmentBackground',
                'EnvironmentTab', 'PopupBackground']
    pairs = [(fg, bg, 4.5) for fg in ('TextFillPrimary', 'TextFillSecondary', 'TextFillTertiary',
                                      'AccentTextFillPrimary', 'AccentTextFillTertiary', 'HyperlinkFillPrimary',
                                      'HyperlinkFillSecondary', 'EnvironmentBodyText') for bg in surfaces]
    pairs += [(fg, bg, 3.0) for fg in ('AccentFillDefault', 'FocusStrokeOuter', 'SystemFillCritical',
                                       'SystemFillCaution', 'SystemFillSuccess', 'SystemFillAttention') for bg in surfaces]
    pairs += [
        ('TextOnAccentFillPrimary', 'AccentFillDefault', 4.5),
        ('TextOnAccentFillSelectedText', 'AccentFillSelectedTextBackground', 4.5),
        ('PopupText', 'PopupBackground', 4.5), ('PopupSubtleText', 'PopupBackground', 4.5),
        ('PopupHyperlink', 'PopupBackground', 4.5), ('PopupSelectedText', 'PopupSelectedBackground', 4.5),
    ]
    for state in ('Rest', 'Building', 'Debugging', 'SolutionLoading'):
        pairs.append((f'StatusBarTextFill{state}', f'StatusBarBackgroundFill{state}', 4.5))
    return [(f'{label} 2026 {f} on {b}', solid(f), solid(b), r) for f, b, r in pairs]


__all__ = ['DARK_FALLBACK', 'categories', 'xml', 'checks', 'contrast', 'to_hex']
