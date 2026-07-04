#!/usr/bin/env python3
"""
Auto-update README.md with latest GitHub data:
  1. Header capsule-render  → "N+ Projects Shipped"
  2. Typing SVG animation   → "N+ Projects Shipped & Live"
  3. Achievements table     → Stars count, Repo count
  4. New repos              → Auto-add project cards
"""

import os
import re
import requests

USERNAME    = "Rupam852"
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
    repos, page = [], 1
    while True:
        url  = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=public"
        data = requests.get(url, headers=HEADERS).json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

# ── Fetch user profile ───────────────────────────────────────────────────────
def fetch_user():
    return requests.get(f"https://api.github.com/users/{USERNAME}", headers=HEADERS).json()

# ── Build markdown card for a new repo ──────────────────────────────────────
def build_project_card(repo):
    name        = repo.get("name", "")
    description = repo.get("description") or "No description provided."
    language    = repo.get("language") or "N/A"
    stars       = repo.get("stargazers_count", 0)
    url         = repo.get("html_url", "")
    homepage    = repo.get("homepage") or ""
    live_line   = f"| **Live Link** | [{homepage}]({homepage}) |\n" if homepage else ""
    return (
        f"<details>\n"
        f"<summary><b>❖ {name}</b></summary>\n\n"
        f"| | |\n| :--- | :--- |\n"
        f"| **Description** | {description} |\n"
        f"| **Language** | {language} |\n"
        f"| **Stars** | ⭐ {stars} |\n"
        f"| **Repository** | [{USERNAME}/{name}]({url}) |\n"
        f"{live_line}\n</details>\n"
    )

# ── Replace content between comment markers ──────────────────────────────────
def replace_between(content, start_marker, end_marker, new_content):
    pattern = re.compile(
        rf"({re.escape(start_marker)}\n)(.*?)({re.escape(end_marker)})",
        re.DOTALL,
    )
    return pattern.sub(rf"\g<1>{new_content}\g<3>", content)

# ── Update header capsule "N+ Projects Shipped" ──────────────────────────────
def update_header_capsule(content, count):
    # Matches: %20NN%2B%20Projects%20Shipped  (URL-encoded " N+ Projects Shipped")
    return re.sub(
        r"(%20)\d+(%2B%20Projects%20Shipped)",
        rf"\g<1>{count}\g<2>",
        content,
    )

# ── Update typing SVG "N+ Projects Shipped & Live" ──────────────────────────
def update_typing_svg(content, count):
    # Matches: NN%2B+Projects+Shipped+%26+Live
    return re.sub(
        r"\d+(%2B\+Projects\+Shipped\+%26\+Live)",
        rf"{count}\g<1>",
        content,
    )

# ── Update experience "14+ live deployments" line ───────────────────────────
def update_experience_line(content, count):
    return re.sub(
        r"Maintained \d+\+ live deployments",
        f"Maintained {count}+ live deployments",
        content,
    )

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    repos = fetch_repos()
    user  = fetch_user()

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    repo_count  = user.get("public_repos", len(repos))

    # ── Find new repos not yet in Featured Projects ──────────────────────────
    new_repos = sorted(
        [r for r in repos if r["name"] not in MANUALLY_LISTED and not r.get("fork")],
        key=lambda r: r.get("updated_at", ""),
        reverse=True,
    )

    # ── Build blocks ─────────────────────────────────────────────────────────
    projects_block = ("\n" + "\n".join(build_project_card(r) for r in new_repos) + "\n") if new_repos else "\n"

    stats_block = (
        f"| **Production Shipped** | Deployed fully operational SaaS platforms and tools across Vercel & Cloudflare | **{repo_count}+ Live Products** |\n"
        f"| **Open Source** | Maintained active public repositories, source-available tooling, and utilities | **{repo_count} Public Repos** |\n"
        f"| **Total Stars** | Stars earned across all public repositories on GitHub | **⭐ {total_stars} Stars** |\n"
    )

    # ── Apply all updates ─────────────────────────────────────────────────────
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between(content, "<!-- AUTO_PROJECTS_START -->", "<!-- AUTO_PROJECTS_END -->", projects_block)
    content = replace_between(content, "<!-- AUTO_STATS_START -->",    "<!-- AUTO_STATS_END -->",    stats_block)
    content = update_header_capsule(content, repo_count)
    content = update_typing_svg(content, repo_count)
    content = update_experience_line(content, repo_count)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ README updated:")
    print(f"   📦 Repos     : {repo_count}")
    print(f"   ⭐ Stars     : {total_stars}")
    print(f"   🆕 New cards : {len(new_repos)}")
    print(f"   🎬 Header    : {repo_count}+ Projects Shipped")
    print(f"   ✍️  Typing SVG: {repo_count}+ Projects Shipped & Live")

if __name__ == "__main__":
    main()

