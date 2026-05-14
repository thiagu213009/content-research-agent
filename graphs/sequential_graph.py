from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from agents.trends_agent import run_trends_agent
from agents.news_agent import run_news_agent
from agents.statistics_agent import run_statistics_agent
from agents.examples_agent import run_examples_agent
from agents.reflection_agent import run_reflection_agent
from agents.writer_agent import run_writer_agent
from callback_manager import notify

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

def trends_node(state: ResearchState) -> dict:
    return {"trends": run_trends_agent(state["topic"])}

def news_node(state: ResearchState) -> dict:
    return {"news": run_news_agent(state["topic"])}

def statistics_node(state: ResearchState) -> dict:
    return {"statistics": run_statistics_agent(state["topic"])}

def examples_node(state: ResearchState) -> dict:
    return {"examples": run_examples_agent(state["topic"])}

def aggregator_node(state: ResearchState) -> dict:
    print("\n→ Aggregator: Combining all research...")
    aggregated = f"""
RESEARCH COMPILATION — {state['topic']}

TRENDS:
{state['trends']}

RECENT NEWS:
{state['news']}

STATISTICS:
{state['statistics']}

REAL WORLD EXAMPLES:
{state['examples']}
"""
    print("  Aggregation complete ✅")
    return {"aggregated": aggregated}

def writer_node(state: ResearchState) -> dict:
    report = run_writer_agent(
        state["topic"],
        state["aggregated"],
        state.get("reflection_feedback", "")
    )
    return {"final_report": report}

def build_sequential_graph():
    """
    Sequential pattern — one agent at a time:
    Trends → News → Statistics → Examples → Aggregator → Writer
    """
    print("\n📋 Pattern: Sequential (ReAct style)")
    
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("trends", trends_node)
    workflow.add_node("news", news_node)
    workflow.add_node("statistics", statistics_node)
    workflow.add_node("examples", examples_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("writer", writer_node)
    
    # Sequential flow — one after another
    workflow.set_entry_point("trends")
    workflow.add_edge("trends", "news")
    workflow.add_edge("news", "statistics")
    workflow.add_edge("statistics", "examples")
    workflow.add_edge("examples", "aggregator")
    workflow.add_edge("aggregator", "writer")
    workflow.add_edge("writer", END)
    
    return workflow.compile()