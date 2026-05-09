from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ArticleSimpleOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class FavoriteResponse(BaseModel):
    id: int
    created_at: datetime
    article: ArticleSimpleOut

    class Config:
        from_attributes = True
