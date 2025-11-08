# MCP School Tools Agent  
**A LangChain + Ollama agent that talks to a FastMCP server using Llama 3.1 8B**

---

## Overview

This project demonstrates a **fully functional AI agent** that:
- Connects to a **FastMCP JSON-RPC server** over HTTP
- Discovers tools via `tools.list`
- Uses **Llama 3.1 8B** (via Ollama) to decide when to call tools
- Calls tools like `lunch_menu(date)` and `report_absence(date, reason)`
- Returns natural language responses

**No empty `args`. No missing parameters. 100% working.**

---

## Project Structure

```
mcp-school-tools/
├── mcp_server_fixed.py       # MCP JSON-RPC server (manual registry)
├── mcp_agent_final_fixed.py  # LangChain + Ollama agent (structured JSON)
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

---

## Features

| Feature | Status |
|-------|--------|
| MCP Protocol (initialize, tools.list, tools.call) | Working |
| Tool Schema Discovery | Working |
| Structured Tool Calling | Working |
| Pydantic Validation | Working |
| JSON Response Parsing | Working |
| Ollama + Llama 3.1 8B | Working |
| No LangChain Agent Bugs | Working |

---

## Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running
3. **Llama 3.1 8B** model pulled

```bash
ollama pull llama3.1:8b
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/mcp-school-tools.git
cd mcp-school-tools
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```txt
fastapi
uvicorn
langchain
langchain-ollama
langchain-core
pydantic
requests
```

---

## Run the System

### Step 1: Start the MCP Server

```bash
python mcp_server_fixed.py
```

Server runs at: `http://127.0.0.1:8000`

### Step 2: Start the Agent

```bash
python mcp_agent_final_fixed.py

### Ollama Start Up

Ollama serve
```

---

## Try It!

```text
You: what is for lunch on 2025-11-09
LLM response: {'tool': 'lunch_menu', 'args': {'date': '2025-11-09'}}
Sending to MCP: lunch_menu(args={'date': '2025-11-09'})

Agent: Veggie Burger, Sweet Potato Fries, Orange Wedges
```

```text
You: report absence on 2025-11-12 because I'm sick
LLM response: {'tool': 'report_absence', 'args': {'date': '2025-11-12', 'reason': "I'm sick"}}

Agent: Absence reported for 2025-11-12. Reason: I'm sick
```

---

## How It Works

1. **Agent** sends `initialize` → `notifications/initialized` → `tools.list`
2. **Server** returns full JSON schema for each tool
3. **Agent** prompts Llama 3.1 with **escaped JSON examples**
4. **LLM** outputs structured JSON: `{"tool": "...", "args": {...}}`
5. **Agent** validates args with **Pydantic**
6. **Agent** calls MCP server with `tools.call`
7. **Server** executes tool and returns result

---

## Debugging Tips

- Check **MCP server logs** for incoming `tools.call`
- Check **agent logs** for `Sending to MCP`
- Use `curl` to test server directly:

```bash
curl -X POST http://127.0.0.1:8000 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools.call","params":{"tool":"lunch_menu","args":{"date":"2025-11-08"}},"id":1}'
```

---

## Customization

### Add a New Tool

1. Add function in `mcp_server_fixed.py`
2. Register in `TOOLS` dict with `parameters`
3. Add Pydantic model in `mcp_agent_final_fixed.py`
4. Add to `TOOL_SCHEMAS`

---

## Troubleshooting

| Error | Fix |
|------|-----|
| `missing 1 required positional argument` | Args not sent → use **escaped JSON in prompt** |
| `INVALID_PROMPT_INPUT` | Escape `{{` and `}}` in prompt |
| `Unsupported function` | Don’t pass `StructuredTool` to `with_structured_output` |
| Ollama not responding | Run `ollama serve` |

---

## Future Ideas

- [ ] Web UI (Streamlit/Gradio)
- [ ] Conversation memory
- [ ] Async support
- [ ] Authentication
- [ ] More tools (grades, schedule, etc.)

---

## License

MIT

---

**Built with love for hackathons, demos, and learning.**

Let me know when you're ready to deploy!