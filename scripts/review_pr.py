#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Mobile based PR Reviewer
- Mobile-focused rubric (Android/iOS/cross-platform)
- Loads rubric from central URL (RUBRIC_URL), supports private repos via RUBRIC_TOKEN
- Filters noisy/binary/irrelevant files by glob + ignore rules
- Summarizes diffs and posts one structured PR review comment

Environment (provided by GitHub Actions + secrets):
  GITHUB_TOKEN        (required)
  GITHUB_REPOSITORY   (required, e.g. org/repo)
  GITHUB_EVENT_PATH   (required)
  OPENAI_API_KEY      (required)
  MODEL_NAME          (optional, default: gpt-4o-mini)
  MAX_PATCH_CHARS     (optional, default: 12000)
  MAX_FILES           (optional, default: 25)
  FILE_GLOBS          (optional, default covers Kotlin/Swift/Gradle/XML/plist)
"""

import os
import re
import sys
import json
from typing import List, Dict

import requests

# ---- Required env ----
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
REPO            = os.environ.get("GITHUB_REPOSITORY", "")
EVENT_PATH      = os.environ.get("GITHUB_EVENT_PATH", "")
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "")

# ---- Optional env ----
MODEL_NAME      = os.environ.get("MODEL_NAME", "gpt-4o-mini")
MAX_PATCH_CHARS = int(os.environ.get("MAX_PATCH_CHARS", "12000"))
MAX_FILES       = int(os.environ.get("MAX_FILES", "25"))
FILE_GLOBS      = os.environ.get("FILE_GLOBS", "*.kt,*.kts,*.java,*.xml,*.swift,*.m,*.mm,*.gradle,*.gradle.kts,*.pro,*.plist,*.md")
RUBRIC_URL      = os.environ.get("RUBRIC_URL", "https://raw.githubusercontent.com/Ahabdelhak/ai-mobile-pr-reviewer/main/rubric/mobile_review.md")

if not (GITHUB_TOKEN and REPO and EVENT_PATH and OPENAI_API_KEY):
    print("Missing required env vars: GITHUB_TOKEN / GITHUB_REPOSITORY / GITHUB_EVENT_PATH / OPENAI_API_KEY")
    sys.exit(1)

# ---- Load PR event ----
with open(EVENT_PATH, "r", encoding="utf-8") as f:
    event = json.load(f)

pr = event.get("pull_request") or {}
pr_number = pr.get("number")
if not pr_number:
    print("Not a PR event. Exiting.")
    sys.exit(0)

api_base = f"https://api.github.com/repos/{REPO}"

# ---- HTTP helpers ----
def gh_get(url: str, params=None):
    r = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def gh_post(url: str, body: Dict):
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json=body,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()

def post_comment_on_pr(body: str):
    gh_post(f"{api_base}/issues/{pr_number}/comments", {"body": body})

# ---- File filtering ----
# Convert comma-separated globs to a regex (e.g., "*.kt,*.swift" -> (.*\.kt|.*\.swift)$)
def compile_glob_regex(globs: str):
    parts = [p.strip().replace(".", r"\.").replace("*", ".*") for p in globs.split(",") if p.strip()]
    if not parts:
        return None
    return re.compile(r"(" + r"|".join(parts) + r")$", re.IGNORECASE)

GLOB_RE = compile_glob_regex(FILE_GLOBS)

def is_ignored(filename: str) -> bool:
    ignore_patterns = [
        r"(^|/)(dist|build|outputs|out|coverage|node_modules|Pods|vendor|\.git)/",
        r"(^|/)DerivedData/",
        r"\.(min\.js|lock|png|jpg|jpeg|gif|svg|ico|pdf|zip|gz|tgz|jar|aab|apk|mp3|mp4|mov|webm|woff2?)$",
        r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|composer\.lock)$",
        r"(^|/)(\.gradle/|\.idea/|\.vs/)"
    ]
    if any(re.search(p, filename, re.IGNORECASE) for p in ignore_patterns):
        return True
    if GLOB_RE and not GLOB_RE.search(filename):
        return True
    return False

def fetch_changed_files() -> List[Dict]:
    files, page = [], 1
    while True:
        chunk = gh_get(f"{api_base}/pulls/{pr_number}/files", params={"page": page, "per_page": 100})
        files.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return files

def sanitize_patch(patch: str) -> str:
    if not patch:
        return ""
    # Keep only first N chars; trim very long lines
    patch = patch[:MAX_PATCH_CHARS]
    out_lines = []
    for line in patch.splitlines():
        if len(line) > 2000:
            out_lines.append(line[:2000] + " …(trimmed)")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)

# ---- Rubric loading ----
def load_rubric() -> str:
    try:
        if RUBRIC_URL:
            r = requests.get(RUBRIC_URL, timeout=10)
            r.raise_for_status()
            return r.text
        else:
            return "No rubric URL provided."
    except Exception as e:
        # Minimal fallback rubric
        return f"""
