CONTEXT_PACK_PROMPT = """
You are an AI assistant.

Given these memories, generate:

Current Work
Relevant Background
Recent Context
Important Decisions
Suggested Next Step
ChatGPT Prompt

Memories:

{memories}

Return plain text.

Format exactly like:

Current Work:
...

Relevant Background:
...

Recent Context:
...

Important Decisions:
...

Suggested Next Step:
...

ChatGPT Prompt:
...

Do not use markdown.
Do not use bullet points.
Do not use numbering.
Do not use **.
Do not surround anything with quotes.
"""