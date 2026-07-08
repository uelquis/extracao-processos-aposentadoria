# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

run:
    uv run ./src/main.py aposentadorias .

profile:
    uv run scalene run --profile-all src/main.py aposentadorias .

view:
    uv run scalene view