import requests
import re
import os
from .log import logger
from typing import List, Optional


class AIMigrationHelper:
    def __init__(self):
        self._session = requests.Session()
        self._timeout = int(os.getenv("AI_MIGRATION_TIMEOUT", 30))
        self._webhook_url = os.getenv("AI_MIGRATION_WEBHOOK_URL")
        self.suggestions = {}

    def transform_code_block(self, key, code_block: str, prompt: str) -> Optional[str]:
        if not self._webhook_url:
            return None

        payload = {"content": code_block, "prompt": prompt}

        try:
            response = self._session.post(
                self._webhook_url,
                json=payload,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                logger.error(f"AI agent error {response.status_code}: {response.text}")
                return None

            result = response.json()
            should_replace = result.get(
                "replace", False
            )  # This has not yet been tested, so it is always False.
            content = result.get("output", "")
            show_suggestion = result.get("show_change", False)

            if not content:
                return None

            if should_replace and content:
                return content

            if show_suggestion:
                self.suggestions.setdefault(key, []).append(content)
                logger.info(f"AI suggestion for {key}:\n{content}")

        except requests.exceptions.Timeout:
            logger.error("AI agent timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"AI agent connection error: {e}")
        except Exception as e:
            logger.error(f"AI agent unexpected error: {e}")

    def apply_ai_transforms(self, content: str, ai_transforms: List[tuple]) -> str:
        if not ai_transforms:
            return content

        for patterns, prompt in ai_transforms:
            if not prompt:
                continue
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
                if not matches:
                    continue

                for match in reversed(matches):
                    code_with_context = self._get_code_with_context(content, match)
                    self.transform_code_block(pattern, code_with_context, prompt)

    def _get_code_with_context(self, content: str, match) -> str:
        lines = content.split("\n")
        start_line = content[: match.start()].count("\n")
        end_line = content[: match.end()].count("\n")

        context_start = max(0, start_line - 5)
        context_end = min(len(lines) - 1, end_line + 5)

        return "\n".join(lines[context_start : context_end + 1])
