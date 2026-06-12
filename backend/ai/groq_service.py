from groq import Groq
from dotenv import load_dotenv
from .prompts import CLASSIFICATION_PROMPT
import os
import json

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def classify_context(context):

    if isinstance(context, dict):
        window_title = context.get("windowTitle", "Unknown")
        source_app = context.get("sourceApp", "Unknown")
        raw_text = context.get("rawContext", "")
        formatted_context = (
            f"Source App: {source_app}\n"
            f"Window Title: {window_title}\n"
            f"Clipboard Text / Content:\n{raw_text}"
        )
    else:
        formatted_context = str(context)

    prompt = CLASSIFICATION_PROMPT.replace(
        "{context}",
        formatted_context
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    result = response.choices[0].message.content

    # Remove markdown formatting
    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    try:
        return json.loads(result)

    except Exception as e:

        print("\nJSON Parsing Failed")
        print(e)

        return {
            "title": "Parsing Error",
            "summary": result,
            "type": "General Note",
            "intent": "",
            "topic": "",
            "tags": [],
            "sensitivity": "Low",
            "usefulnessScore": 0,
            "suggestedNextAction": ""
        }