# AI Mobile PR Review Rubric (Fallback)

## Correctness
- Android lifecycle & coroutines; iOS ARC & SwiftUI state; proper async/error handling.

## Performance
- Avoid UI-thread blocking; efficient Compose/SwiftUI updates; memory/caching.

## Security
- No hardcoded secrets; secure storage (EncryptedSharedPreferences/Keychain); TLS/HTTPS; WebView safety.

## Readability / Maintainability
- Clean architecture (MVVM/MVI); DI; idiomatic Kotlin/Swift.

## Testing / Coverage
- Unit tests for ViewModels/UseCases; UI tests; offline/retry edge cases.

(⚠️ Failed to load rubric from {RUBRIC_URL}: {e})
"""

# ---- Context hints (helps the LLM tailor the review) ----
def detect_mobile_context(file_summaries: List[Dict]) -> str:
    names = " ".join(f["filename"] for f in file_summaries)
    hints = []
    if re.search(r"\.(kt|kts|java)\b", names): hints.append("Android/Kotlin")
    if re.search(r"\bcompose\b|\b@Composable\b", names, re.IGNORECASE): hints.append("Jetpack Compose")
    if re.search(r"\.(swift|mm|m)\b", names): hints.append("iOS/Swift")
    if re.search(r"\bSwiftUI\b|\b@State(Object)?\b", names): hints.append("SwiftUI")
    if re.search(r"\bgradle(\.kts)?\b|\bproguard\b", names, re.IGNORECASE): hints.append("Gradle/ProGuard")
    if re.search(r"\bplist\b", names): hints.append("Info.plist")
    return ", ".join(sorted(set(hints))) or "Mobile (Android/iOS) code"

# ---- Prompt construction ----
def make_prompt(pr_title: str, pr_body: str, file_summaries: List[Dict]) -> str:
    rubric_text = load_rubric()
    context_hint = detect_mobile_context(file_summaries)

    files_block_parts = []
    for f in file_summaries:
        files_block_parts.append(
            f"""FILE: {f['filename']}
STATUS: {f.get('status')}
CHANGES: +{f.get('additions')} / -{f.get('deletions')}
PATCH (trimmed):
{f['patch']}
""".rstrip()
        )
    files_block = "\n\n".join(files_block_parts)

        pr_overview = f"PR TITLE: {pr_title}\n\nPR DESCRIPTION:\n{pr_body or '(no description)'}"

    mobile_guidance = """
You are an expert senior mobile engineer (Android/iOS). Review ONLY the provided diffs.
Produce:
1) High-level PR summary
2) Findings grouped: Correctness, Performance, Security, Readability/Maintainability, Testing/Coverage
3) Actionable suggestions (brief, with code snippet if needed)
4) Risk Assessment: Low/Medium/High + pre-merge checklist
5) TODOs / Follow-ups
Be concise and avoid speculation beyond the diffs.
"""

    return f"""{mobile_guidance}

{rubric_text}

Detected stack hints: {context_hint}

{pr_overview}

--- BEGIN DIFFS ---
{files_block}
--- END DIFFS ---
"""

# ---- LLM call ----
def openai_review(prompt: str) -> str:
    import openai
    openai.api_key = OPENAI_API_KEY
    resp = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a senior staff mobile engineer reviewing pull requests with precision and practicality."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

# ---- Main flow ----
def main():
    # Gather changed files
    changed_files = fetch_changed_files()

    # Filter & prepare
    prepared: List[Dict] = []
    for f in changed_files:
        filename = f.get("filename") or ""
        if is_ignored(filename):
            continue
        patch = sanitize_patch(f.get("patch") or "")
        if not patch.strip():
            continue  # skip empty/rename/binary
        prepared.append({
            "filename": filename,
            "status": f.get("status"),
            "additions": f.get("additions"),
            "deletions": f.get("deletions"),
            "patch": patch,
        })
        if len(prepared) >= MAX_FILES:
            break

    if not prepared:
        post_comment_on_pr("🤖 **AI Mobile PR Review**: No eligible text diffs to review (binary/ignored/empty).")
        return

    pr_title = pr.get("title", "")
    pr_body  = pr.get("body", "")

    prompt = make_prompt(pr_title, pr_body, prepared)

    try:
        review = openai_review(prompt)
        header = "### 🤖 AI Mobile PR Review\n"
        footer = "\n\n---\n_This is an automated mobile-focused review. Please verify suggestions before applying._"
        post_comment_on_pr(header + review + footer)
    except Exception as e:
        post_comment_on_pr(f"🤖 **AI Mobile PR Review** failed: `{e}`")

if __name__ == "__main__":
    main()
