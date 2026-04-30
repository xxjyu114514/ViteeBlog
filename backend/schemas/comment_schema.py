from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserSimpleOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    parent_id: Optional[int]
    user_id: int
    created_at: datetime
    author: UserSimpleOut

    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    reason: str = Field(..., min_length=2, max_length=200)

class ReportResponse(BaseModel):
    id: int
    reason: str
    is_resolved: bool
    created_at: datetime
    comment: CommentResponse
    reporter: UserSimpleOut

    class Config:
        from_attributes = True


####