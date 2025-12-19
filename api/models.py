from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DocumentSession(BaseModel):
    id: str
    filename: str
    page_count: int
    current_page: int = 0
    created_at: datetime
    last_modified: datetime


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


class CanvasData(BaseModel):
    objects: List[Dict[str, Any]]
    zoom: float = 1.0
    background_image: Optional[str] = None
    overlay_image: Optional[str] = None


class TextAnnotation(BaseModel):
    text: str
    x: float
    y: float
    font_size: Optional[int] = 12
    color: Optional[str] = "#000000"


class ImageAnnotation(BaseModel):
    image_data: str  # Base64 encoded
    x: float
    y: float
    width: float
    height: float


class MetadataUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
