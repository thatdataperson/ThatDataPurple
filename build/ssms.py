"""SQL Server Management Studio colours.

SSMS 22 runs on the VS 2026 shell, so the VS2022 extension installs on it too. SSMS adds its own
Fonts and Colors categories for query results, and only gives them values for VS's built-in Dark
theme, so without these the Messages tab and execution plan text fall back to Dark's grey (#2D2D30).
"""

CATEGORIES = {
    # Messages tab (and results to text)
    'TextSQLResults': ('{AD3737CA-26A1-47cb-A143-0EB0ECBC7FC9}', ('Plain Text', 'Error Message')),
    # Execution plan labels
    'ExecutionPlan': ('{90A03679-39CF-450f-A9E9-91DAADF17F38}', ('Text',)),
}


def categories(p):
    s, t, st = p['surface'], p['text'], p['status']
    colours = {  # name -> (background, foreground), matching the editor (ink1)
        'Plain Text': (s['ink1'], t['fg']),
        'Error Message': (s['ink1'], st['error']),
        'Text': (s['ink1'], t['fg']),
    }
    return {cat: (guid, {n: colours[n] for n in names}) for cat, (guid, names) in CATEGORIES.items()}


def xml(cats, indent='\t\t'):
    argb = lambda c: 'FF' + c.lstrip('#').upper()  # noqa: E731  vstheme is AARRGGBB
    lines = []
    for cat, (guid, colours) in cats.items():
        lines.append(f'{indent}<Category Name="{cat}" GUID="{guid}">')
        for n, (bg, fg) in colours.items():
            lines.append(f'{indent}\t<Color Name="{n}">')
            lines.append(f'{indent}\t\t<Background Type="CT_RAW" Source="{argb(bg)}" />')
            lines.append(f'{indent}\t\t<Foreground Type="CT_RAW" Source="{argb(fg)}" />')
            lines.append(f'{indent}\t</Color>')
        lines.append(f'{indent}</Category>')
    return '\n'.join(lines) + '\n'


def checks(cats, label):
    return [(f'{label} SSMS {cat} {n}', fg, bg, 4.5)
            for cat, (_, colours) in cats.items() for n, (bg, fg) in colours.items()]
