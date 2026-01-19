from mcp.server.fastmcp import FastMCP
import random
import json

mcp = FastMCP("Recommendation Service")

@mcp.tool()
def get_recommendation(symbol: str) -> dict:
    """Get buy/sell recommendation and target price for a symbol."""
    recs = ["Buy", "Sell", "Hold", "Strong Buy"]
    rec = random.choice(recs)
    current_price_est = 100 # Dummy
    target = round(current_price_est * random.uniform(0.8, 1.5), 2)
    
    return {
        "symbol": symbol,
        "recommendation": rec,
        "target_price": target
    }

if __name__ == "__main__":
    import uvicorn
    # FastMCP provides sse_app which is a Starlette/FastAPI-like app
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8080)
