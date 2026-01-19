#!/bin/bash
VENV_PYTHON="../../.venv/bin/python3"

echo "Starting Price API..."
pkill -f mock_price_api.py
$VENV_PYTHON mock_price_api.py 8085 > price_api.log 2>&1 &
PRICE_PID=$!
echo "Price API PID: $PRICE_PID"

echo "Starting MCP Server..."
pkill -f mock_mcp_server.py
$VENV_PYTHON mock_mcp_server.py > mcp_server.log 2>&1 &
MCP_PID=$!
echo "MCP Server PID: $MCP_PID"

echo "Starting Agent..."
sleep 10

$VENV_PYTHON main.py --symbols AAPL BTC ETH --api-url http://localhost:8085 --mcp-url http://localhost:8080/sse

# Cleanup
kill $PRICE_PID
kill $MCP_PID
