#!/usr/bin/env python3
"""Create a GitHub repository and publish a generated site with Pages.

Usage:
    python publish.py --dir <site-dir> --repo my-site [--dry-run]

Behaviour:
  * never pushes into a repository that already exists (use --force to
    publish into a repo you own and really want to overwrite);
  * refuses to run if index.html is missing;
  * uses the `gh` CLI when available, otherwise prints the exact manual
    steps and exits with code 2.

Requires: git and (for automation) GitHub CLI, authenticated once with
`gh auth login`.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

# Windows consoles default to a legacy code page; keep accented paths printable.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import time

GIT_FALLBACKS = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    "/usr/bin/git",
    "/usr/local/bin/git",
    "/opt/homebrew/bin/git",
]


def find(name, fallbacks=()):
    path = shutil.which(name)
    if path:
        return path
    for candidate in fallbacks:
        if os.path.isfile(candidate):
            return candidate
    return None


def run(cmd, cwd=None, dry=False, check=True):
    printable = " ".join(cmd)
    if dry:
        print("  $ " + printable)
        return ""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except FileNotFoundError:
        sys.exit("command not found: " + cmd[0])
    if check and proc.returncode != 0:
        print(proc.stdout.strip())
        print(proc.stderr.strip(), file=sys.stderr)
        sys.exit("failed: " + printable)
    return (proc.stdout or "") + (proc.stderr or "")


def manual_steps(site_dir, repo, owner, branch):
    print()
    print("gh (GitHub CLI) is not installed, so nothing was published.")
    print()
    print("Option A — install gh and rerun this script:")
    print("  Windows        winget install GitHub.cli")
    print("  macOS          brew install gh")
    print("  Debian/Ubuntu  sudo apt install gh")
    print("  then           gh auth login")
    print()
    print("Option B — do it by hand:")
    print("  1. Create an empty public repository named " + repo + " on github.com")
    print("  2. In " + site_dir + ":")
    print("       git init -b " + branch)
    print("       git add -A")
    print('       git commit -m "site: first publish"')
    print("       git remote add origin https://github.com/" + owner + "/" + repo + ".git")
    print("       git push -u origin " + branch)
    print("  3. Repository → Settings → Pages → Source: Deploy from a branch")
    print("     Branch: " + branch + " / root")
    print("  4. Your site appears at " + site_url(owner, repo))


def site_url(owner, repo):
    if repo.lower() == (owner + ".github.io").lower():
        return "https://" + owner.lower() + ".github.io/"
    return "https://" + owner.lower() + ".github.io/" + repo + "/"


def pages_request(gh, owner, repo, branch, dry):
    endpoint = "repos/" + owner + "/" + repo + "/pages"
    body = ["-f", "source[branch]=" + branch, "-f", "source[path]=/"]
    out = run([gh, "api", "-X", "POST", endpoint] + body, dry=dry, check=False)
    low = out.lower()
    if not dry and ("already" in low or "409" in low or "conflict" in low):
        run([gh, "api", "-X", "PUT", endpoint] + body, dry=dry, check=False)


def wait_for_pages(gh, owner, repo, dry, seconds=120):
    if dry:
        return "unknown"
    endpoint = "repos/" + owner + "/" + repo + "/pages"
    deadline = time.time() + seconds
    status = ""
    while time.time() < deadline:
        out = run([gh, "api", endpoint], check=False)
        try:
            status = json.loads(out).get("status", "")
        except Exception:  # noqa: BLE001 - gh may print a message instead of JSON
            status = ""
        if status == "built":
            return status
        if status == "errored":
            return status
        time.sleep(5)
    return status or "unknown"


def main():
    ap = argparse.ArgumentParser(description="Publish a site to GitHub Pages")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--repo", required=True, help="repository name, e.g. my-site or <user>.github.io")
    ap.add_argument("--owner", help="GitHub user or org (default: the authenticated user)")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--force", action="store_true", help="push into an existing repository")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    site_dir = os.path.abspath(args.dir)
    if not os.path.isfile(os.path.join(site_dir, "index.html")):
        sys.exit("index.html not found in " + site_dir + " — run build.py first")

    git = find("git", GIT_FALLBACKS)
    if not git:
        sys.exit("git is not installed or not on PATH")

    gh = find("gh")
    if not gh:
        owner = args.owner or "<your-github-user>"
        manual_steps(site_dir, args.repo, owner, args.branch)
        sys.exit(2)

    owner = args.owner
    if not owner:
        owner = run([gh, "api", "user", "--jq", ".login"], dry=args.dry_run).strip()
    if not owner:
        sys.exit("could not read the GitHub user; pass --owner")

    full = owner + "/" + args.repo
    print("publishing " + site_dir)
    print("repository " + full)

    exists = run([gh, "repo", "view", full], dry=False, check=False)
    if not args.dry_run and "not found" not in exists.lower() and exists.strip():
        if not args.force:
            sys.exit(
                "repository " + full + " already exists.\n"
                "Refusing to overwrite it. Pass --force only if it is yours and you want to replace it."
            )
        print("warning: repository exists and --force was given; pushing anyway")

    if not os.path.isdir(os.path.join(site_dir, ".git")):
        run([git, "init", "-b", args.branch], cwd=site_dir, dry=args.dry_run)
    run([git, "add", "-A"], cwd=site_dir, dry=args.dry_run)
    run([git, "commit", "-m", "site: first publish"], cwd=site_dir, dry=args.dry_run, check=False)
    run([git, "branch", "-M", args.branch], cwd=site_dir, dry=args.dry_run, check=False)

    if args.dry_run:
        print("  $ gh repo create " + args.repo + " --public --source=. --remote=origin --push")
        pages_request(gh, owner, args.repo, args.branch, dry=True)
        print()
        print("dry run: nothing was created. Site would be at " + site_url(owner, args.repo))
        return

    if "not found" in exists.lower() or not exists.strip():
        run(
            [gh, "repo", "create", args.repo, "--public", "--source=.", "--remote=origin", "--push"],
            cwd=site_dir,
        )
    else:
        has_remote = run([git, "remote"], cwd=site_dir).split()
        if "origin" not in has_remote:
            run([git, "remote", "add", "origin", "https://github.com/" + full + ".git"], cwd=site_dir)
        run([git, "push", "-u", "origin", args.branch], cwd=site_dir)

    pages_request(gh, owner, args.repo, args.branch, dry=False)
    print("waiting for GitHub Pages...")
    status = wait_for_pages(gh, owner, args.repo, dry=False)
    print("pages status: " + status)
    print()
    print("site: " + site_url(owner, args.repo))
    print("repo: https://github.com/" + full)
    if status not in ("built",):
        print("Pages is still building; it usually takes 1–2 minutes.")


if __name__ == "__main__":
    main()
