"""Re-colours a Visual Studio .vstheme against palette.json.

The .vstheme files are full Color Theme Editor exports (~360 colours across ~80 categories), so they
are re-coloured in place rather than generated: every Source value is remapped by role (surface,
border or text, worked out from the colour's name), the editor classifications are set explicitly,
and every text colour is then lifted until it meets WCAG AA against the surfaces it can sit on.
Structure, names and GUIDs are left untouched.
"""
import re

from colour import blend, contrast, hls, from_hls, lighten_until

EDITOR_CATEGORIES = {
    'Text Editor Language Service Items',
    'Text Editor Text Manager Items',
    'Text Editor Text Marker Items',
    'PythonTools',  # the MEF classification category {75a05685-...}; the exporter mislabels it
}

TEXT_WORDS = ('text', 'glyph', 'foreground', 'hyperlink', 'link', 'label', 'caption', 'watermark',
              'arrow', 'checkmark')
# Words that usually mean text, unless the name also says it's a surface (ToolboxHeadingBegin,
# PopupSectionHeaderGradientEnd, ToolboxIconShadow...).
WEAK_TEXT_WORDS = ('icon', 'heading', 'header', 'h1', 'h2', 'title')
SURFACE_HINTS = ('begin', 'end', 'middle', 'gradient', 'accent', 'background', 'highlight', 'shadow',
                 'tab', 'bar', 'button', 'row', 'panel')
BORDER_WORDS = ('border', 'separator', 'line', 'rule', 'stroke', 'outline', 'divider', 'snaplines', 'grip')
STATE_WORDS = ('selected', 'pressed', 'mouseover', 'mousedown', 'hover', 'hot', 'checked', 'focused', 'down')

# Old surface purples → new surfaces, keeping the original's dark-to-light order (menus < editor <
# chrome < hover < pressed) so hover and selected states stay distinguishable. Unlisted ones fall
# back to a lightness ramp.
BRAND_SURFACES = {
    '160B91': 'ink0', '221C97': 'ink0', '2D16AF': 'ink1', '482DC2': 'ink1', '4320CC': 'ink2',
    '593ED3': 'ink3', '4E428F': 'ink3', '6A4EDA': 'selection',
}

# Environment entries where the generic mapping isn't enough.
SCROLL_THUMB, SCROLL_THUMB_HOVER = '#6A5BB0', '#8577C8'
ENVIRONMENT = {
    'StatusBarDefault': 'primary', 'StatusBarNoSolution': 'primary', 'StatusBarBuilding': 'primaryHover',
    'StatusBarDebugging': '#8A2A63', 'StatusBarHighlight': 'primaryHover',
    'CommandBarMenuItemMouseOver': 'primary', 'CommandBarMenuItemMouseOverBorder': 'primary',
    'FileTabProvisionalSelectedActive': '#5B2C9E', 'FileTabProvisionalSelectedActiveBorder': '#5B2C9E',
    'ScrollBarThumbBackground': SCROLL_THUMB, 'ScrollBarThumbBorder': SCROLL_THUMB,
    'ScrollBarThumbGlyph': SCROLL_THUMB, 'FileTabScrollBarThumb': SCROLL_THUMB,
    'ScrollBarThumbMouseOverBackground': SCROLL_THUMB_HOVER, 'ScrollBarThumbMouseOverBorder': SCROLL_THUMB_HOVER,
    'ScrollBarThumbGlyphMouseOverBorder': SCROLL_THUMB_HOVER, 'FileTabScrollBarThumbHover': SCROLL_THUMB_HOVER,
    'ScrollBarThumbPressedBackground': 'accent', 'ScrollBarThumbPressedBorder': 'accent',
    'ScrollBarThumbGlyphPressedBorder': 'accent', 'FileTabScrollBarThumbPressed': 'accent',
}


def kind(hex_):
    h, l, s = hls(hex_)
    deg = h * 360
    if s < 0.15 or l < 0.06 or l > 0.95:
        return 'neutral'
    if 220 <= deg <= 295:
        return 'brand'
    if 295 < deg <= 352:
        return 'pink'
    if 190 <= deg < 220:
        return 'blue'
    return 'semantic'


def is_active(n):
    return any(w in n for w in STATE_WORDS) or ('active' in n and 'inactive' not in n)


def role(name, tag, has_pair):
    n = name.lower().replace(' ', '')
    if has_pair:
        return 'surface' if tag == 'Background' else 'text'
    if any(w in n for w in TEXT_WORDS) and not (('titlebar' in n or 'background' in n) and 'text' not in n):
        return 'text'
    if any(w in n for w in BORDER_WORDS):
        return 'border'
    if any(w in n for w in WEAK_TEXT_WORDS) and not any(w in n for w in SURFACE_HINTS):
        return 'text'
    return 'surface'


