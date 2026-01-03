from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# Import your trading agents
from service import enqueue_analysis, get_status
from tradingagents.config import get_config

config = get_config()
DEFAULT_USER = "global_user"

# Create FastAPI app instance
app = FastAPI(
    title="TradingAgents API",
    description="API for TradingAgents financial trading framework",
    version="0.1.0"
)

class TradingAnalyzeRequest(BaseModel):
    symbol: str
    date: str

class TradingAnalyzeResponse(BaseModel):
    symbol: str
    date: str
    job_id: str
    timestamp: str
    status: str
    
class TradingStatusResponse(BaseModel):
    job_id: str
    status: str
    result: str | None = None
    message: str | None = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to TradingAgents API"}

@app.get("/ping")
async def ping():
    """Simple ping endpoint that returns pong"""
    return {"message": "pong"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "tradingagents-api"
    }

@app.post("/v1/trading/analyze", response_model=TradingAnalyzeResponse, status_code=status.HTTP_202_ACCEPTED,)
async def analyze_trading_decision(request: TradingAnalyzeRequest):
    """
    Analyze trading decision for a given symbol and date
    
    Example usage:
    POST /trading/analyze
    {
        "symbol": "BTC/USDT",
        "date": "2024-05-10"
    }
    """
    response = enqueue_analysis(DEFAULT_USER, request.symbol, request.date)
    print(f"INFO: Enqueue response: {response}")

    if response.status == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
    
    return TradingAnalyzeResponse(
        symbol=request.symbol,
        date=request.date,
        job_id=response.job_id,
        timestamp=datetime.now().isoformat(),
        status=response.status
    )

@app.get("/v1/trading/status/{job_id}", response_model=TradingStatusResponse, status_code=status.HTTP_200_OK)
def get_trading_status(job_id: str):
    response = get_status(DEFAULT_USER, job_id)
    if response:
        return TradingStatusResponse(
            job_id=job_id,
            status=response.status,
            result=response.result,
            message=response.message
        )

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "webapp:app",
        host=config.get("APP_HOST", "localhost"),
        port=config.get("APP_PORT", 8000),
        reload=True,
        log_level="info"
    )
