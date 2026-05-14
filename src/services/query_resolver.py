"""Query resolver — semantic resolution now handled by the SLM rewrite step.

This module previously contained deterministic ordinal and vague-reference
parsing. That logic was brittle (e.g. "3rd one" matched "one"→1 instead of
"3rd"→3) and is superseded by the SLM query rewrite in LLMService.rewrite_query.

Kept as a module stub so existing imports do not break.
"""
