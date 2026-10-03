# Installs the ThatDataPurple colour scheme for Windows Terminal as a settings fragment.
# Terminal picks it up on its next start; your settings.json is not changed.
# To remove it, delete the folder this script prints.
$dest = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows Terminal\Fragments\ThatDataPurple'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item (Join-Path $PSScriptRoot 'ThatDataPurple.json') $dest -Force
"Installed to $dest"
"Restart Windows Terminal, then choose ThatDataPurple under Settings > Profiles > Defaults > Appearance > Color scheme."
