from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    product: str

class VisualComboRequest(BaseModel):
    main_item: str
    matched_items: List[str]

class FitScoreRequest(BaseModel):
    user_body_type: str
    product_id: int

class EventStylistRequest(BaseModel):
    user_request: str