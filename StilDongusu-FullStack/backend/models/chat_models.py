# models/chat_models.py

from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    message: str
    product: str

# YENİ: Görsel Kombin İsteği Modeli
class VisualComboRequest(BaseModel):
    main_item: str
    matched_items: List[str]