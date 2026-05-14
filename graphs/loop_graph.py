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
    reflection_history: Annotated[List, operator.add]
    retry_count: int
    final_report: str
    pattern: str

def planner_node(state: ResearchState) -> dict:
    notify("planner", "running")
    print("\n→ Planner: Planning research...")
    notify("planner", "done")
    return {}

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

def reflection_node(state: ResearchState) -> dict:
    result = run_reflection_agent(state["topic"], state["aggregated"])

    # Store each reflection attempt for UI cards
    history_entry = [{
        "attempt": state.get("retry_count", 0) + 1,
        "draft_summary": result["draft_summary"],
        "status": result["status"],
        "feedback": result["feedback"],
        "score": result["score"]
    }]

    return {
        "reflection_score": result["score"],
        "reflection_feedback": result["feedback"],
        "reflection_history": history_entry
    }

def writer_node(state: ResearchState) -> dict:
    report = run_writer_agent(
        state["topic"],
        state["aggregated"],
        state.get("reflection_feedback", "")
    )
    return {"final_report": report}

def route_after_reflection(state: ResearchState) -> str:
    if state["reflection_score"] < 0.85 and state["retry_count"] < 3:
        print(f"\n  Score too low ({state['reflection_score']}) — retrying...")
        return "retry"
    return "write"

def increment_retry(state: ResearchState) -> dict:
    return {"retry_count": state["retry_count"] + 1}

def build_loop_graph():
    """
    Loop/Reflection pattern — Self-reflection loop:
    Planner → [Parallel research] → Aggregator → Reflection →
    if score < 0.7 → loop back (max 3 retries)
    if score >= 0.7 → Writer → END
    """
    print("\n🔄 Pattern: Loop (Reflection)")

    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("trends", trends_node)
    workflow.add_node("news", news_node)
    workflow.add_node("statistics", statistics_node)
    workflow.add_node("examples", examples_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("retry_counter", increment_retry)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("planner")

    # Fan-out
    workflow.add_edge("planner", "trends")
    workflow.add_edge("planner", "news")
    workflow.add_edge("planner", "statistics")
    workflow.add_edge("planner", "examples")

    # Fan-in
    workflow.add_edge("trends", "aggregator")
    workflow.add_edge("news", "aggregator")
    workflow.add_edge("statistics", "aggregator")
    workflow.add_edge("examples", "aggregator")

    workflow.add_edge("aggregator", "reflection")

    # Self-reflection loop
    workflow.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "retry": "retry_counter",
            "write": "writer"
        }
    )

    # Loop back to research
    workflow.add_edge("retry_counter", "trends")
    workflow.add_edge("retry_counter", "news")
    workflow.add_edge("retry_counter", "statistics")
    workflow.add_edge("retry_counter", "examples")

    workflow.add_edge("writer", END)

    return workflow.compile()
