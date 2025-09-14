# 🤖 AI Mobile PR Reviewer

**AI Mobile PR Reviewer** is a GitHub Action that automatically reviews pull requests for **mobile codebases** (Android, iOS, cross-platform).  
It uses OpenAI’s models and a central rubric to provide structured, actionable feedback — saving reviewers’ time and improving code quality.

---

## ✨ Features

- 🔍 **Mobile-focused reviews** — Kotlin, Java, Swift, Objective-C, Gradle, XML, plist…  
- 📑 **Org-wide rubric** — consistent review standards across all repos.  
- 🚦 **Risk assessment** — each PR is flagged as Low / Medium / High risk.  
- ✅ **Actionable suggestions** — correctness, performance, security, maintainability, testing.  
- 🤝 **Seamless GitHub integration** — posts a structured review comment directly on PRs.  
- 🪶 **Lightweight** — no infra to maintain, runs entirely via GitHub Actions.

---

## 🚀 Setup

### 1. Add this Action to your repo

Create a workflow file at `.github/workflows/ai-mobile-pr-review.yml`:

```yaml
name: AI Mobile PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  review:
    uses: Ahabdelhak/ai-mobile-pr-reviewer/.github/workflows/mobile-pr-review.yml@main
    permissions:
      contents: read
      pull-requests: write
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    with:
      model_name: gpt-4o-mini
      max_files: 25
      max_patch_chars: 12000
      file_globs: "*.kt,*.kts,*.java,*.xml,*.swift,*.m,*.mm,*.gradle,*.gradle.kts,*.pro,*.plist,*.md"
      rubric_url: "https://raw.githubusercontent.com/Ahabdelhak/ai-mobile-pr-reviewer/main/rubric/mobile_review.md"
```

### 2. Add your OpenAI API key

 * Go to your repository → Settings → Secrets and variables → Actions
 * Add a new secret:
    - Name: "OPENAI_API_KEY"
    - Value: "your OpenAI API key"

### 3. Open a Pull Request

The Action will run automatically and leave an AI-generated review comment on the PR.

## ⚙️ How It Works

1. Detects PR event via GitHub Actions
2. Filters relevant files (Kotlin, Swift, Gradle, XML, plist, etc.)
3. Summarizes diffs and trims noisy/binary files
4. Loads rubric from the central repo
5. Builds a context prompt and queries OpenAI model
6. Posts a structured review back as a PR comment

## 🤝 Contributing

Contributions are welcome! 🎉

Ideas, bug reports, and pull requests help make this tool better for everyone.

 * Fork the repo
 * Create a feature branch
 * Submit a pull request

Please follow our rubric style and keep features mobile-focused.
