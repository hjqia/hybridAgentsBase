import uvicorn
import os
import argparse
from server import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cookie", "jwt"], default="cookie")
    args = parser.parse_args()
    
    os.environ["AUTH_MODE"] = args.mode
    print(f"Starting Mock Server in {args.mode.upper()} mode on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
