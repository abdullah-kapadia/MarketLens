from pydantic import BaseModel

class AIRequest(BaseModel):
    symbol: str

class AIResponse(BaseModel):
    symbol: str
    headline: str
    commentry: str
    chart_path: str