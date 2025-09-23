# 🤖 AI Mobile PR Reviewer

**AI Mobile PR Reviewer** is a GitHub Action that automatically reviews pull requests for **mobile codebases** (Android, iOS,cross-platform).  
It leverages advanced LLMs and a central rubric to provide structured, actionable feedback — saving reviewers’ time and improving code quality.

---

## ✨ Features

- 🔍 **Mobile-focused reviews** — Kotlin, Java, Swift, Objective-C, Gradle, XML, plist…  
- 📑 **Org-wide rubric** — consistent review standards across all repos.  
- 🚦 **Risk assessment** — each PR is flagged as Low / Medium / High risk.  
- ✅ **Actionable suggestions** — correctness, performance, security, maintainability, testing.  
- 🤝 **Seamless GitHub integration** — posts a structured review comment directly on PRs.  
- 🪶 **Lightweight** — no infra to maintain, runs entirely via GitHub Actions.
---

## 🎥 Demo Ai Reviewer

Check out a real demo review here:  
👉 [View Demo Review](https://github.com/Ahabdelhak/InstaCrypto/pull/9#issuecomment-3315928198)

*(This shows how the AI reviewer leaves structured comments directly on a pull request.)*

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

## 📝 TO DO (Roadmap)

Planned improvements for upcoming releases:

- [X] Cost optimization (batching diffs, token limits, caching)
- [ ] Multi-language support (React Native, C++ for mobile)
- [ ] Configurable rubric per repo (override central rubric with local rules)
- [ ] Inline review comments (comment directly on code lines, not just summary)
- [ ] Custom model selection (support for GPT-4.1, Anthropic, open-source LLMs)
- [ ] Rich reporting (summary + checklist in Markdown tables)
- [ ] Slack/Teams integration (notify teams of high-risk PRs)

## 🤝 Contributing

Contributions are welcome! 🎉

Ideas, bug reports, and pull requests help make this tool better for everyone.

 * Fork the repo
 * Create a feature branch
 * Submit a pull request

Please follow our rubric style and keep features mobile-focused.

# ⚠️ License
```xml
Copyright 2025 AHMED ABDELHAK, All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
