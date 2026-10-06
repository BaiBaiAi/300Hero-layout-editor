$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

python -m PyInstaller --noconfirm --clean --onefile `
    --name 300Hero-Layout-Editor `
    --add-data 'web;web' `
    --add-data 'option_templates;option_templates' `
    app.py

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$hash = Get-FileHash 'dist/300Hero-Layout-Editor.exe' -Algorithm SHA256
('{0}  {1}' -f $hash.Hash.ToLowerInvariant(), '300Hero-Layout-Editor.exe') |
    Set-Content 'dist/SHA256SUMS.txt' -Encoding ascii
Get-Content 'dist/SHA256SUMS.txt'
