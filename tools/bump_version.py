import re
import sys
import subprocess

VERSION_FILE = "config.py"
INSTALLER_FILE = "WarInstaller.iss"

def set_version_in_config(new_version):
    with open(VERSION_FILE, "r") as f:
        content = f.read()

    updated = re.sub(
        r'APP_VERSION\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"',
        f'APP_VERSION = "{new_version}"',
        content
    )

    with open(VERSION_FILE, "w") as f:
        f.write(updated)

def set_version_in_installer(new_version):
    with open(INSTALLER_FILE, "r") as f:
        content = f.read()

    updated = re.sub(
        r'#define MyAppVersion\s*"[^"]+"',
        f'#define MyAppVersion "{new_version}"',
        content
    )

    with open(INSTALLER_FILE, "w") as f:
        f.write(updated)

def git(*args):
    subprocess.check_call(["git"] + list(args))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: bump_version.py 1.0.1")
        sys.exit(1)

    version = sys.argv[1]

    print(f"Bumping version to {version}...")

    set_version_in_config(version)
    set_version_in_installer(version)

    git("add", VERSION_FILE)
    git("add", INSTALLER_FILE)
    git("commit", "-m", f"Bump version to {version}")
    git("tag", f"v{version}")
    git("push")
    git("push", "--tags")

    print("Done.")