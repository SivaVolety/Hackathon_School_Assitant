# mcp_agent_final_fixed.py
import json
import requests
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# ------------------- MCP CLIENT -------------------
class MCPClient:
    def __init__(self, url="http://127.0.0.1:8000/"):
        self.url = url
        self.rid = 0
        self._init()

    def _send(self, method, params=None, notification=False):
        self.rid += 1
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            payload["id"] = self.rid
        if params:
            payload["params"] = params
        r = requests.post(self.url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json() if not notification else None

    def _init(self):
        self._send("initialize")
        self._send("notifications/initialized", notification=True)

    def call(self, name, args):
        print(f"Sending to MCP: {name}(args={args})")
        return self._send("tools.call", {"tool": name, "args": args})["result"]

# ------------------- TOOL SCHEMAS -------------------
class LunchMenuArgs(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")

class ReportAbsenceArgs(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    reason: str = Field(..., description="Reason for absence")

TOOL_SCHEMAS = {
    "lunch_menu": LunchMenuArgs,
    "report_absence": ReportAbsenceArgs
}

# ------------------- PROMPT (ESCAPED BRACES) -------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful assistant. Use tools when needed.

Available tools:
- lunch_menu(date): Get lunch menu
- report_absence(date, reason): Report absence

Respond in JSON with one of these formats:

{{
  "tool": "lunch_menu",
  "args": {{"date": "2025-11-09"}}
}}

or

{{
  "tool": "report_absence",
  "args": {{"date": "2025-11-09", "reason": "sick"}}
}}

or (if no tool needed)

{{
  "answer": "direct response"
}}
"""),
    ("human", "{input}"),
])

parser = JsonOutputParser()

chain = prompt | ChatOllama(model="llama3.1:8b", temperature=0) | parser

# ------------------- AGENT LOOP -------------------
def run_agent(query: str):
    try:
        response = chain.invoke({"input": query})
        print("LLM response:", response)

        if "tool" in response:
            tool_name = response["tool"]
            args = response.get("args", {})

            if tool_name not in TOOL_SCHEMAS:
                return f"Unknown tool: {tool_name}"

            # Validate with Pydantic
            validated_args = TOOL_SCHEMAS[tool_name](**args)
            client = MCPClient()
            result = client.call(tool_name, validated_args.dict())
            return result

        else:
            return response.get("answer", "No answer")

    except Exception as e:
        return f"Error: {e}"

# ------------------- RUN -------------------
if __name__ == "__main__":
    print("\nMCP Agent Ready (type 'exit' to quit)\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if not q:
            continue
        result = run_agent(q)
        print("\nAgent:", result, "\n")
