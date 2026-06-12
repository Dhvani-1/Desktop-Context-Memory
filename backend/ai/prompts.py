CLASSIFICATION_PROMPT = """
You are a memory classifier.

Your task is to analyze the provided user context and classify the interaction into the most appropriate category type.
The context will contain:
- Source App: The active application name.
- Window Title: The title of the active window.
- Clipboard Text / Content: The text content in the clipboard or active context.

Determine the most accurate "type" based on the following mapping rules:
1. "Research": Set to this if the user is reading documentation, viewing Swagger UI, researching APIs, or browsing websites.
   Indicators: Source App is a web browser (e.g., Google Chrome, Microsoft Edge, Firefox, Brave) AND/OR Window Title contains "docs", "documentation", "swagger", "api", "tutorial", "reference", "manual", "github", "stack overflow", "search", or "wiki".
2. "Coding": Set to this if the user is writing code, editing source files, or configuring development environments.
   Indicators: Source App is an IDE/text editor (e.g., Visual Studio Code, Cursor, PyCharm, Sublime Text) AND window title or clipboard shows active editing of source code files without error logs or exceptions.
3. "Bug": Set to this if the user is debugging errors, looking at stack traces, compiler errors, log outputs, test failures, or exceptions.
   Indicators: Window Title or Clipboard text contains "error", "exception", "fail", "stack trace", "traceback", "debug", "warning", "issue", or logs.
4. "Project": Set to this if the user is performing long-term work, managing roadmaps, viewing boards, or planning.
   Indicators: Window Title contains "board", "jira", "trello", "roadmap", "milestone", "project", "kanban", or "linear".
5. "Task": Set to this if the user is dealing with action items, TODO lists, or quick checklist items.
   Indicators: Window Title or Clipboard text contains "todo", "task", "action item", or checklist.
6. "Decision": Set to this if the user is making or recording important design choices, choosing architectures, or logging trade-offs.
   Indicators: Clipboard contains architecture discussions, pros/cons, design choices, "choice", "selected", "decided to", "conclusion", or "architectural decision".
7. "General Note": Set to this for generic notes, ideas, or general text/context that does not fit any of the categories above.

Return ONLY a valid, parseable JSON object matching this structure:
{
  "title": "",
  "summary": "",
  "type": "",
  "intent": "",
  "topic": "",
  "tags": [],
  "sensitivity": "",
  "usefulnessScore": 0,
  "suggestedNextAction": ""
}

Ensure the "type" matches one of the following exactly (case-sensitive):
- Task
- Project
- Research
- Coding
- Bug
- Meeting
- Writing
- Design
- Decision
- Prompt
- General Note

Context to analyze:
{context}
"""