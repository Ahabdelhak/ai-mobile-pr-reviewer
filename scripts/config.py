import os
import sys
from typing import Optional

class Config:
    """Centralized configuration for environment variables."""
    
    def __init__(self):
        # Required environment variables
        self.github_token: str = os.environ.get("GITHUB_TOKEN", "")
        self.repo: str = os.environ.get("GITHUB_REPOSITORY", "")
        self.event_path: str = os.environ.get("GITHUB_EVENT_PATH", "")
        self.openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
        
        # Optional environment variables with defaults
        self.model_name: str = os.environ.get("MODEL_NAME", "gpt-4o-mini")
        self.max_patch_chars: int = int(os.environ.get("MAX_PATCH_CHARS", "12000"))
        self.max_files: int = int(os.environ.get("MAX_FILES", "25"))
        self.file_globs: str = os.environ.get(
            "FILE_GLOBS",
            "*.kt,*.kts,*.java,*.xml,*.swift,*.m,*.mm,*.gradle,*.gradle.kts,*.pro,*.plist,*.md"
        )
        self.rubric_url: str = os.environ.get(
            "RUBRIC_URL",
            "https://raw.githubusercontent.com/Ahabdelhak/ai-mobile-pr-reviewer/main/rubric/mobile_review.md"
        )
    
    def validate(self) -> None:
        """Validate required environment variables."""
        if not all([self.github_token, self.repo, self.event_path, self.openai_api_key]):
            print("❌ Missing required env vars: GITHUB_TOKEN / GITHUB_REPOSITORY / GITHUB_EVENT_PATH / OPENAI_API_KEY")
            sys.exit(1)

def load_config() -> Config:
    """Factory method to create and validate configuration."""
    config = Config()
    config.validate()
    return config