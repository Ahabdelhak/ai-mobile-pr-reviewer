import requests
from typing import Dict, List, Optional

class GitHubClient:
    """Handles GitHub API interactions."""
    
    def __init__(self, token: str, repo: str):
        self.api_base = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Perform a GET request to the GitHub API."""
        r = requests.get(
            f"{self.api_base}/{endpoint}",
            headers=self.headers,
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    
    def post(self, endpoint: str, body: Dict) -> Dict:
        """Perform a POST request to the GitHub API."""
        r = requests.post(
            f"{self.api_base}/{endpoint}",
            headers=self.headers,
            json=body,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    
    def fetch_changed_files(self, pr_number: int) -> List[Dict]:
        """Fetch all changed files in a PR with pagination."""
        files, page = [], 1
        while True:
            chunk = self.get(f"pulls/{pr_number}/files", params={"page": page, "per_page": 100})
            files.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return files
    
    def post_comment(self, pr_number: int, body: str) -> Dict:
        """Post a comment on a PR."""
        return self.post(f"issues/{pr_number}/comments", {"body": body})