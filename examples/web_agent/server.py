from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import argparse

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Determine Auth Mode from environment (passed by our runner)
AUTH_MODE = os.getenv("AUTH_MODE", "cookie") # 'cookie', 'jwt', or 'hybrid'

def get_auth_mode(request: Request):
    # Allow URL to override global mode for easier multi-node testing
    mode = request.query_params.get("mode")
    if mode in ["cookie", "jwt", "hybrid"]:
        return mode
    return AUTH_MODE

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, response: Response):
    data = await request.json()
    mode = get_auth_mode(request)
    
    if data.get("username") == "admin" and data.get("password") == "admin":
        if mode == "jwt":
            return {"status": "success", "token": "mock-jwt-token-12345"}
        elif mode == "hybrid":
            # Set BOTH: A cookie and return a token
            response.set_cookie(key="hybrid_session", value="secret-session-999", httponly=True)
            return {"status": "success", "token": "hybrid-jwt-456"}
        else:
            response.set_cookie(key="session_id", value="mock-session-54321")
            return {"status": "success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    mode = get_auth_mode(request)
    
    # Validation Logic
    if mode == "cookie":
        if not request.cookies.get("session_id"):
            return RedirectResponse(url="/login?mode=cookie")
    elif mode == "hybrid":
        # Server-side check for the cookie
        if not request.cookies.get("hybrid_session"):
            return RedirectResponse(url="/login?mode=hybrid")
        # Note: JWT check happens in the frontend template (index.html)
    
    return templates.TemplateResponse("index.html", {"request": request, "auth_mode": mode})

@app.post("/submit")
async def submit_form(data: dict):
    print(f"Received form data: {data}")
    return {"status": "success", "received": data}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cookie", "jwt", "hybrid"], default="cookie")
    args = parser.parse_args()
    os.environ["AUTH_MODE"] = args.mode
    print(f"Starting Mock Server in {args.mode.upper()} mode on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
