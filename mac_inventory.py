#!/usr/bin/env python3
"""
Mac Tool & Application Inventory Script
Outputs a readable report of installed CLI tools and applications.
"""

import subprocess
import shutil
import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text) if text else text

def run(cmd, shell=False):
    try:
        env = os.environ.copy()
        env['NO_COLOR'] = '1'
        env['TERM'] = 'dumb'
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=shell, timeout=15, env=env
        )
        output = result.stdout.strip() or result.stderr.strip()
        return strip_ansi(output)
    except Exception:
        return None


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_tool(name, version_cmd=None):
    """Returns (found, version) for a CLI tool."""
    path = shutil.which(name)
    if not path:
        return False, None
    version = None
    if version_cmd:
        version = run(version_cmd, shell=True)
        if version:
            # Just grab first line to keep it clean
            version = version.splitlines()[0]
    return True, version


# ── CLI Tools to check ────────────────────────────────────────────────────────
CLI_TOOLS = [
    # Shells
    ("bash",        "bash --version | head -1"),
    ("zsh",         "zsh --version"),
    ("fish",        "fish --version"),

    # Package managers
    ("brew",        "brew --version | head -1"),
    ("nix",         "nix --version"),
    ("macports",    "port version"),

    # Version managers
    ("nvm",         None),  # nvm is a shell function, just check the dir
    ("pyenv",       "pyenv --version"),
    ("rbenv",       "rbenv --version"),
    ("nodenv",      "nodenv --version"),
    ("asdf",        "asdf --version"),
    ("mise",        "mise --version"),
    ("tfenv",       "tfenv --version"),

    # Runtimes
    ("node",        "node --version"),
    ("python3",     "python3 --version"),
    ("python",      "python --version"),
    ("ruby",        "ruby --version"),
    ("go",          "go version"),
    ("java",        "java -version 2>&1 | head -1"),
    ("rustc",       "rustc --version"),
    ("cargo",       "cargo --version"),
    ("deno",        "deno --version | head -1"),
    ("bun",         "bun --version"),
    ("elixir",      "elixir --version | tail -1"),
    ("erlang",      "erl -eval 'erlang:display(erlang:system_info(version)), halt()' -noshell 2>/dev/null"),
    ("julia",       "julia --version"),
    ("R",           "R --version | head -1"),
    ("perl",        "perl --version | head -2 | tail -1"),
    ("php",         "php --version | head -1"),
    ("scala",       "scala --version"),
    ("kotlin",      "kotlinc -version 2>&1"),
    ("swift",       "swift --version 2>&1 | head -1"),

    # Package managers / build tools
    ("npm",         "npm --version"),
    ("yarn",        "yarn --version"),
    ("pnpm",        "pnpm --version"),
    ("pip3",        "pip3 --version"),
    ("pipx",        "pipx --version"),
    ("poetry",      "poetry --version"),
    ("uv",          "uv --version"),
    ("gem",         "gem --version"),
    ("bundler",     "bundle --version"),
    ("gradle",      "gradle --version | grep Gradle"),
    ("maven",       "mvn --version | head -1"),

    # Version control
    ("git",         "git --version"),
    ("gh",          "gh --version | head -1"),
    ("git-lfs",     "git-lfs --version"),
    ("svn",         "svn --version | head -1"),
    ("hg",          "hg --version | head -1"),

    # Cloud / infra
    ("aws",         "aws --version"),
    ("az",          "az --version | head -1"),
    ("gcloud",      "gcloud --version | head -1"),
    ("terraform",   "terraform --version | head -1"),
    ("tofu",        "tofu --version | head -1"),
    ("pulumi",      "pulumi version"),
    ("ansible",     "ansible --version | head -1"),
    ("kubectl",     "kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null | head -1"),
    ("helm",        "helm version --short"),
    ("minikube",    "minikube version | head -1"),
    ("kind",        "kind --version"),
    ("k9s",         "k9s version 2>/dev/null | grep -i 'version' | head -1"),
    ("flux",        "flux --version"),
    ("argocd",      "argocd version --client | head -1"),
    ("eksctl",      "eksctl version"),
    ("skaffold",    "skaffold version"),
    ("zarf",        "zarf version"),
    ("uds",         "uds version"),

    # Containers
    ("docker",      "docker --version"),
    ("docker-compose", "docker-compose --version"),
    ("podman",      "podman --version"),
    ("colima",      "colima version"),
    ("lima",        "limactl --version"),

    # Editors / IDEs (CLI)
    ("vim",         "vim --version | head -1"),
    ("nvim",        "nvim --version | head -1"),
    ("emacs",       "emacs --version | head -1"),
    ("nano",        "nano --version | head -1"),
    ("code",        "code --version | head -1"),
    ("cursor",      "cursor --version 2>/dev/null | head -1"),
    ("subl",        "subl --version"),

    # Shell tools / utilities
    ("tmux",        "tmux -V"),
    ("zellij",      "zellij --version"),
    ("screen",      "screen --version"),
    ("fzf",         "fzf --version"),
    ("ripgrep",     "rg --version | head -1"),
    ("fd",          "fd --version"),
    ("bat",         "bat --version"),
    ("exa",         "exa --version"),
    ("eza",         "eza --version | head -1"),
    ("lsd",         "lsd --version"),
    ("delta",       "delta --version"),
    ("jq",          "jq --version"),
    ("yq",          "yq --version"),
    ("htop",        "htop --version | head -1"),
    ("btop",        "btop --version | head -1"),
    ("dust",        "dust --version"),
    ("duf",         "duf --version"),
    ("procs",       "procs --version"),
    ("zoxide",      "zoxide --version"),
    ("starship",    "starship --version"),
    ("thefuck",     "thefuck --version"),
    ("tldr",        "tldr --version"),
    ("atuin",       "atuin --version"),
    ("mcfly",       "mcfly --version"),
    ("direnv",      "direnv --version"),
    ("stow",        "stow --version | head -1"),
    ("chezmoi",     "chezmoi --version | head -1"),

    # Networking
    ("curl",        "curl --version | head -1"),
    ("wget",        "wget --version | head -1"),
    ("httpie",      "http --version"),
    ("xh",          "xh --version"),
    ("nmap",        "nmap --version | head -1"),
    ("netcat",      "nc -h 2>&1 | head -1"),
    ("mtr",         "mtr --version"),
    ("wrk",         "wrk --version 2>&1 | head -1"),
    ("hey",         "hey 2>&1 | head -1"),
    ("k6",          "k6 version"),
    ("ngrok",       "ngrok --version"),

    # Databases
    ("psql",        "psql --version"),
    ("mysql",       "mysql --version"),
    ("sqlite3",     "sqlite3 --version"),
    ("mongosh",     "mongosh --version"),
    ("redis-cli",   "redis-cli --version"),

    # Security / smart card (relevant for you!)
    ("gpg",         "gpg --version | head -1"),
    ("openssh",     "ssh -V 2>&1"),
    ("openssl",     "openssl version"),
    ("sc_auth",     "sc_auth version 2>/dev/null || echo 'present (no --version flag)'"),
    ("yubikey-manager", "ykman --version"),
    ("step",        "step --version 2>&1 | head -1"),

    # Misc dev tools
    ("make",        "make --version | head -1"),
    ("cmake",       "cmake --version | head -1"),
    ("gcc",         "gcc --version | head -1"),
    ("clang",       "clang --version | head -1"),
    ("llvm",        "llvm-config --version"),
    ("protoc",      "protoc --version"),
    ("grpcurl",     "grpcurl --version 2>&1"),
    ("buf",         "buf --version"),
    ("air",         "air -v 2>&1 | head -1"),
    ("golangci-lint", "golangci-lint --version | head -1"),
    ("staticcheck", "staticcheck --version"),
    ("black",       "black --version"),
    ("ruff",        "ruff --version"),
    ("mypy",        "mypy --version"),
    ("eslint",      "eslint --version"),
    ("prettier",    "prettier --version"),
    ("pre-commit",  "pre-commit --version"),
    ("act",         "act --version"),
    ("tflint",      "tflint --version"),
    ("hadolint",    "hadolint --version"),

    # Data / ML
    ("conda",       "conda --version"),
    ("mamba",       "mamba --version | head -1"),

    # Media
    ("ffmpeg",      "ffmpeg -version | head -1"),
    ("imagemagick", "convert --version | head -1"),
    ("exiftool",    "exiftool -ver"),
]


