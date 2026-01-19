def price_fetch_task(symbol: str) -> str:
    return f"Fetch the current price for {symbol}. Return the JSON with symbol, price, currency, and name."

def conversion_task(price_data: dict) -> str:
    return f"Convert the following price from USD to CAD (assume 1 USD = 1.40 CAD). Data: {price_data}. Return JSON with symbol, price_cad, price_usd, and name."

def recommendation_task(symbol_data: dict) -> str:
    return f"Get the recommendation and 1-year target price for {symbol_data['symbol']} from the MCP server. Return JSON with symbol, recommendation, and target_price."
