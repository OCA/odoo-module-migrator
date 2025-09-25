import requests
import re
import os
from .log import logger
from typing import List, Optional


class AIMigrationHelper:
    def __init__(self):
        self._session = requests.Session()
        self._timeout = int(os.getenv("AI_MIGRATION_TIMEOUT", 30))
        self._webhook_url = os.getenv("AI_SUGGESTION_WEBHOOK")
        self.suggestions = {}

    def transform_code_block(self, code_block: str, prompt: str) -> Optional[str]:
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
            content = result.get("output", "")
            show_suggestion = result.get("show_change", False)

            if not content:
                return None

            if show_suggestion:
                return content

        except requests.exceptions.Timeout:
            logger.error("AI agent timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"AI agent connection error: {e}")
        except Exception as e:
            logger.error(f"AI agent unexpected error: {e}")
        return ""

    def apply_ai_transforms(
        self, filename: str, extension: str, content: str, ai_transforms: List[tuple]
    ):
        if not ai_transforms:
            return

        for extensions, patterns, prompt in ai_transforms:
            if not prompt or extension not in extensions:
                continue
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
                if not matches:
                    continue
                for match in reversed(matches):
                    (
                        code_with_context,
                        line_start,
                        line_end,
                    ) = self._get_code_with_context(content, match)
                    suggestion = self.transform_code_block(code_with_context, prompt)
                    if (
                        suggestion
                        and (filename, line_start, line_end) not in self.suggestions
                    ):
                        self.suggestions[(filename, line_start, line_end)] = suggestion

    def _get_code_with_context(self, content: str, match) -> tuple:
        lines = content.split("\n")
        match_line = content[: match.start()].count("\n")

        function_start = None
        for i in range(match_line, -1, -1):
            line = lines[i].strip()
            if line.startswith(("def ", "class ", "async def ")):
                function_start = i
                break

        if function_start is None:
            offset = 20
            context_start = max(0, match_line - offset)
            context_end = min(len(lines) - 1, match_line + offset)
            return (
                "\n".join(lines[context_start : context_end + 1]),
                context_start + 1,
                context_end + 1,
            )

        base_indent = len(lines[function_start]) - len(lines[function_start].lstrip())
        function_end = len(lines) - 1

        for i in range(function_start + 1, len(lines)):
            line = lines[i]
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= base_indent:
                    function_end = i - 1
                    break

        return (
            "\n".join(lines[function_start : function_end + 1]),
            function_start + 1,
            function_end + 1,
        )
