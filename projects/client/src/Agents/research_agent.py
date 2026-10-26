from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from settings import config, HttpStatusCode
from utils.exceptions.error_code import ErrorCode, ErrorCodeStatus
from utils.exceptions.custom_app_exception import CustomAppException
from utils.error_logs import log_error
from utils.helper import get_llm, log_decorator,get_db_uri
from Agents.prompt import research_system_prompt
from models.agent_model import Research
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
class ResearchAgent:
    @log_decorator
    async def create_research_agent(self, state) -> tuple[str, bool]:

        try:
            llm = get_llm(max_tokens=1500, temperature=0.8)
            agent_config = {"configurable": {"thread_id": f"{state['username']}_research"}}

            # Enrich query with code + review context when research was triggered by a review failure
            user_query = state["user_query"]
            if state.get("Code") and state.get("ReviewResponse"):
                user_query = (
                    f"{user_query}\n\n"
                    f"Code that was reviewed:\n{state['Code']}\n\n"
                    f"Review feedback requiring research:\n{state['ReviewResponse']}\n\n"
                    f"Please research the topic to provide context for improving this code."
                )


            # Research currently uses the configured model and its own instructions.
            # MCP tools are attached when the configured server is reachable.
            client = MultiServerMCPClient(
                {
                    "tools": {
                        "transport": "sse",
                        "url": config.MCP_SERVER_URL,
                    }
                }
            )
            tools = await client.get_tools()

            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()
                agent = create_agent(
                    model=llm,
                    tools=tools,
                    system_prompt=research_system_prompt,
                    checkpointer=checkpointer,
                )
                print(f"[ResearchAgent] thread: {agent_config['configurable']['thread_id']}")
                data = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_query}]},
                    config=agent_config,
                )

            
            # ✅ Extract generated research text
            messages = data.get("messages", [])
            ai_message = messages[-1]

            research_text = (
                ai_message.content
                if isinstance(ai_message.content, str)
                else str(ai_message.content)
            )
            
            is_completed = len(research_text.strip()) > 200

            print(f"[ResearchAgent] IsResearchCompleted={is_completed}")

            return research_text, is_completed


        except CustomAppException:
            raise
        except Exception as e:
            log_error("research_agent.py", "create_research_agent()", str(e))
            raise CustomAppException(
                message=f"Research agent error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus[ErrorCode.INTERNAL_SERVER_ERROR],
            )
