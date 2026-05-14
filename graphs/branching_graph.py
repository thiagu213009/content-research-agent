from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from callback_manager import notify
from agents.trends_agent import run_trends_agent
from agents.news_agent import run_news_agent
from agents.statistics_agent import run_statistics_agent
from agents.examples_agent import run_examples_agent
from agents.writer_agent import run_writer_agent
from typing import TypedDict
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)

class ResearchState(TypedDict):
    topic: str
    trends: str
    news: str
    statistics: str
    examples: str
    aggregated: str
    reflection_score: float
    reflection_feedback: str
    retry_count: int
    final_report: str
    pattern: str
    selected_agent: str

def router_node(state: ResearchState) -> dict:
    """Router decides which single agent best fits the topic."""
    notify("router", "running")
    print("\n→ Router: Analysing topic to pick best agent...")
    
    prompt = f"""You are a research router.
    
Topic: "{state['topic']}"

Choose the SINGLE best research approach:
- trends_agent: if topic is about emerging developments, future direction
- news_agent: if topic is about recent events, current happenings  
- statistics_agent: if topic needs data, numbers, market size
- examples_agent: if topic needs real world use cases, implementations

Respond with ONLY one word: trends_agent, news_agent, statistics_agent, or examples_agent"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    selected = response.content.strip().lower()
    print(f"  Router decision: {selected}")
    notify("router", "done", selected)
    return {"selected_agent": selected}

def trends_node(state: ResearchState) -> dict:
    result = run_trends_agent(state["topic"])
    return {"trends": result, "aggregated": result}

def news_node(state: ResearchState) -> dict:
    result = run_news_agent(state["topic"])
    return {"news": result, "aggregated": result}

def statistics_node(state: ResearchState) -> dict:
    result = run_statistics_agent(state["topic"])
    return {"statistics": result, "aggregated": result}

def examples_node(state: ResearchState) -> dict:
    result = run_examples_agent(state["topic"])
    return {"examples": result, "aggregated": result}

def writer_node(state: ResearchState) -> dict:
    report = run_writer_agent(
        state["topic"],
        state["aggregated"]
    )
    return {"final_report": report}

def route_to_agent(state: ResearchState) -> str:
    agent = state.get("selected_agent", "trends_agent")
    if "news" in agent:
        return "news"
    elif "statistics" in agent:
        return "statistics"
    elif "examples" in agent:
        return "examples"
    return "trends"

def build_branching_graph():
    """
    Branching pattern — Router picks ONE best agent:
    Router → trends OR news OR statistics OR examples → Writer
    """
    print("\n🔀 Pattern: Branching (Router)")
    
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("trends", trends_node)
    workflow.add_node("news", news_node)
    workflow.add_node("statistics", statistics_node)
    workflow.add_node("examples", examples_node)
    workflow.add_node("writer", writer_node)
    
    workflow.set_entry_point("router")
    
    # Router branches to ONE agent
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "trends": "trends",
            "news": "news",
            "statistics": "statistics",
            "examples": "examples"
        }
    )
    
    # All paths lead to writer
    workflow.add_edge("trends", "writer")
    workflow.add_edge("news", "writer")
    workflow.add_edge("statistics", "writer")
    workflow.add_edge("examples", "writer")
    workflow.add_edge("writer", END)
    
    return workflow.compile()