def main():
    print(f"Mac Inventory Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Hostname:  {run('hostname')}")
    print(f"macOS:     {run('sw_vers -productVersion')} ({run('sw_vers -buildVersion')})")
    print(f"Arch:      {run('uname -m')}")

    # ── CLI Tools ──────────────────────────────────────────────────────────────
    section("CLI TOOLS & RUNTIMES")
    found_tools = []

    for name, vcmd in CLI_TOOLS:
        found, version = check_tool(name, vcmd)
        if found:
            found_tools.append((name, version or "found (no version)"))
        else:
            # Special case: nvm lives in ~/.nvm, not on PATH
            if name == "nvm" and Path.home().joinpath(".nvm").exists():
                found_tools.append(("nvm", "found (~/.nvm exists)"))

    print(f"\n✅ Installed ({len(found_tools)}):\n")
    for name, version in sorted(found_tools):
        print(f"  {name:<25} {version}")

    # ── Homebrew details ───────────────────────────────────────────────────────
    if shutil.which("brew"):
        section("HOMEBREW PACKAGES")

        print("\n--- Formulae (brew list --formula) ---\n")
        formulae = run("brew list --formula", shell=True)
        if formulae:
            items = formulae.splitlines()
            print(f"  ({len(items)} installed)\n")
            for item in items:
                print(f"  {item}")
        else:
            print("  (none found)")

        print("\n--- Casks (brew list --cask) ---\n")
        casks = run("brew list --cask", shell=True)
        if casks:
            items = casks.splitlines()
            print(f"  ({len(items)} installed)\n")
            for item in items:
                print(f"  {item}")
        else:
            print("  (none found)")

        print("\n--- Taps (brew tap) ---\n")
        taps = run("brew tap", shell=True)
        if taps:
            for tap in taps.splitlines():
                print(f"  {tap}")
        else:
            print("  (none found)")

    # ── Mac Applications ───────────────────────────────────────────────────────
    section("INSTALLED APPLICATIONS (/Applications)")
    apps = run("ls /Applications", shell=True)
    if apps:
        app_list = [a for a in apps.splitlines() if a.endswith(".app")]
        print(f"\n  ({len(app_list)} apps)\n")
        for app in sorted(app_list):
            print(f"  {app}")

    user_apps = run(f"ls ~/Applications 2>/dev/null", shell=True)
    if user_apps:
        user_app_list = [a for a in user_apps.splitlines() if a.endswith(".app")]
        if user_app_list:
            print(f"\n--- ~/Applications ({len(user_app_list)}) ---\n")
            for app in sorted(user_app_list):
                print(f"  {app}")

    # ── Shell config files ─────────────────────────────────────────────────────
    section("SHELL CONFIG FILES (existence check)")
    config_files = [
        "~/.zshrc", "~/.zprofile", "~/.zshenv",
        "~/.bashrc", "~/.bash_profile", "~/.bash_aliases",
        "~/.profile",
        "~/.config/fish/config.fish",
        "~/.tmux.conf", "~/.config/tmux/tmux.conf",
        "~/.vimrc", "~/.config/nvim/init.vim", "~/.config/nvim/init.lua",
        "~/.gitconfig", "~/.gitignore_global",
        "~/.ssh/config",
        "~/.gnupg/gpg.conf",
        "~/.config/starship.toml",
        "~/.tool-versions",
        "~/.mise.toml",
        "~/.Brewfile",
    ]
    print()
    for f in config_files:
        p = Path(f).expanduser()
        exists = "✅" if p.exists() else "  "
        size = f"  ({p.stat().st_size} bytes)" if p.exists() else ""
        print(f"  {exists}  {f}{size}")

    # ── Python pip packages ────────────────────────────────────────────────────
    if shutil.which("pip3"):
        section("PYTHON GLOBAL PACKAGES (pip3 list)")
        packages = run("pip3 list --format=columns", shell=True)
        if packages:
            lines = packages.splitlines()
            print(f"\n  ({max(0, len(lines)-2)} packages)\n")
            print(packages)

    # ── npm global packages ────────────────────────────────────────────────────
    if shutil.which("npm"):
        section("NPM GLOBAL PACKAGES")
        pkgs = run("npm list -g --depth=0", shell=True)
        if pkgs:
            print(f"\n{pkgs}")

    # ── VS Code extensions ─────────────────────────────────────────────────────
    if shutil.which("code"):
        section("VS CODE EXTENSIONS")
        exts = run("code --list-extensions", shell=True)
        if exts:
            ext_list = exts.splitlines()
            print(f"\n  ({len(ext_list)} extensions)\n")
            for e in ext_list:
                print(f"  {e}")

    if shutil.which("cursor"):
        section("CURSOR EXTENSIONS")
        exts = run("cursor --list-extensions", shell=True)
        if exts:
            ext_list = exts.splitlines()
            print(f"\n  ({len(ext_list)} extensions)\n")
            for e in ext_list:
                print(f"  {e}")

    print(f"\n{'='*60}")
    print("  END OF REPORT")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

