from pydantic import BaseModel
from typing import List, Optional

class PriceData(BaseModel):
    symbol: str
    price: float
    currency: str
    name: str

class PriceDataList(BaseModel):
    items: List[PriceData]

class ConvertedPriceData(BaseModel):
    symbol: str
    price_cad: float
    price_usd: float
    name: str

class ConvertedPriceDataList(BaseModel):
    items: List[ConvertedPriceData]

class RecommendationData(BaseModel):
    symbol: str
    recommendation: str
    target_price: float

class SymbolAnalysis(BaseModel):
    symbol: str
    name: str
    price_cad: float
    recommendation: str
    target_price: float

class FinalResult(BaseModel):
    analyses: List[SymbolAnalysis]