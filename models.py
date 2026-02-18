from datetime import datetime, timezone
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, Column, JSON

class LandmarkHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    english_info: str
    hindi_info: str
    # New: Store full metadata if you want to save confidence scores or extra AI notes
    extra_metadata: Optional[Dict] = Field(default={}, sa_column=Column(JSON)) 
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )