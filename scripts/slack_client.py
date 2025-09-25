import requests
from typing import Dict, Optional

class SlackClient:
    """Handles Slack incoming webhook posts."""
    
    def __init__(self, webhook_url: Optional[str]):
        self.webhook_url = webhook_url
    
    def post_message(self, message: str, channel: Optional[str] = None) -> bool:
        """Post a message to Slack via webhook."""
        if not self.webhook_url:
            return False  # Silently skip if not configured
        
        payload = {"text": message}
        if channel:
            payload["channel"] = channel
        
        try:
            r = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )
            r.raise_for_status()
            return True
        except Exception:
            # Log failure but don't raise (non-blocking)
            print("⚠️ Slack alert failed (continuing...)")
            return False