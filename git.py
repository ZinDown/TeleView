import os
import sys
import subprocess
import re

# ---------- AUTO INSTALL ----------
def ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            stdout=subprocess.DEVNULL
        )

ensure("colorama")
ensure("pyfiglet")

from colorama import Fore, Style, init
import pyfiglet

init(autoreset=True)
BR = Style.BRIGHT

# ---------- UI ----------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print(Fore.CYAN + BR + pyfiglet.figlet_format("GitHub Tool"))
    print(Fore.YELLOW + BR + "Script By Lynn Xu • Git Repo Update • Download\n")

def ok(msg):   print(Fore.GREEN + BR + "✔ " + msg)
def err(msg):  print(Fore.RED   + BR + "✖ " + msg)
def info(msg): print(Fore.CYAN  + BR + "➜ " + msg)

def run(cmd, cwd=None):
    return subprocess.run(cmd, shell=True, cwd=cwd)

def pause():
    input(Fore.MAGENTA + BR + "\nPress Enter to continue...")

# ---------- INPUT BLOCK ----------
def input_block(title, example, label):
    print(Fore.MAGENTA + BR + f"\n{title}")
    print(Fore.WHITE + BR + "Example: " + Fore.GREEN + BR + example + "\n")
    while True:
        val = input(Fore.YELLOW + BR + f"{label}: ").strip()
        if val:
            return val
        err("This field is required!")

# ---------- REPO URL ----------
def input_repo_url():
    while True:
        repo = input_block(
            "🔗 GitHub Repository URL",
            "https://github.com/user/repo.git",
            "GitHub Repo URL"
        )

        if not repo.startswith("https://"):
            err("URL must start with https://")
            continue

        m = re.match(r"https://github\.com/([^/]+)/([^/]+)(\.git)?$", repo)
        if not m:
            err("Invalid GitHub repository link!")
            continue

        username = m.group(1)
        repo_name = m.group(2).replace(".git", "")
        clean_repo = f"https://github.com/{username}/{repo_name}.git"

        return clean_repo, username, repo_name

# ---------- DOWNLOAD ----------
def download_repo():
    banner()
    print(Fore.BLUE + BR + "📥 DOWNLOAD FROM GITHUB")

    repo, _, repo_name = input_repo_url()

    parent = input_block(
        "📁 Download Folder Path",
        "/storage/emulated/0/Download",
        "Download parent folder"
    )

    parent = os.path.abspath(parent)
    if not os.path.isdir(parent):
        err("Folder not found!")
        pause()
        return

    final_path = os.path.join(parent, repo_name)

    if not os.path.exists(final_path):
        info("Repo not found → Cloning...")
        if run(f'git clone "{repo}" "{final_path}"').returncode == 0:
            ok(f"Downloaded → {final_path}")
        else:
            err("Clone failed ❌")
    else:
        git_dir = os.path.join(final_path, ".git")
        if not os.path.isdir(git_dir):
            err("Folder exists but is NOT a git repository!")
            pause()
            return

        info("Repo exists → Updating (git pull)...")
        if run("git pull", cwd=final_path).returncode == 0:
            ok(f"Updated → {final_path}")
        else:
            err("Pull failed ❌")

    pause()

# ---------- UPLOAD ----------
def upload_repo():
    banner()
    print(Fore.BLUE + BR + "📤 UPLOAD TO GITHUB")

    folder = input_block(
        "📁 Project Folder Path",
        "/storage/emulated/0/Download/myrepo",
        "Project folder path"
    )

    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        err("Folder not found!")
        pause()
        return

    repo, username, _ = input_repo_url()

    print(Fore.MAGENTA + BR + "\n📝 Commit Message")
    msg = input(Fore.YELLOW + BR + "Enter message (Enter = auto): ").strip()
    if not msg:
        msg = "update from github tool"

    token = input_block(
        "🔐 GitHub Token",
        "ghp_xxxxxxxxxxxxxxxxxxxx",
        "GitHub Token"
    )

    secure_repo = repo.replace(
        "https://",
        f"https://{username}:{token}@"
    )

    if not os.path.isdir(os.path.join(folder, ".git")):
        run("git init", cwd=folder)

    # 🔥 FIX: Termux / Android storage safe directory
    run(f'git config --global --add safe.directory "{folder}"')

    # local identity (github email not required)
    run(f'git config user.name "{username}"', cwd=folder)
    run(f'git config user.email "{username}@users.noreply.github.com"', cwd=folder)

    run("git add .", cwd=folder)
    if run(f'git commit -m "{msg}"', cwd=folder).returncode != 0:
        err("Nothing to commit!")
        pause()
        return

    run("git branch -M main", cwd=folder)
    run("git remote remove origin", cwd=folder)
    run(f'git remote add origin "{secure_repo}"', cwd=folder)

    info("Uploading to GitHub...")
    if run("git push -u origin main", cwd=folder).returncode == 0:
        ok("Upload successful 🎉")
    else:
        err("Upload failed ❌")

    pause()

# ---------- MENU ----------
def menu():
    while True:
        banner()
        print(Fore.GREEN + BR + "[1] Download (clone / pull)")
        print(Fore.GREEN + BR + "[2] Upload (local folder → repo)")
        print(Fore.RED   + BR + "[0] Exit\n")

        choice = input(Fore.YELLOW + BR + "Choose option: ").strip()

        if choice == "1":
            download_repo()
        elif choice == "2":
            upload_repo()
        elif choice == "0":
            ok("Bye Bye 👋")
            sys.exit()
        else:
            err("Invalid choice!")
            pause()

# ---------- START ----------
if __name__ == "__main__":
    menu()
