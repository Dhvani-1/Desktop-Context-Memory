from ai.groq_service import classify_context

text = """
Working on FastAPI routes and SQLite models.
Need dashboard APIs.
"""

result = classify_context(text)

print(result)