import re
from typing import List, Dict

class PromptBuilder:
    """Constructs the OpenAI prompt for PR review."""
    
    def __init__(self, rubric_loader: 'RubricLoader'):
        self.rubric_loader = rubric_loader
    
    def detect_mobile_context(self, file_summaries: List[Dict]) -> str:
        """Detect mobile context from file names."""
        names = " ".join(f["filename"] for f in file_summaries)
        hints = []
        if re.search(r"\.(kt|kts|java)\b", names): hints.append("Android/Kotlin")
        if re.search(r"\bcompose\b|\b@Composable\b", names, re.IGNORECASE): hints.append("Jetpack Compose")
        if re.search(r"\.(swift|mm|m)\b", names): hints.append("iOS/Swift")
        if re.search(r"\bSwiftUI\b|\b@State(Object)?\b", names): hints.append("SwiftUI")
        if re.search(r"\bgradle(\.kts)?\b|\bproguard\b", names, re.IGNORECASE): hints.append("Gradle/ProGuard")
        if re.search(r"\bplist\b", names): hints.append("Info.plist")
        return ", ".join(sorted(set(hints))) or "Mobile (Android/iOS) code"
    
    def make_prompt(self, pr_title: str, pr_body: str, file_summaries: List[Dict]) -> str:
        """Construct the complete OpenAI prompt."""
        rubric_text = self.rubric_loader.load_rubric()
        context_hint = self.detect_mobile_context(file_summaries)
        
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