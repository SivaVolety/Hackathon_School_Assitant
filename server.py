# mcp_server_manual.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# ================================
# TOOL DEFINITIONS (keep your logic)
# ================================

def report_absence(date: str, reason: str) -> str:
    """Report an absence on a specific date for a specific reason."""
    return f"Absence reported for {date}. Reason: {reason}"

def lunch_menu(date: str) -> str:
    """Return lunch menu for a given date."""
    menus = {
        "2025-11-07": "Cheese Pizza, Garden Salad, Apple Slices, Milk",
        "2025-11-08": "Chicken Nuggets, Mashed Potatoes, Green Beans",
        "2025-11-09": "Veggie Burger, Sweet Potato Fries, Orange Wedges",
    }
    return menus.get(date, "No menu available for that date.")

# ================================
# MANUAL TOOL REGISTRY
# ================================

TOOLS = {
    "report_absence": {
        "func": report_absence,
        "description": "Report an absence on a specific date for a specific reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "reason": {"type": "string", "description": "Reason for absence"}
            },
            "required": ["date", "reason"],
            "additionalProperties": False
        }
    },
    "lunch_menu": {
        "func": lunch_menu,
        "description": "Return lunch menu for a given date.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
            },
            "required": ["date"],
            "additionalProperties": False
        }
    }
}

# ================================
# JSON-RPC HANDLER
# ================================

@app.post("/")
async def handle_jsonrpc(request: Request):
    try:
        body = await request.json()
        print("→", body)
        method = body.get("method")
        params = body.get("params", {})
        req_id = body.get("id")

        # --- initialize / initialized ---
        if method in ("initialize", "notifications/initialized"):
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "serverInfo": {"name": "School Tools MCP", "version": "1.0"},
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {"listChanged": True}}
                }
            })

        # --- tools.list ---
        elif method == "tools.list":
            result = {
                name: {
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
                for name, tool in TOOLS.items()
            }
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})

        # --- tools.call ---
        elif method == "tools.call":
            tool_name = params.get("tool")
            args = params.get("args", {})
            print(f"Received tool call: {tool_name}, args: {args}")

            if tool_name not in TOOLS:
                return JSONResponse({
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": "Unknown tool"}
                })

            result = TOOLS[tool_name]["func"](**args)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})

        # --- unknown method ---
        else:
            return JSONResponse({
                "jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": "Unknown method"}
            })

    except Exception as e:
        import traceback
        print("ERROR:", traceback.format_exc())
        return JSONResponse({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32000, "message": str(e)}
        })

# ================================
# RUN SERVER
# ================================

if __name__ == "__main__":
    print("MCP Server running at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
