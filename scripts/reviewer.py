import json
import openai
from typing import List, Dict
from .config import Config
from .http_client import GitHubClient
from .file_filter import FileFilter
from .prompt_builder import PromptBuilder

class PRReviewer:
    """Main PR review workflow."""
    
    def __init__(self, config: Config, github_client: GitHubClient, file_filter: FileFilter, prompt_builder: PromptBuilder):
        self.config = config
        self.github_client = github_client
        self.file_filter = file_filter
        self.prompt_builder = prompt_builder
        
        # Load PR event
        with open(self.config.event_path, "r", encoding="utf-8") as f:
            self.event = json.load(f)
        self.pr = self.event.get("pull_request") or {}
        self.pr_number = self.pr.get("number")
        if not self.pr_number:
            print("Not a PR event. Exiting.")
            sys.exit(0)
    
    def openai_review(self, prompt: str) -> str:
        """Call OpenAI API for review."""
        openai.api_key = self.config.openai_api_key
        resp = openai.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are a senior staff mobile engineer reviewing pull requests with precision and practicality."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    
    def run(self) -> None:
        """Execute the PR review workflow."""
        changed_files = self.github_client.fetch_changed_files(self.pr_number)
        prepared: List[Dict] = []
        
        for f in changed_files:
            filename = f.get("filename") or ""
            if self.file_filter.is_ignored(filename):
                continue
            patch = self.file_filter.sanitize_patch(f.get("patch") or "", self.config.max_patch_chars)
            if not patch.strip():
                continue
            prepared.append({
                "filename": filename,
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "patch": patch,
            })
            if len(prepared) >= self.config.max_files:
                break
        
        if not prepared:
            self.github_client.post_comment(self.pr_number, "🤖 **AI Mobile PR Review**: No eligible text diffs to review (binary/ignored/empty).")
            return
        
        pr_title = self.pr.get("title", "")
        pr_body = self.pr.get("body", "")
        prompt = self.prompt_builder.make_prompt(pr_title, pr_body, prepared)
        
        try:
            review = self.openai_review(prompt)
            header = "### 🤖 AI Mobile PR Review\n"
            footer = "\n\n---\n_This is an automated mobile-focused review. Please verify suggestions before applying._"
            self.github_client.post_comment(self.pr_number, header + review + footer)
        except Exception as e:
            self.github_client.post_comment(self.pr_number, f"🤖 **AI Mobile PR Review** failed: `{e}`")