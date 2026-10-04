"""Browser and mail themes: Chrome (also Edge), Firefox and Thunderbird.

All three share one layout: the window frame and background tabs are the darkest ink, the selected tab and
toolbar are brand purple, and the address/search field is dark ink with a light purple outline (dark ink
alone is only about 2:1 against brand purple). Firefox and Thunderbird use the same manifest format;
Thunderbird also reads the sidebar_* keys for its folder pane and message list.
"""
import json

from colour import blend, rgb

VERSION = '2026.10.0'
AUTHOR = 'That Data Person Limited (www.thatdataperson.com)'
THUNDERBIRD_ID = 'thatdatapurple@thatdataperson.com'
FIREFOX_ID = '{84d20a3f-e209-4307-8636-7d33094c916b}'  # the ID addons.mozilla.org gave the first upload
# Firefox asks every add-on to declare what it collects; a theme collects nothing.
NO_DATA = {'required': ['none']}


def roles(p):
    s, t, st = p['surface'], p['text'], p['status']
    return {
        'frame': s['ink0'], 'frameInactive': s['ink1'], 'frameIncognito': '#07031A',
        'tabText': t['bright'], 'backgroundTabText': t['muted'],
        'toolbar': s['primary'], 'toolbarText': t['bright'], 'tabLine': t['link'],
        'buttonHover': s['primaryHover'], 'buttonActive': '#6A4EDA', 'attention': st['warning'],
        'field': s['ink1'], 'fieldText': t['fg'], 'fieldBorder': t['link'],
        'fieldFocus': s['ink0'], 'fieldFocusBorder': t['bright'],
        'fieldHighlight': s['primary'], 'fieldHighlightText': t['bright'],
        'popup': s['ink2'], 'popupText': t['fg'], 'popupBorder': s['border'],
        'popupHighlight': s['selection'], 'popupHighlightText': t['bright'],
        'sidebar': s['ink1'], 'sidebarText': t['fg'], 'sidebarBorder': s['border'],
        'sidebarHighlight': s['primary'], 'sidebarHighlightText': t['bright'],
        'raised': s['ink3'], 'page': s['ink1'], 'pageText': t['fg'], 'pageLink': t['link'],
    }


def chrome(p):
    r = roles(p)
    c = lambda k: list(rgb(r[k]))  # noqa: E731  Chrome wants [r, g, b]
    colors = {
        'frame': c('frame'), 'frame_inactive': c('frameInactive'),
        'frame_incognito': c('frameIncognito'), 'frame_incognito_inactive': c('frameIncognito'),
        'background_tab': c('frame'), 'background_tab_inactive': c('frameInactive'),
        'background_tab_incognito': c('frameIncognito'), 'background_tab_incognito_inactive': c('frameIncognito'),
        'tab_background_text': c('backgroundTabText'), 'tab_background_text_inactive': c('backgroundTabText'),
        'tab_background_text_incognito': c('backgroundTabText'),
        'tab_background_text_incognito_inactive': c('backgroundTabText'),
        'toolbar': c('toolbar'), 'tab_text': c('tabText'), 'bookmark_text': c('toolbarText'),
        'toolbar_text': c('toolbarText'), 'toolbar_button_icon': c('toolbarText'),
        'omnibox_background': c('field'), 'omnibox_text': c('fieldText'),
        'ntp_background': c('page'), 'ntp_text': c('pageText'), 'ntp_link': c('pageLink'),
    }
    return {
        'manifest_version': 3,
        'name': 'ThatDataPurple.Chrome',
        'description': 'A purple theme for Chrome, Edge and Brave'
                       ' in the That Data Person brand colours, by That Data Person Limited.',
        'version': VERSION,
        'author': AUTHOR,
        'icons': {'128': 'images/ThatDataPurple.icon.png'},
        'theme': {'colors': colors},
    }


def _gecko_colors(r):
    return {
        'frame': r['frame'], 'frame_inactive': r['frameInactive'],
        'tab_background_text': r['backgroundTabText'], 'tab_selected': r['toolbar'], 'tab_text': r['tabText'],
        'tab_line': r['tabLine'], 'tab_loading': r['tabLine'],
        'toolbar': r['toolbar'], 'toolbar_text': r['toolbarText'], 'icons': r['toolbarText'],
        'icons_attention': r['attention'],
        'button_background_hover': r['buttonHover'], 'button_background_active': r['buttonActive'],
        'toolbar_top_separator': r['frame'], 'toolbar_bottom_separator': r['frame'],
        'toolbar_vertical_separator': r['buttonActive'],
        'toolbar_field': r['field'], 'toolbar_field_text': r['fieldText'], 'toolbar_field_border': r['fieldBorder'],
        'toolbar_field_focus': r['fieldFocus'], 'toolbar_field_text_focus': r['fieldText'],
        'toolbar_field_border_focus': r['fieldFocusBorder'],
        'toolbar_field_highlight': r['fieldHighlight'], 'toolbar_field_highlight_text': r['fieldHighlightText'],
        'popup': r['popup'], 'popup_text': r['popupText'], 'popup_border': r['popupBorder'],
        'popup_highlight': r['popupHighlight'], 'popup_highlight_text': r['popupHighlightText'],
        'sidebar': r['sidebar'], 'sidebar_text': r['sidebarText'], 'sidebar_border': r['sidebarBorder'],
        'sidebar_highlight': r['sidebarHighlight'], 'sidebar_highlight_text': r['sidebarHighlightText'],
    }