class Recolourer:
    def __init__(self, p):
        self.p = p
        self.s, self.t, self.x, self.st = p['surface'], p['text'], p['syntax'], p['status']
        self.checks = []
        self.editor = self._editor_overrides()

    # ---- generic roles -------------------------------------------------------------------------
    def surface(self, old, name):
        s, n, k = self.s, name.lower(), kind(old)
        if k in ('pink', 'blue'):
            return s['primaryHover'] if ('hover' in n or 'mouseover' in n or 'hot' in n) else s['primary']
        if k == 'semantic':
            return s['ink2'] if hls(old)[1] > 0.75 else blend(old, s['ink1'], 0.45)
        key = old[1:].upper()
        if key in BRAND_SURFACES:
            return s[BRAND_SURFACES[key]]
        l = hls(old)[1]
        if k == 'brand':
            return s['ink0'] if l < 0.35 else s['ink1'] if l < 0.42 else s['ink2'] if l < 0.5 else s['ink3'] if l < 0.56 else s['selection']
        if l < 0.13:
            return s['ink0']
        if l < 0.22:
            return s['ink1']
        if l < 0.33:
            return s['ink2']
        if l < 0.45:
            return s['ink3']
        if l < 0.6:
            return s['selection']
        return s['ink2']  # light popups/tooltips become dark widgets

    def border(self, old, name):
        k, n = kind(old), name.lower()
        if k in ('pink', 'blue') or is_active(n):
            return self.t['accent']
        if k == 'semantic':
            return lighten_until(old, [self.s['ink1']], 3.0)
        return self.s['border']

    def text(self, old, name, bgs=None):
        t, s, n, k = self.t, self.s, name.lower(), kind(old)
        if 'disabled' in n:
            return t['disabled']
        if k in ('pink', 'blue') or 'hyperlink' in n or 'link' in n:
            new = t['link']
        elif k == 'neutral':
            l = hls(old)[1]
            new = t['bright'] if l > 0.97 else from_hls(252 / 360, l, 0.30)
        else:
            new = old
        if bgs is None:
            bgs = [s['ink3'], s['selection']]
            if is_active(n):
                bgs += [s['primary'], s['primaryHover']]
                if k in ('pink', 'blue'):
                    new = t['bright']
        return lighten_until(new, bgs, 4.5)

    # ---- editor --------------------------------------------------------------------------------
    def _editor_overrides(self):
        s, t, x, st = self.s, self.t, self.x, self.st
        B, F = 'Background', 'Foreground'
        o = {
            # Text Manager
            'Plain Text': {B: s['ink1'], F: t['fg']},
            'Selected Text': {B: s['selection']},
            'Inactive Selected Text': {B: s['ink3']},
            'Indicator Margin': {B: s['ink1']},
            'Visible Whitespace': {F: '#4A3C8C'},
            'Line Number': {B: s['ink1'], F: t['lineNumber']},
            'Caret (Primary)': {F: t['bright']},
            'Caret (Secondary)': {F: t['accent']},
            'CurrentLineActiveFormat': {B: s['ink2']},
            # Language Service
            'Keyword': {F: x['keyword']}, 'Comment': {F: x['comment']}, 'Identifier': {F: t['fg']},
            'String': {F: x['string']}, 'Number': {F: x['number']}, 'Text': {F: t['fg']},
            'Error': {F: st['error']}, 'Operator': {F: x['operator']}, 'Literal': {F: x['number']},
            'Type': {F: x['type']}, 'Excluded Code': {F: t['disabled']},
            'Preprocessor Keyword': {F: x['escape']}, 'preprocessor text': {F: t['fg']},
            'punctuation': {F: x['operator']}, 'string - verbatim': {F: x['string']},
            'string - escape character': {F: x['escape']},
            'XML Comment': {F: x['comment']}, 'XML CData Section': {F: x['string']},
            'XML Text': {F: t['fg']}, 'XML Keyword': {F: x['keyword']}, 'XML Delimiter': {F: x['operator']},
            'XML Name': {F: x['tag']}, 'XML Attribute': {F: x['type']}, 'XML Attribute Value': {F: x['string']},
            'XML Attribute Quotes': {F: x['string']}, 'XML Processing Instruction': {F: x['keyword']},
            'XSLT Keyword': {F: x['keyword']},
            'XAML Text': {F: t['fg']}, 'XAML Keyword': {F: x['keyword']}, 'XAML Delimiter': {F: x['operator']},
            'XAML Comment': {F: x['comment']}, 'XAML Name': {F: x['tag']}, 'XAML Attribute': {F: x['type']},
            'XAML Attribute Value': {F: x['string']}, 'XAML Attribute Quotes': {F: x['string']},
            'XAML CData Section': {F: x['string']}, 'XAML Processing Instruction': {F: x['keyword']},
            'XAML Markup Extension Class': {F: x['function']},
            'XAML Markup Extension Parameter Name': {F: x['property']},
            'XAML Markup Extension Parameter Value': {F: x['string']},
            'SQL Stored Procedure': {F: x['function']}, 'SQL System Table': {F: x['type']},
            'SQL System Function': {F: x['function']}, 'SQL Operator': {F: x['operator']},
            'SQL String': {F: x['string']}, 'SQLCMD Command': {B: s['ink2'], F: x['keyword']},
            # Roslyn / MEF classifications
            'class name': {F: x['type']}, 'record class name': {F: x['type']}, 'record struct name': {F: x['type']},
            'delegate name': {F: x['type']}, 'enum name': {F: x['type']}, 'interface name': {F: x['type']},
            'module name': {F: x['type']}, 'struct name': {F: x['type']}, 'type parameter name': {F: x['type']},
            'method name': {F: x['function']}, 'extension method name': {F: x['function']},
            'property name': {F: x['property']}, 'field name': {F: x['property']}, 'event name': {F: x['property']},
            'enum member name': {F: x['number']}, 'constant name': {F: x['number']},
            'local name': {F: t['fg']}, 'parameter name': {F: x['parameter']},
            'namespace name': {F: x['namespace']}, 'label name': {F: x['escape']},
            'keyword - control': {F: x['keyword']}, 'operator - overloaded': {F: x['function']},
            'inline hints': {B: s['ink2'], F: t['muted']},
            'xml doc comment - text': {F: x['comment']}, 'xml doc comment - comment': {F: x['comment']},
            'xml doc comment - delimiter': {F: x['comment']}, 'xml doc comment - name': {F: x['keyword']},
            'xml doc comment - attribute name': {F: x['keyword']},
            'xml doc comment - attribute quotes': {F: x['comment']},
            'xml doc comment - attribute value': {F: x['comment']},
            'xml doc comment - cdata section': {F: x['comment']},
            'xml doc comment - entity reference': {F: x['escape']},
            'xml doc comment - processing instruction': {F: x['comment']},
            'XML Doc Comment': {F: x['comment']}, 'XML Doc Tag': {F: x['keyword']},
            'regex - text': {F: x['string']}, 'regex - comment': {F: x['comment']},
            'regex - character class': {F: x['escape']}, 'regex - anchor': {F: x['keyword']},
            'regex - quantifier': {F: x['number']}, 'regex - grouping': {F: x['escape']},
            'regex - alternation': {F: x['keyword']}, 'regex - self escaped character': {F: x['escape']},
            'regex - other escape': {F: x['escape']},
            'CSS Keyword': {F: x['keyword']}, 'CSS Comment': {F: x['comment']}, 'CSS Selector': {F: x['tag']},
            'CSS Property Name': {F: x['property']}, 'CSS Property Value': {F: x['number']},
            'CSS String Value': {F: x['string']},
            'HTML Attribute Name': {F: x['type']}, 'HTML Attribute Value': {F: x['string']},
            'HTML Comment': {F: x['comment']}, 'HTML Element Name': {F: x['tag']},
            'HTML Entity': {F: x['escape']}, 'HTML Operator': {F: x['operator']},
            'HTML Tag Delimiter': {F: x['operator']}, 'HTML Server-Side Script': {B: s['ink2'], F: t['fg']},
            'JSON Property Name': {F: x['property']},
            'RazorDirective': {F: x['keyword']}, 'RazorCode': {B: s['ink2']},
            'RazorTagHelperElement': {F: x['type']}, 'RazorTagHelperAttribute': {F: x['type']},
            'RazorComponentElement': {F: x['type']}, 'RazorComponentAttribute': {F: x['type']},
            'RazorDirectiveAttribute': {F: x['keyword']},
            'urlformat': {F: t['link']}, 'NavigableSymbolFormat': {F: t['link']},
            'FSharp.Function': {F: x['function']}, 'FSharp.MutableVar': {F: x['property']},
            'FSharp.Printf': {F: x['escape']}, 'FSharp.DisposableType': {F: x['type']},
            'U-SQL - Keyword': {F: x['keyword']}, 'U-SQL - Comment': {F: x['comment']},
            'U-SQL - String': {F: x['string']}, 'U-SQL - Number': {F: x['number']},
            'U-SQL - ClassName': {F: x['type']}, 'U-SQL - BuiltInFunction': {F: x['function']},
            'U-SQL - Parameter': {F: x['parameter']}, 'U-SQL - Text': {F: t['fg']},
            'U-SQL - Identifier': {F: t['fg']}, 'U-SQL - Error': {F: st['error']},
            'U-SQL - Preprocess': {F: x['escape']},
            # Highlights and markers
            'brace matching': {B: '#4A3C8C'},
            'Brace Matching (Rectangle)': {B: '#4A3C8C'},
            'MarkerFormatDefinition/HighlightedReference': {B: '#3A2A85'},
            'MarkerFormatDefinition/HighlightedWrittenReference': {B: '#4A2A6B'},
            'MarkerFormatDefinition/HighlightedDefinition': {B: '#3A2A85'},
            'MarkerFormatDefinition/FindHighlight': {B: '#5A3FB0'},
            'Definition Window Background': {B: s['ink0']},
            'Refactoring Background': {B: s['ink0']},
            'Peek Background': {B: s['ink0']}, 'Peek Background Unfocused': {B: s['ink0']},
            'Peek Focused Border': {B: t['accent']}, 'Peek Label Text': {F: t['bright']},
            'Code Snippet Field': {B: s['ink3']}, 'Code Snippet Field (Selected)': {B: s['selection']},
            'Read-Only Region': {B: s['ink2']},
            'Current Statement': {B: '#FFE08A', F: '#0D0629'},
            'Executing Thread IP': {B: '#FFCB6B', F: '#0D0629'},
            'Call Return': {B: '#9DD8D0', F: '#0D0629'},
            'Breakpoint (Enabled)': {B: '#8A2A3E', F: t['bright']},
            'Bookmark': {B: '#6B5A2A'},
            'compiler error': {F: st['error']}, 'syntax error': {F: st['error']},
            'other error': {F: x['keyword']}, 'compiler warning': {F: st['warning']},
            'hinted suggestion': {F: t['muted']}, 'Error Message': {F: st['error']},
            'Track Changes before save': {B: st['warning']}, 'Track Changes after save': {B: st['success']},
            'SQL DML Marker': {F: t['accent']},
            'deltadiff.add.line': {B: blend(st['success'], s['ink1'], 0.14)},
            'deltadiff.remove.line': {B: blend(st['error'], s['ink1'], 0.14)},
            'deltadiff.add.word': {B: blend(st['success'], s['ink1'], 0.30)},
            'deltadiff.remove.word': {B: blend(st['error'], s['ink1'], 0.30)},
            'data.tools.diff.add.line': {B: blend(st['success'], s['ink1'], 0.14)},
            'data.tools.diff.remove.line': {B: blend(st['error'], s['ink1'], 0.14)},
            'data.tools.diff.add.word': {B: blend(st['success'], s['ink1'], 0.30)},
            'data.tools.diff.remove.word': {B: blend(st['error'], s['ink1'], 0.30)},
            'Python Interactive - Black': {F: '#4A3C8C'}, 'Python Interactive - DarkGray': {F: t['subtle']},
            'Python Interactive - Gray': {F: t['muted']}, 'Python Interactive - White': {F: t['bright']},
            'Python Interactive - Red': {F: '#FFA3AE'}, 'Python Interactive - DarkRed': {F: st['error']},
            'Python Interactive - Green': {F: '#C6F0C2'}, 'Python Interactive - DarkGreen': {F: x['string']},
            'Python Interactive - Yellow': {F: '#FFE3A8'}, 'Python Interactive - DarkYellow': {F: x['type']},
            'Python Interactive - Blue': {F: '#A9D8FF'}, 'Python Interactive - DarkBlue': {F: x['function']},
            'Python Interactive - Magenta': {F: '#DCD2FF'}, 'Python Interactive - DarkMagenta': {F: x['keyword']},
            'Python Interactive - Cyan': {F: '#A3EEE5'}, 'Python Interactive - DarkCyan': {F: x['escape']},
        }
        for n in ('Breakpoint - Advanced (Enabled)', 'Breakpoint - Mapped (Enabled)', 'Breakpoint (Warning)',
                  'Breakpoint - Advanced (Warning)', 'Breakpoint - Mapped (Warning)', 'Breakpoint (Error)',
                  'Breakpoint - Mapped (Error)', 'Breakpoint - Advanced (Error)'):
            o[n] = o['Breakpoint (Enabled)']
        return o

    def editor_value(self, old, name, tag):
        """Colour for an editor-category entry that has no explicit override."""
        s = self.s
        if tag == 'Background':
            if kind(old) in ('neutral', 'brand', 'pink', 'blue'):
                return s['ink3'] if hls(old)[1] < 0.5 else s['selection']
            return blend(old, s['ink1'], 0.35)
        if kind(old) == 'pink':
            old = self.x['property']
        elif kind(old) == 'neutral':
            old = from_hls(252 / 360, hls(old)[1], 0.25)
        return lighten_until(old, [s['ink1'], s['ink2']], 4.5)

    # ---- driver --------------------------------------------------------------------------------
    def recolour(self, xml, label):
        source_re = re.compile(r'<(Background|Foreground) Type="(\w+)" Source="([0-9A-Fa-f]{8})"')

        def do_color(cat, m):
            name, body = m.group(1), m.group(2)
            parts = [(tg, ty, src) for tg, ty, src in source_re.findall(body)]
            live = [p for p in parts if p[1] != 'CT_INVALID' and p[2][:2] != '00']
            has_pair = len({p[0] for p in live}) == 2
            override = self.editor.get(name) if cat in EDITOR_CATEGORIES else None
            if cat == 'Environment' and name in ENVIRONMENT:
                v = ENVIRONMENT[name]
                v = self.s.get(v) or self.t.get(v) or v
                override = {'Background': v}
            new_vals = {}
            for tag, ty, src in parts:
                alpha, old = src[:2].upper(), '#' + src[2:].upper()
                if override and tag in override:
                    new = override[tag]
                    if ty == 'CT_INVALID':
                        alpha = 'FF'
                elif ty == 'CT_INVALID' or alpha == '00':
                    continue
                elif ty != 'CT_RAW':
                    continue  # CT_SYSCOLOR, CT_AUTOMATIC etc. refer to system colours, leave them
                elif cat in EDITOR_CATEGORIES:
                    new = self.editor_value(old, name, tag)
                else:
                    r = role(name, tag, has_pair)
                    new = self.surface(old, name) if r == 'surface' else self.border(old, name) if r == 'border' else self.text(old, name)
                new_vals[tag] = (alpha, new)

            # Paired fg/bg in one entry: make sure the pair itself passes.
            if 'Background' in new_vals and 'Foreground' in new_vals and new_vals['Background'][0] == 'FF':
                bg = new_vals['Background'][1]
                fa, fg = new_vals['Foreground']
                if 'disabled' not in name.lower():
                    if contrast(fg, bg) < 4.5:
                        fg = lighten_until(fg, [bg], 4.5) if contrast('#FFFFFF', bg) >= 4.5 else '#0D0629'
                    new_vals['Foreground'] = (fa, fg)
                    self.checks.append((f'{label} {cat}/{name}', fg, bg, 4.5))

            def sub(pm):
                tag, ty, src = pm.group(1), pm.group(2), pm.group(3)
                if tag not in new_vals:
                    return pm.group(0)
                alpha, new = new_vals[tag]
                if ty == 'CT_INVALID':
                    ty = 'CT_RAW'
                return f'<{tag} Type="{ty}" Source="{alpha}{new[1:].upper()}"'
            return m.group(0).replace(body, source_re.sub(sub, body))

        def do_cat(m):
            cat = m.group(1)
            return re.sub(r'<Color Name="([^"]+)">(.*?)</Color>', lambda cm: do_color(cat, cm), m.group(0), flags=re.S)

        out = re.sub(r'<Category Name="([^"]+)".*?</Category>', do_cat, xml, flags=re.S)
        self._audit_editor(out, label)
        return out

    def _audit_editor(self, xml, label):
        """Every editor foreground must pass on the editor background, current line and selection."""
        s = self.s
        for cat in EDITOR_CATEGORIES:
            m = re.search(r'<Category Name="%s".*?</Category>' % re.escape(cat), xml, re.S)
            if not m:
                continue
            for cm in re.finditer(r'<Color Name="([^"]+)">(.*?)</Color>', m.group(0), re.S):
                name = cm.group(1)
                bg = re.search(r'<Background Type="CT_RAW" Source="FF([0-9A-F]{6})"', cm.group(2))
                fg = re.search(r'<Foreground Type="CT_RAW" Source="FF([0-9A-F]{6})"', cm.group(2))
                if not fg or 'Disabled' in name or name in ('Visible Whitespace', 'Python Interactive - Black', 'Excluded Code'):
                    continue
                f = '#' + fg.group(1)
                if bg:
                    self.checks.append((f'{label} editor {name}', f, '#' + bg.group(1), 4.5))
                else:
                    for b in (s['ink1'], s['ink2']):
                        self.checks.append((f'{label} editor {name}', f, b, 4.5))
