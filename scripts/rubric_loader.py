import requests
from typing import Optional

class RubricLoader:
    """Loads the review rubric from a URL or provides a fallback."""
    
    def __init__(self, rubric_url: Optional[str]):
        self.rubric_url = rubric_url
    
    def load_rubric(self) -> str:
        """Load rubric from URL or return fallback content."""
        try:
            if self.rubric_url:
                r = requests.get(self.rubric_url, timeout=10)
                r.raise_for_status()
                return r.text
            else:
                return "No rubric URL provided."
        except Exception as e:
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

(⚠️ Failed to load rubric from {self.rubric_url}: {e})
"""