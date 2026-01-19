from smolagents import Tool
import urllib.request
import json
import urllib.error

class PriceFetcherTool(Tool):
    name = "fetch_price"
    description = "Fetches the current price of a symbol."
    inputs = {
        "symbol": {"type": "string", "description": "Symbol ticker (e.g. AAPL)"}
    }
    output_type = "string"

    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip("/")
        super().__init__()

    def forward(self, symbol: str) -> str:
        try:
            # Mocking the request since the server URL is dynamic
            # In a real scenario, this would use the self.api_base_url
            url = f"{self.api_base_url}/price?symbol={symbol}"
            
            # Since I cannot actually hit the user's local server from here without it running,
            # I will implement the logic. If the user provided URL is reachable, it works.
            # However, for the purpose of the 'build' request, I assume the tool logic is what's needed.
            
            try:
                with urllib.request.urlopen(url) as response:
                    if response.status == 200:
                        return response.read().decode()
                    return json.dumps({"error": f"HTTP {response.status}"})
            except urllib.error.URLError as e:
                 return json.dumps({"error": f"Connection failed: {e}"})
                 
        except Exception as e:
            return json.dumps({"error": str(e)})

class CurrencyConverterTool(Tool):
    name = "convert_currency"
    description = "Converts USD to CAD."
    inputs = {
        "amount": {"type": "number", "description": "Amount in USD"},
        "rate": {"type": "number", "description": "Exchange rate (default 1.40)", "nullable": True}
    }
    output_type = "number"

    def forward(self, amount: float, rate: float = 1.40) -> float:
        return amount * rate
