from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from services.context_pack import generate_context_pack

router = APIRouter()


class ContextPackRequest(BaseModel):
    memory_id: Optional[int] = None
    memory_ids: Optional[List[int]] = None


@router.post("/context-pack")
def context_pack(payload: ContextPackRequest):
    ids = []
    if payload.memory_ids:
        ids = payload.memory_ids
    elif payload.memory_id is not None:
        ids = [payload.memory_id]

    result = generate_context_pack(ids if ids else None)

    return {

        "contextPack": result

    }