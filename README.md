# ThatDataPurple
A purple theme for lots of different apps in the That Data Person brand colours, by That Data Person Limited.

![ThatDataPurple](https://github.com/thatdataperson/ThatDataPurple/blob/main/images/ThatDataPurple.preview.png?raw=true)

---

### Available on:
- Chrome, Edge and Brave
  - [GitHub repo](https://github.com/thatdataperson/ThatDataPurple.Chrome)
  - [chrome web store](https://chrome.google.com/webstore/detail/thatdatapurplechrome/eikanpoghdlfifddajgjlfahfoodipjo)
- Firefox
  - [GitHub repo](https://github.com/thatdataperson/ThatDataPurple.Firefox)
  - [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/thatdatapurple/)
- Thunderbird
  - [GitHub repo](https://github.com/thatdataperson/ThatDataPurple.Firefox) (in the `thunderbird` folder)
- Visual Studio 2019
  - [GitHub repo](https://github.com/thatdataperson/ThatDataPurple.VS2019)
  - [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ThatDataPerson.themeThatDataPurpleVS2019)
- Visual Studio 2022 and 2026
  - [GitHub repo](https://github.com/thatdataperson/ThatDataPurple.VS2022)
  - [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ThatDataPerson.themeThatDataPurpleVS2022)
- Visual Studio Code 
  -  [Github repo](https://github.com/thatdataperson/ThatDataPurple.VSCode)
  -  [Visual Studio Code Marketplace](https://marketplace.visualstudio.com/items?itemName=ThatDataPerson.thatdatapurple)
- Windows 11 (wallpaper, accent colour and Dark mode) and Windows Terminal
  - [In this repo](windows/) (in the `windows` folder)
- Ubuntu (GNOME apps, wallpaper, and the Ptyxis and GNOME Terminal terminals)
  - [In this repo](ubuntu/) (in the `ubuntu` folder)
- Samsung Galaxy phones (wallpaper sized for the S24 Ultra, plus Theme Park colours)
  - [In this repo](samsung/) (in the `samsung` folder)
---

### You can also make your own theme for:
- [Slack](https://slack.com/)
  - In Slack, open *Preferences > Appearance*, select *Custom theme*, then *Import theme* next to *Theme colours*
  - Paste the following and select *Apply*: `#0D0629,#1B1048,#4320CC,#9580E6`
  - To share it, select *Share* next to *Theme colours* and paste it into a message ([Slack's instructions](https://slack.com/intl/en-gb/help/articles/205166337-Change-your-Slack-theme))

---

### Palette and build

The 2026 colours follow the That Data Person branding (brand purple `#4320CC`, light purple `#9580E6`, dark `#0D0629`).
[`palette/palette.json`](palette/palette.json) is the single source for every theme, and
[`palette/CONTRAST.md`](palette/CONTRAST.md) lists the WCAG contrast ratios. All text meets AA (4.5:1) against the
editor background, current line and selection, and the browser themes meet it for tab, toolbar,
address bar and menu text.

To rebuild the themes, clone the theme repos next to this one and run:

```
python build/build.py
```

It writes the VS Code theme JSON, both `.vstheme` files and the Chrome, Firefox and Thunderbird manifests
(with their store packages in each repo's `bin/Release`), plus the Windows Terminal scheme and Windows 11
theme pack in `windows/`, the Ubuntu theme in `ubuntu/`, and the Samsung wallpaper in `samsung/` (the wallpaper needs Pillow and numpy, and the pack needs `makecab`, so Windows only).
It then checks contrast, and exits non-zero if any pair falls below its target. The Visual Studio themes are re-coloured from the original exports kept in
`build/templates/`, so rebuilding always gives the same result.
