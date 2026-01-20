from core import PowerfulNode
from core.smolagents_factory import get_agent, get_mcp_tools
from models import PriceDataList, ConvertedPriceDataList, FinalResult, PriceData, ConvertedPriceData, SymbolAnalysis
from prompts import price_fetch_task, conversion_task, recommendation_task
from tools import PriceFetcherTool, CurrencyConverterTool
from smolagents import Tool

class PriceNode(PowerfulNode):
    def prep(self, shared):
        return {
            "symbols": shared.get("input", {}).get("symbols", []),
            "api_url": shared.get("input", {}).get("api_url"),
            "shared": shared,
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id"),
        }

    def exec(self, inputs):
        symbols = inputs["symbols"]
        api_url = inputs["api_url"]
        print(f"[PriceNode] Fetching prices for: {symbols}")

        price_tool = PriceFetcherTool(api_base_url=api_url)
        agent = get_agent(self.model, tools=[price_tool])

        # Strategy: Construct a task for ALL symbols
        task = f"Fetch prices for the following symbols: {', '.join(symbols)}. Return a JSON object with a list 'items' containing symbol, price, currency, name for each. Always wrap your code in <code> tags."
        
        status = self.run_and_validate(
            agent=agent,
            task=task,
            response_model=PriceDataList,
            shared=inputs["shared"],
            result_key="prices",
            system_prompt="You are a stock price fetcher. Use the tool to get prices.",
            session_id=inputs["session_id"],
            user_id=inputs["user_id"]
        )
        return status

class ConverterNode(PowerfulNode):
    def prep(self, shared):
        prices = shared.get("price", {}).get("prices") # Namespace is 'price' (from PriceNode)
        return {
            "prices": prices,
            "shared": shared,
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id"),
        }

    def exec(self, inputs):
        prices = inputs["prices"]
        if not prices:
            print("[ConverterNode] No prices found.")
            return "error"
            
        print(f"[ConverterNode] Converting prices for {len(prices.items)} items.")
        
        agent = get_agent(self.model, tools=[CurrencyConverterTool()])
        
        # Serialize input for the prompt
        data_str = prices.model_dump_json()
        task = f"Convert these prices to CAD using the tool (rate 1.40). Data: {data_str}. Return JSON with list 'items' containing symbol, price_cad, price_usd, name. Always wrap your code in <code> tags."

        status = self.run_and_validate(
            agent=agent,
            task=task,
            response_model=ConvertedPriceDataList,
            shared=inputs["shared"],
            result_key="converted_prices",
            system_prompt="You are a currency converter.",
            session_id=inputs["session_id"],
            user_id=inputs["user_id"]
        )
        return status

class RecommendationNode(PowerfulNode):
    def prep(self, shared):
        converted = shared.get("converter", {}).get("converted_prices")
        return {
            "converted": converted,
            "mcp_url": shared.get("input", {}).get("mcp_url"),
            "shared": shared,
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id"),
        }

    def exec(self, inputs):
        converted = inputs["converted"]
        mcp_url = inputs["mcp_url"]
        
        if not converted:
            return "error"

        print(f"[RecommendationNode] Getting recommendations for {len(converted.items)} items.")
        
        # MCP Connection
        mcp_client = None
        tools = []
        if mcp_url:
            mcp_client, mcp_tools = get_mcp_tools([mcp_url])
            if mcp_tools: tools.extend(mcp_tools)
        
        try:
            agent = get_agent(self.model, tools=tools)
            
            # Construct task
            # We want to merge the converted price data with the new recommendation data
            data_str = converted.model_dump_json()
            task = f"""
            For each item in the following list, get the recommendation and target price using the available MCP tool. 
            Input Data: {data_str}
            
            Return a JSON object with 'analyses' list. Each item should have:
            - symbol (from input)
            - name (from input)
            - price_cad (from input)
            - recommendation (from tool)
            - target_price (from tool)

            Always wrap your code in <code> tags.
            """
            
            status = self.run_and_validate(
                agent=agent,
                task=task,
                response_model=FinalResult,
                shared=inputs["shared"],
                result_key="final_analysis",
                system_prompt="You are a financial analyst. Use the tools to get recommendations.",
                session_id=inputs["session_id"],
                user_id=inputs["user_id"]
            )
            return status
        finally:
            if mcp_client: mcp_client.disconnect()

class EndNode(PowerfulNode):
    def exec(self, inputs):
        return "Flow_ended"
