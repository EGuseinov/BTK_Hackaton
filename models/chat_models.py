from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    product: str # Gelecekte kullanılabilir diye ekledik

class ChatResponse(BaseModel):
    reply: str
