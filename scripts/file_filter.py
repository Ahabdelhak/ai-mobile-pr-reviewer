import re
from typing import Optional

class FileFilter:
    """Handles file filtering based on glob and ignore patterns."""
    
    def __init__(self, file_globs: str):
        self.glob_re = self._compile_glob_regex(file_globs)
        self.ignore_patterns = [
            r"(^|/)(dist|build|outputs|out|coverage|node_modules|Pods|vendor|\.git)/",
            r"(^|/)DerivedData/",
            r"\.(min\.js|lock|png|jpg|jpeg|gif|svg|ico|pdf|zip|gz|tgz|jar|aab|apk|mp3|mp4|mov|webm|woff2?)$",
            r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|composer\.lock)$",
            r"(^|/)(\.gradle/|\.idea/|\.vs/)"
        ]
    
    def _compile_glob_regex(self, globs: str) -> Optional[re.Pattern]:
        """Compile glob patterns into a regex."""
        parts = [p.strip().replace(".", r"\.").replace("*", ".*") for p in globs.split(",") if p.strip()]
        if not parts:
            return None
        return re.compile(r"(" + r"|".join(parts) + r")$", re.IGNORECASE)
    
    def is_ignored(self, filename: str) -> bool:
        """Check if a file should be ignored based on patterns."""
        if any(re.search(p, filename, re.IGNORECASE) for p in self.ignore_patterns):
            return True
        if self.glob_re and not self.glob_re.search(filename):
            return True
        return False
    
    def sanitize_patch(self, patch: str, max_chars: int) -> str:
        """Sanitize and trim patch content."""
        if not patch:
            return ""
        patch = patch[:max_chars]
        out_lines = []
        for line in patch.splitlines():
            if len(line) > 2000:
                out_lines.append(line[:2000] + " …(trimmed)")
            else:
                out_lines.append(line)
        return "\n".join(out_lines)