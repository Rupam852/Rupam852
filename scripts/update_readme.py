#!/usr/bin/env python3
"""
Auto-update README.md with latest GitHub data:
  1. Achievements stats (stars, repo count)
  2. New repos not yet listed in Featured Projects
"""

import os
import re
import requests

USERNAME = "Rupam852"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

HEADERS = {}
token = os.environ.get("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = f"token {token}"

# ── Repos already documented manually in Featured Projects ──────────────────
MANUALLY_LISTED = {
    "OmniPDF", "G-Drive-Vault", "GmailMNT", "CloudStream-TV",
    "MYPortfolio", "Link-Flow", "Expense-App", "Calculator",
    "Tic-Tac-Toe-Game", "Drive_Flow", "TRAFFICFLOW-AI",
    "Neo-Files-Transfer", "Payment_Page", "Login_page_Glass_Effect",
    "Rupam852",  # profile repo itself
}

# ── Fetch all public repos ───────────────────────────────────────────────────
def fetch_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=public"
        resp = requests.get(url, headers=HEADERS)
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

# ── Fetch user profile (stars, followers, etc.) ─────────────────────────────
def fetch_user():
    url = f"https://api.github.com/users/{USERNAME}"
    return requests.get(url, headers=HEADERS).json()

# ── Build markdown card for a new repo ──────────────────────────────────────
def build_project_card(repo):
    name        = repo.get("name", "")
    description = repo.get("description") or "No description provided."
    language    = repo.get("language") or "N/A"
    stars       = repo.get("stargazers_count", 0)
    url         = repo.get("html_url", "")
    homepage    = repo.get("homepage") or ""

    live_line = f"| **Live Link** | [{homepage}]({homepage}) |\n" if homepage else ""

    return (
        f"<details>\n"
        f"<summary><b>❖ {name}</b></summary>\n\n"
        f"| | |\n"
        f"| :--- | :--- |\n"
        f"| **Description** | {description} |\n"
        f"| **Language** | {language} |\n"
        f"| **Stars** | ⭐ {stars} |\n"
        f"| **Repository** | [{USERNAME}/{name}]({url}) |\n"
        f"{live_line}"
        f"\n</details>\n"
    )

# ── Replace content between markers ─────────────────────────────────────────
def replace_between(content, start_marker, end_marker, new_content):
    pattern = re.compile(
        rf"({re.escape(start_marker)}\n)(.*?)({re.escape(end_marker)})",
        re.DOTALL,
    )
    replacement = rf"\g<1>{new_content}\g<3>"
    return pattern.sub(replacement, content)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    repos = fetch_repos()
    user  = fetch_user()

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    repo_count  = user.get("public_repos", len(repos))

    # ── 1. Find new repos not yet listed ────────────────────────────────────
    new_repos = [
        r for r in repos
        if r["name"] not in MANUALLY_LISTED and not r.get("fork", False)
    ]
    new_repos.sort(key=lambda r: r.get("updated_at", ""), reverse=True)

    # ── 2. Build new projects block ──────────────────────────────────────────
    if new_repos:
        projects_block = "\n" + "\n".join(build_project_card(r) for r in new_repos) + "\n"
    else:
        projects_block = "\n"

    # ── 3. Build updated stats rows ──────────────────────────────────────────
    stats_block = (
        f"| **Production Shipped** | Deployed fully operational SaaS platforms and tools across Vercel & Cloudflare | **{repo_count}+ Live Products** |\n"
        f"| **Open Source** | Maintained active public repositories, source-available tooling, and utilities | **{repo_count} Public Repos** |\n"
        f"| **Total Stars** | Stars earned across all public repositories on GitHub | **⭐ {total_stars} Stars** |\n"
    )

    # ── 4. Update README ────────────────────────────────────────────────────
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between(content, "<!-- AUTO_PROJECTS_START -->", "<!-- AUTO_PROJECTS_END -->", projects_block)
    content = replace_between(content, "<!-- AUTO_STATS_START -->",    "<!-- AUTO_STATS_END -->",    stats_block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ README updated — {repo_count} repos, ⭐ {total_stars} stars, {len(new_repos)} new projects added.")

if __name__ == "__main__":
    main()
