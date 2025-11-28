from pydantic import BaseModel
from typing import Optional

class Download(BaseModel):
    current_file: str
    progress: int
    max_progress: int

class ErrorEvent(BaseModel):
    func: str
    error: str

class LoadEvent(BaseModel):
    type: str
    success: Optional[bool] = None

class DeleteEvent(BaseModel):
    obj_type: str
    obj_id: int