def firefox(p):
    r = roles(p)
    colors = _gecko_colors(r)
    colors.update({'ntp_background': r['page'], 'ntp_text': r['pageText']})
    return {
        'manifest_version': 2,
        'version': VERSION,
        'name': 'ThatDataPurple',
        'description': 'A purple theme for Firefox in the That Data Person brand colours, by That Data Person Limited.',
        'author': AUTHOR,
        'browser_specific_settings': {'gecko': {'id': FIREFOX_ID, 'data_collection_permissions': NO_DATA}},
        'icons': {'128': 'images/ThatDataPurple.icon.png'},
        'theme': {
            'colors': colors,
            # Menus and built-in pages follow the dark theme; websites keep following the system setting.
            'properties': {'color_scheme': 'dark', 'content_color_scheme': 'system'},
        },
    }


def thunderbird(p):
    r = roles(p)
    colors = _gecko_colors(r)
    # Thunderbird draws the message header (sender, subject, date, header buttons) in the background-tab
    # text colour on the toolbar purple, and fades some labels further, so it needs white, not muted.
    colors['tab_background_text'] = r['tabText']
    # Thunderbird-only keys, declared in theme_experiment below. Its window background reads --lwt-frame,
    # which the standard frame keys don't set (as of Thunderbird 157), and the message list reads
    # --tree-view-bg rather than the sidebar colours. The --layout-background-* greys (reading pane,
    # account pages, dialogs) move onto the ink ramp.
    s = p['surface']
    experiment = {
        'tdp_window': '--lwt-frame', 'tdp_window_inactive': '--lwt-frame-inactive',
        'tdp_message_list': '--tree-view-bg',
        'tdp_layout_0': '--layout-background-0', 'tdp_layout_1': '--layout-background-1',
        'tdp_layout_2': '--layout-background-2', 'tdp_layout_3': '--layout-background-3',
    }
    colors.update({'tdp_window': r['frame'], 'tdp_window_inactive': r['frameInactive'],
                   'tdp_message_list': r['sidebar'],
                   'tdp_layout_0': s['ink0'], 'tdp_layout_1': s['ink1'],
                   'tdp_layout_2': s['ink2'], 'tdp_layout_3': s['ink3']})
    return {
        'manifest_version': 2,
        'version': VERSION,
        'name': 'ThatDataPurple',
        'description': 'A purple theme for Thunderbird in the That Data Person brand colours, by That Data Person Limited.',
        'author': AUTHOR,
        'browser_specific_settings': {'gecko': {'id': THUNDERBIRD_ID, 'strict_min_version': '128.0', 'strict_max_version': '154.*',
                                                 'data_collection_permissions': NO_DATA}},
        'icons': {'128': 'images/ThatDataPurple.icon.png'},
        'theme_experiment': {'colors': experiment},
        'theme': {
            'colors': colors,
            'properties': {'color_scheme': 'dark', 'content_color_scheme': 'system'},
        },
    }


def checks(p):
    r = roles(p)
    text = [
        ('selected tab text', 'tabText', 'toolbar'), ('background tab text', 'backgroundTabText', 'frame'),
        ('background tab text, inactive window', 'backgroundTabText', 'frameInactive'),
        ('background tab text, private window', 'backgroundTabText', 'frameIncognito'),
        ('toolbar text', 'toolbarText', 'toolbar'), ('toolbar text on hover', 'toolbarText', 'buttonHover'),
        ('toolbar text when pressed', 'toolbarText', 'buttonActive'),
        ('address bar text', 'fieldText', 'field'), ('address bar text, focused', 'fieldText', 'fieldFocus'),
        ('address bar selected text', 'fieldHighlightText', 'fieldHighlight'),
        ('menu text', 'popupText', 'popup'), ('menu highlighted text', 'popupHighlightText', 'popupHighlight'),
        ('sidebar text', 'sidebarText', 'sidebar'), ('sidebar selected text', 'sidebarHighlightText', 'sidebarHighlight'),
        ('Thunderbird text on raised panels', 'popupText', 'raised'),
        ('new tab page text', 'pageText', 'page'), ('new tab page links', 'pageLink', 'page'),
    ]
    ui = [
        ('selected tab line', 'tabLine', 'toolbar'), ('selected tab line against frame', 'tabLine', 'frame'),
        ('address bar outline', 'fieldBorder', 'toolbar'), ('address bar focus outline', 'fieldFocusBorder', 'toolbar'),
        ('attention icon', 'attention', 'toolbar'),
    ]
    # Thunderbird's message header: background-tab text on the toolbar, with some labels at reduced opacity.
    header = [('Thunderbird message header text', 1.0), ('Thunderbird message header address (90%)', 0.9),
              ('Thunderbird message header labels (70%)', 0.7)]
    return ([(f'Browsers {n}', r[f], r[b], 4.5) for n, f, b in text]
            + [(n, blend(r['tabText'], r['toolbar'], a), r['toolbar'], 4.5) for n, a in header]
            + [(f'Browsers {n}', r[f], r[b], 3.0) for n, f, b in ui])


def write(manifest, path, tabs=False):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, indent='\t' if tabs else 2)
        f.write('\n')
