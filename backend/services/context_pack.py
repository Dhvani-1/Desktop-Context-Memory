from database.db import SessionLocal
from database.models import Memory
from ai.context_pack_prompt import CONTEXT_PACK_PROMPT

from ai.groq_service import client


def generate_context_pack(memory_ids=None):

    db = SessionLocal()

    if memory_ids:
        memories = db.query(Memory).filter(Memory.id.in_(memory_ids)).all()
    else:
        memories = db.query(Memory).filter(Memory.pending_confirmation != 1).all()

    db.close()

    # Prioritize memories: sort so that isImportant = True/1 comes first
    memories = sorted(memories, key=lambda m: getattr(m, 'isImportant', False) or False, reverse=True)

    memory_text = ""

    for memory in memories:
        is_imp = getattr(memory, 'isImportant', False)
        importance_str = " (Priority: Important)" if is_imp else ""
        memory_title = getattr(memory, 'title', '') or 'Memory Chunk'
        memory_text += (
            f"Title: {memory_title}{importance_str}\n"
            f"Summary: {memory.summary}\n"
            f"Type: {memory.type}\n\n"
        )

    prompt = CONTEXT_PACK_PROMPT.replace(
        "{memories}",
        memory_text
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

    result = result.replace("\\n", "\n")

    return result