from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import SystemMessage, HumanMessage
 
from settings import HttpStatusCode, config
from utils.exceptions.error_code import ErrorCode, ErrorCodeStatus
from utils.exceptions.custom_app_exception import CustomAppException
from utils.error_logs import log_error
from utils.helper import get_llm, log_decorator
from Agents.code_agent import CodeAgent
from Agents.review_agent import ReviewAgent
from Agents.research_agent import ResearchAgent
from Agents.prompt import orches_prompt
from utils.helper import get_db_uri
 
 
class State(TypedDict, total=False):
    user_query: str
    username: str
    decision: str
    AgentPath: str          
    Code: Optional[str]
    ReviewResponse: Optional[dict]
    IsReviewValid: Optional[bool]
    NeedsResearch: Optional[bool]  
    ResearchResponse: Optional[str]
    IsResearchCompleted: Optional[bool]
    review_attempts: int
 
 
class AgentService:
   
    async def node_orchs(self, state: State) -> Command[Literal["node_code", "node_review", "node_research", "__end__"]]:       
        llm = get_llm(max_tokens=20, temperature=0)
        messages = [
            SystemMessage(content=orches_prompt),
            HumanMessage(content=state["user_query"]),
        ]
       
        response = llm.invoke(messages)
        decision = response.content.strip().lower()
 
        if "research" in decision:
            path = "research"
            next_node = "node_research"
        elif "review" in decision:
            path = "review"
            next_node = "node_review"
        elif "code" in decision:
            path = "code"
            next_node = "node_code"
        else:
            # Avoid silently ending with no answer for ordinary conversation.
            path = "research"
            next_node = "node_research"
 
        print(f"Orchestrator decision={decision} AgentPath={path} next={next_node}")
       
        return Command(
            goto=next_node,
            update={"decision": decision, "AgentPath": path}
        )
   
    async def node_code_agent(self, state: State) -> Command[Literal["node_review", "__end__"]]:
        code = await CodeAgent().create_coder_agent(state)
        return Command(
            goto="node_review",
            update={"Code": code}
        )
   
    async def node_review_agent(self, state: State) -> Command[Literal["node_code", "node_research", "__end__"]]:
        response, valid, needs_research = await ReviewAgent().create_review_agent(state)
       
        state_update = {
            "ReviewResponse": response,
            "IsReviewValid": valid,
            "NeedsResearch": needs_research,
        }
       
        if state.get("AgentPath") == "review":
            return Command(goto=END, update=state_update)
       
        if valid:
            return Command(goto=END, update=state_update)
       
        if needs_research:
            return Command(goto="node_research", update=state_update)
       
        return Command(goto="node_code", update=state_update)
   
    async def node_researcher_agent(self, state: State) -> Command[Literal["node_code", "__end__"]]:
       
        response, completed = await ResearchAgent().create_research_agent(state)
       
        state_update = {
            "ResearchResponse": response,
            "IsResearchCompleted": completed,
        }
       
        if completed:
            return Command(goto=END, update=state_update)
        else:
            return Command(goto=END, update=state_update)
   
    @log_decorator
    async def chatbot_service(self, user_query: str, username: str) -> dict:
        try:
            graph = StateGraph(State)
           
            graph.add_node("node_orchs", self.node_orchs)
            graph.add_node("node_code", self.node_code_agent)
            graph.add_node("node_review", self.node_review_agent)
            graph.add_node("node_research", self.node_researcher_agent)           
            graph.add_edge(START, "node_orchs")
           
            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()
                compiled = graph.compile(checkpointer=checkpointer)
                agent_config = {"configurable": {"thread_id": username}}
                print("GRAPH COMPLIED")
               
                data = await compiled.ainvoke(
                    {"user_query": user_query, "username": username},
                    config=agent_config,
                )
 
            return {
                "content": data.get("decision"),
                "code": data.get("Code"),
                "review_response": data.get("ReviewResponse"),
                "research_response": data.get("ResearchResponse"),
            }
 
        except CustomAppException:
            raise
        except Exception as e:
            log_error("agent_service.py", "chatbot_service()", str(e))
            raise CustomAppException(
                message=f"Service error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus[ErrorCode.INTERNAL_SERVER_ERROR],
            )