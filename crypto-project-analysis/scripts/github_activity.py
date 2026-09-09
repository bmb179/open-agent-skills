#!/usr/bin/env python3
"""
github_activity.py — Basic GitHub repo metrics (keyless public API)
Part of crypto-project-analysis skill. Quantitative proxy for Community / Developer ecosystem health and Product/Tech activity.

Usage:
  python github_activity.py owner/repo
  Example: python github_activity.py Uniswap/v3-core
"""

import sys
import json
import urllib.request
from typing import Dict, Any, Optional

def fetch_json(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "crypto-project-analysis-skill/1.0",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] GitHub {url}: {e}", file=sys.stderr)
    return None

def get_repo_metrics(repo_path: str) -> Dict[str, Any]:
    """repo_path like 'owner/repo' """
    url = f"https://api.github.com/repos/{repo_path}"
    data = fetch_json(url)
    if not data:
        return {"error": f"Could not fetch repo {repo_path}. Check spelling or if public."}

    return {
        "source": "github_public_api",
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "watchers": data.get("watchers_count"),
        "open_issues": data.get("open_issues_count"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "language": data.get("language"),
        "checklist_note": "Quantitative proxy for developer activity and community interest. High stars + recent pushes = positive signal for Product/Tech and Community sections. Compare to peers. For deeper activity (commits, contributors), use /stats or commits endpoint in follow-up calls if needed."
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github_activity.py owner/repo")
        print("Example: python github_activity.py Uniswap/v3-core or projectname/repo")
        sys.exit(1)

    repo = sys.argv[1]
    data = get_repo_metrics(repo)
    print(json.dumps(data, indent=2))
