# Multi-Agent Code Generation Chatbot

A production-style multi-agent system that takes a natural-language coding request and routes it through a **Supervisor Agent** to specialist **Code**, **Review**, and **Research** agents, orchestrated with LangGraph and served over a FastAPI REST API.

## How It Works

1. A user query hits `POST /api/v1/chatbot`.
2. An **orchestrator node** (LLM-based intent classifier) decides the entry point: `code`, `review`, or `research`.
3. The **Code Agent** generates code using an AWS Bedrock LLM.
4. The **Review Agent** critiques the generated code — it connects to an external **MCP tool server** (via SSE) to run real static-analysis/lint tools while reviewing, and returns a structured pass/fail + feedback verdict.
5. If review fails, the flow loops back to Code (with feedback) or to **Research** first if more context is needed, then back to Code.
6. Each agent keeps its own conversation thread, checkpointed in PostgreSQL, so multi-turn state persists per user/session.

```
User Query → Orchestrator → Code Agent ⇄ Review Agent ⇄ Research Agent → Response
```

See [`Flow_diagrams/`](./Flow_diagrams) for the PlantUML class/sequence diagrams and OpenAPI spec.

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI, Uvicorn |
| Agent orchestration | LangGraph (`StateGraph`, `Command`-based routing) |
| Agent framework | LangChain (`create_agent`, `create_react_agent`) |
| LLM provider | AWS Bedrock (`langchain-aws` `ChatBedrock`, `boto3`) |
| Tool protocol | Model Context Protocol (MCP) — `langchain-mcp-adapters`, custom FastMCP tool server |
| Persistence / checkpointing | PostgreSQL, SQLAlchemy, `langgraph-checkpoint-postgres`, `psycopg2` |
| Config | `python-dotenv` |
| Language / tooling | Python 3.11, `uv` for dependency management |

## Repository Structure

```
.
├── projects/client/src/          # Main FastAPI application
│   ├── main.py                   # App entrypoint, exception handlers, startup migration
│   ├── settings.py               # Config loader (env vars)
│   ├── Agents/                   # CodeAgent, ReviewAgent, ResearchAgent, prompt templates
│   ├── services/                 # agent_service.py — LangGraph StateGraph / Supervisor logic
│   ├── routes/                   # agent_route.py — /api/v1/chatbot endpoint
│   ├── models/                   # Request/response & structured-output models
│   ├── Repositories/             # DB access layer + schema
│   ├── migration/                # DB migration runner (invoked on startup)
│   └── utils/                    # Custom exceptions, error logging, LLM/DB helpers
│
├── mcp_python_toolbox/           # Standalone MCP server (FastMCP) used by the Review Agent
│   └── src/mcp_python_toolbox/   # File ops, code analysis, formatting, linting, execution,
│                                  # venv & dependency management tools exposed over MCP
│
├── docs/                         # LangGraph learning notes & reference snippets
├── Flow_diagrams/                # PlantUML class/sequence diagrams + OpenAPI (doc.yaml)
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL instance
- AWS account with Bedrock access (for the model inference profile)
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Setup

```bash
cd projects/client/src

# install dependencies
uv sync            # or: pip install -r requirements.txt

# configure environment
cp .env.example .env    # fill in your own DB + AWS credentials
```

Required environment variables:

```
DB_HOST=
DB_PORT=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
MODEL_ID=            # Bedrock inference profile ARN
PROVIDER=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
REGION=
MCP_SERVER_URL=
```

### Run

```bash
# 1. start the MCP tool server (used by the Review Agent)
cd mcp_python_toolbox
python -m mcp_python_toolbox

# 2. start the API
cd projects/client/src
python main.py          # serves on http://0.0.0.0:8080
```

### Example Request

```bash
curl -X POST http://localhost:8080/api/v1/chatbot \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Write a Python function to reverse a linked list", "unique_id": "user123"}'
```

## Security Note

`.env` and any real credentials must **never** be committed. This repo's `.gitignore` excludes `.env`, `__pycache__/`, and other local artifacts — double-check `git status` before your first push, and rotate any credentials that may have been exposed during local development.

## MCP Toolbox

[`mcp_python_toolbox/`](./mcp_python_toolbox) is a self-contained MCP server exposing Python developer tools (file I/O, AST-based code analysis, Black/PEP8 formatting, Pylint linting, sandboxed code execution, venv & dependency management) over the Model Context Protocol, consumed by the Review Agent as an SSE tool source.


## Configuration and safety notes

- Copy `projects/client/.env.example` to `projects/client/.env` and configure the database, AWS region/model, and MCP URL for your local environment.
- Never commit real `.env` files, AWS access keys, database passwords, or other credentials. Prefer an AWS profile or IAM role over static keys.
- The MCP toolbox can write/delete files, install packages, and execute arbitrary Python. Run it only against a dedicated workspace in an isolated environment; it is not a security sandbox.
- The code-execution tool now enforces a 30-second timeout and checks that its working directory is inside the configured workspace. OS-level isolation is still required for untrusted code.
- Configure PostgreSQL and the MCP server before starting the API. A successful syntax check does not guarantee that AWS Bedrock, PostgreSQL, or MCP connectivity works end to end.
- This repository is a development/demo platform. Add authentication, authorization, rate limiting, and production-grade logging before exposing it publicly.
