# ai_helpers.py
import os

def llm_clean_toc_lines(lines: list[str]) -> list[str]:
    """
    Optional: send batches of ToC lines to your LLM to normalize
    (join wrapped lines, fix spacing). Stub returns as-is.
    """
    # integrate your provider here (OpenAI/Azure/Local). Keep deterministic prompts.
    return lines

def llm_autotags_for_section(text: str, max_tags: int = 5) -> list[str]:
    """
    Optional: tag a section with brief keywords using an LLM. Stub returns [].
    """
    return []
