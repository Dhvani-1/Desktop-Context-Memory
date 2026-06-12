from pydantic import BaseModel


class ContextResponse(BaseModel):
    sourceApp: str
    windowTitle: str
    timestamp: str
    contextSource: str
    rawContext: str
    url: str
    sessionId: str
    screenshot: str