"""API 스키마 패키지"""

from .conversion import (
    ConversionRequest,
    ConversionResponse, 
    FeedbackRequest,
    FeedbackResponse
)

__all__ = [
    "ConversionRequest",
    "ConversionResponse", 
    "FeedbackRequest",
    "FeedbackResponse"
]