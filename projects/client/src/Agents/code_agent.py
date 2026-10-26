from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from settings import config, HttpStatusCode
from langchain.agents import create_agent
from utils.exceptions.error_code import ErrorCode, ErrorCodeStatus
from utils.exceptions.custom_app_exception import CustomAppException
from utils.error_logs import log_error
from utils.helper import get_llm, log_decorator,get_db_uri
from Agents.prompt import code_system_prompt
from models.agent_model import Code


class CodeAgent:
    @log_decorator
    async def create_coder_agent(self, state) -> tuple[str, str]:
        try:
            llm = get_llm(max_tokens=1500, temperature=0.5)
            agent_config = {"configurable": {"thread_id": f"{state['username']}_code"}}

            # Build an enriched query when review / research context exists
            user_query = state["user_query"]
            if state.get("Code") and state.get("ReviewResponse"):
                user_query = (
                    f"{user_query}\n\n"
                    f"Previously generated code:\n{state['Code']}\n\n"
                    f"Review feedback — address ALL of the following:\n{state['ReviewResponse']}\n\n"
                    f"Please regenerate the code fixing every review issue listed above."
                )
            if state.get("ResearchResponse"):
                user_query += (
                    f"\n\nResearch context to incorporate into the implementation:\n"
                    f"{state['ResearchResponse']}"
                )


            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()
                agent = create_agent(
                    model=llm,
                    tools=[],
                    system_prompt=code_system_prompt,
                    checkpointer=checkpointer,
                )
                print(f"[CodeAgent] thread: {agent_config['configurable']['thread_id']}")
                data = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_query}]},
                    config=agent_config,
                )

            import html

            messages = data.get("messages", [])
            ai_message = messages[-1]

            code_text = (
                ai_message.content
                if isinstance(ai_message.content, str)
                else str(ai_message.content)
            )
            code_text = html.unescape(code_text)
            code_text = code_text.replace("```python", "").replace("```", "").strip()
            state["Code"] = code_text

            print("\nGENERATED CODE: \n")
            print(code_text)


            return code_text
        
        except CustomAppException:
            raise
        except Exception as e:
            log_error("code_agent.py", "create_coder_agent()", str(e))
            raise CustomAppException(
                message=f"Code agent error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus[ErrorCode.INTERNAL_SERVER_ERROR],
            )