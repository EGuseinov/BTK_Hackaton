from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    product: str

class ChatResponse(BaseModel):
    reply: str
