# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional


class OCRResult(BaseModel):
    text: str = Field(..., description="Extracted text from the image")
    confidence: float = Field(..., description="Overall confidence score of the extracted text (0-100)")


class AIDescription(BaseModel):
    description: str = Field(..., description="Detailed description of the image content")
    objects: List[str] = Field(..., description="List of objects detected in the image")
    brands: List[str] = Field(default_factory=list, description="Brands, logos, or products detected")
    dominant_colors: List[str] = Field(default_factory=list, description="Dominant colors in the image")
    language: str = Field(..., description="Primary language detected in the text/image")


class AnalyzeResponse(BaseModel):
    id: str = Field(..., description="Unique analysis ID for downloading results later")
    text: str = Field(..., description="Extracted text from the image")
    description: str = Field(..., description="AI generated detailed description")
    objects: List[str] = Field(..., description="Detected objects, brands, logos, etc.")
    brands: List[str] = Field(default_factory=list, description="Brands, logos, or products detected")
    dominant_colors: List[str] = Field(default_factory=list, description="Dominant colors in the image")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(..., description="Confidence score of text extraction")
    processing_time: str = Field(..., description="Total processing time (e.g., '2.1 sec')")


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str


class VersionResponse(BaseModel):
    name: str
    version: str = "1.0.0"
