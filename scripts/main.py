#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from .config import load_config
from .http_client import GitHubClient
from .file_filter import FileFilter
from .rubric_loader import RubricLoader
from .prompt_builder import PromptBuilder
from .reviewer import PRReviewer

def main():
    """Entry point for the AI Mobile PR Reviewer."""
    config = load_config()
    github_client = GitHubClient(config.github_token, config.repo)
    file_filter = FileFilter(config.file_globs)
    rubric_loader = RubricLoader(config.rubric_url)
    prompt_builder = PromptBuilder(rubric_loader)
    reviewer = PRReviewer(config, github_client, file_filter, prompt_builder)
    reviewer.run()

    sys.exit(0)

if __name__ == "__main__":
    main()