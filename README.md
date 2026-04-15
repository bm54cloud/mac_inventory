# mac-inventory
A Python script for auditing your Mac's installed tools and applications and writing them to a .txt file. Reference the file when migrating to a new machine so you can remember what you previously had configured.

# What it inventories:

- 120+ CLI tools and runtimes (with versions)
- Homebrew formulae, casks, and taps
- Installed applications in /Applications
- Shell config files (.zshrc, .gitconfig, .ssh/config, etc.)
- npm global packages
- VS Code/Cursor extensions

# Usage:
`python3 mac_inventory.py | tee mac_inventory_report.txt`

Requires Python 3 and macOS. No external dependencies.
