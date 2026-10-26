from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from settings import config, HttpStatusCode
from utils.exceptions.error_code import ErrorCode, ErrorCodeStatus
from utils.exceptions.custom_app_exception import CustomAppException
from utils.error_logs import log_error
from utils.helper import get_llm, log_decorator,get_db_uri
from Agents.prompt import review_system_prompt
from models.agent_model import Review
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient 
class ReviewAgent:
    @log_decorator
    async def create_review_agent(self, state) -> tuple[dict, bool, bool]:
        try:
            llm = get_llm(max_tokens=1500, temperature=0.25)
            agent_config = {"configurable": {"thread_id": f"{state['username']}_review"}}

            user_query = state["user_query"]
            if state.get("Code"):
                user_query = (
                    f"Review the following code that was generated for this request: '{user_query}'\n\n"
                    f"Code to review:\n{state['Code']}"
                )
            client = MultiServerMCPClient(
            {
                "tools": {
                    "transport": "sse",
                    "url": config.MCP_SERVER_URL,
                  
                }
            }
        )
            tools = await client.get_tools()
            for i in tools:
                print(i)
            print("tools-review",tools)
            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()
                agent = create_agent(
                    model=llm,
                    tools=tools,
                    system_prompt=review_system_prompt,
                    response_format=Review,
                    checkpointer=checkpointer,
                )
                print(f"[ReviewAgent] thread: {agent_config['configurable']['thread_id']}")
                data = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_query}]},
                    config=agent_config,
                )

            result: Review = data["structured_response"]
            print(f"[ReviewAgent] IsReviewValid={result.IsReviewValid} NeedsResearch={result.NeedsResearch}")
            return result.ReviewResponse, result.IsReviewValid, result.NeedsResearch

        except CustomAppException:
            raise
        except Exception as e:
            log_error("review_agent.py", "create_review_agent()", str(e))
            raise CustomAppException(
                message=f"Review agent error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus[ErrorCode.INTERNAL_SERVER_ERROR],
            )
