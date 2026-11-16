# Publishing to GitHub Pages

`scripts/publish.py` does everything below in one command. This file is
for the cases where it does not.

## Two kinds of repository

| Repo name | URL | Notes |
| --- | --- | --- |
| `<user>.github.io` | `https://<user>.github.io/` | One per account. The root domain |
| anything else | `https://<user>.github.io/<repo>/` | Project page. The generated site uses relative paths, so it works unchanged |

Both are public by default. Pages on a **private** repository needs a paid
plan; for a CV site, public is the point.

## What the script runs

```sh
git init -b main
git add -A
git commit -m "site: first publish"
gh repo create <repo> --public --source=. --remote=origin --push
gh api -X POST repos/<owner>/<repo>/pages \
  -f source[branch]=main -f source[path]=/
```

Then it polls `repos/<owner>/<repo>/pages` until the status is `built`
(usually 30–90 seconds) and prints the URL.

`--dry-run` prints those commands without running them. That is also the
right thing to show a user who wants to understand before agreeing.

## Prerequisites

- `git` on PATH.
- GitHub CLI installed and authenticated:
  - Windows: `winget install GitHub.cli`
  - macOS: `brew install gh`
  - Debian/Ubuntu: `sudo apt install gh`
  - then `gh auth login` (choose HTTPS, log in through the browser).
- Permission to create repositories in the target account or org.

If `gh` is missing, the script prints the manual path and exits 2. Do not
install software on someone's machine without asking.

## Manual path (no `gh`)

1. Create an empty **public** repo on github.com, no README, no licence.
2. In the site folder:
   ```sh
   git init -b main
   git add -A
   git commit -m "site: first publish"
   git remote add origin https://github.com/<owner>/<repo>.git
   git push -u origin main
   ```
3. Repo → Settings → Pages → Source: *Deploy from a branch* → `main` / `/`.
4. Wait a minute, reload the Pages settings screen; the URL appears there.

## Custom domain

1. Add a file named `CNAME` at the root of the repo containing only the
   domain, e.g. `ada.example.com`.
2. In the DNS provider:
   - apex domain (`example.com`) → four `A` records to
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
     `185.199.111.153`;
   - `www` or a subdomain → `CNAME` to `<user>.github.io`.
3. In Settings → Pages, set the custom domain and enable *Enforce HTTPS*
   once the certificate is issued (can take up to a day).

Do not put a `CNAME` file in a project page unless you really own the
domain; it will hijack the URL.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| 404 right after publishing | Build still running. Check Settings → Pages, wait 2 minutes, hard refresh |
| 404 for CSS and images | The site was built with paths that assume the root. Rebuild — `build.py` emits relative paths |
| Page shows the README instead of the site | No `index.html` at the repo root, or Pages is pointed at `/docs`. Republish from the site folder |
| "Repository not found" from git | Wrong remote, or not authenticated. `gh auth status`, then `git remote -v` |
| Pages refuses a private repo | Plan limitation. Make the repo public or upgrade |
| Changes don't appear | Publish did not commit. `git status` in the site folder, then `git add -A && git commit && git push` |
| Custom domain loops or 404s | Missing DNS record, or `CNAME` file missing at the repo root |
| Build fails with Jekyll errors | `.nojekyll` is missing. `build.py` writes it; if publishing by hand, `touch .nojekyll` |

## Updating the site later

The folder is a normal git repository after the first publish:

```sh
# edit site.json, then
python3 scripts/build.py --out .
git add -A && git commit -m "content: new project"
git push
```

Pages rebuilds on every push to `main`. Keep `site.json` and the PDF in
the repo — they are the source, the HTML is the output. If you rebuild
from a different machine, that is all you need to clone.

## What not to do

- Don't edit `index.html` by hand and then rebuild; it gets overwritten.
- Don't force-push to a repository you did not create.
- Don't publish a phone number, a home address, or a client name under
  NDA just because it is in the CV.
- Don't add analytics, trackers or third-party scripts to a page that only
  needs to show text.
